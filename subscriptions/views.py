import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from .models import SubscriptionPlan, UserSubscription
from .gateways.mtn import MTNMoMoGateway
from .gateways.airtel import AirtelMoneyGateway
from .gateways.stripe_gateway import StripeGateway


# ── PRICING PAGE ──────────────────────────────────────────────────────────────
def pricing_view(request):
    jobseeker_plans = SubscriptionPlan.objects.filter(role='jobseeker', is_active=True)
    employer_plans  = SubscriptionPlan.objects.filter(role='employer',  is_active=True)
    return render(request, 'subscriptions/pricing.html', {
        'jobseeker_plans': jobseeker_plans,
        'employer_plans':  employer_plans,
    })


# ── CHECKOUT PAGE (choose gateway) ───────────────────────────────────────────
@login_required
def checkout_view(request, plan_slug):
    plan  = get_object_or_404(SubscriptionPlan, slug=plan_slug, is_active=True)
    cycle = request.GET.get('cycle', 'monthly')

    price_usd = plan.yearly_usd  if cycle == 'yearly' else plan.monthly_usd
    price_ugx = plan.yearly_ugx  if cycle == 'yearly' else plan.monthly_ugx

    # Get or create pending subscription
    sub, _ = UserSubscription.objects.get_or_create(user=request.user)
    sub.plan          = plan
    sub.billing_cycle = cycle
    sub.status        = UserSubscription.PENDING
    sub.save()

    cancelled = request.GET.get('cancelled') == '1'
    if cancelled:
        messages.warning(request, 'Payment was cancelled. You can try again below.')

    return render(request, 'subscriptions/checkout.html', {
        'plan':      plan,
        'cycle':     cycle,
        'price_usd': price_usd,
        'price_ugx': price_ugx,
        'sub':       sub,
    })


# ── MTN MOBILE MONEY ─────────────────────────────────────────────────────────
@login_required
def mtn_pay(request, plan_slug):
    """Initiate MTN MoMo payment."""
    plan  = get_object_or_404(SubscriptionPlan, slug=plan_slug, is_active=True)
    cycle = request.POST.get('cycle', 'monthly')
    phone = request.POST.get('phone_number', '').strip()

    if not phone:
        messages.error(request, 'Please enter your MTN phone number.')
        return redirect('subscriptions:checkout', plan_slug=plan_slug)

    amount_ugx = int(plan.yearly_ugx if cycle == 'yearly' else plan.monthly_ugx)

    sub, _ = UserSubscription.objects.get_or_create(user=request.user)
    sub.plan          = plan
    sub.billing_cycle = cycle
    sub.status        = UserSubscription.PENDING
    sub.gateway       = UserSubscription.GATEWAY_MTN
    sub.save()

    gw     = MTNMoMoGateway()
    result = gw.request_payment(
        phone_number=phone,
        amount=amount_ugx,
        plan_name=f'JobHub {plan.name} Plan',
        subscription_id=sub.pk,
    )

    if result['success']:
        sub.gateway_ref  = result['reference_id']
        sub.currency_paid = 'UGX'
        sub.amount_paid  = amount_ugx
        sub.save()
        messages.success(
            request,
            f'✅ Payment request sent! Check your phone ({phone}) for the MTN MoMo prompt and approve it.'
        )
        return redirect('subscriptions:payment_pending', ref=result['reference_id'])
    else:
        messages.error(request, f'MTN payment failed: {result["error"]}')
        return redirect('subscriptions:checkout', plan_slug=plan_slug)


@login_required
def mtn_payment_status(request, ref):
    """Poll MTN payment status (AJAX or page refresh)."""
    gw     = MTNMoMoGateway()
    result = gw.check_payment_status(ref)

    if result['status'] == 'SUCCESSFUL':
        try:
            sub = UserSubscription.objects.get(gateway_ref=ref, user=request.user)
            sub.activate(
                gateway    = UserSubscription.GATEWAY_MTN,
                gateway_ref= ref,
                txn_id     = ref,
                amount     = sub.amount_paid,
                currency   = 'UGX',
            )
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'SUCCESSFUL'})
            messages.success(request, '🎉 Payment successful! Your plan is now active.')
            return redirect('subscriptions:success')
        except UserSubscription.DoesNotExist:
            pass

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': result['status']})

    return render(request, 'subscriptions/payment_pending.html', {
        'ref':    ref,
        'status': result['status'],
        'gateway': 'MTN Mobile Money',
    })


@csrf_exempt
def mtn_callback(request):
    """MTN webhook callback — called by MTN servers after payment."""
    if request.method != 'POST':
        return HttpResponse(status=405)
    try:
        data         = json.loads(request.body)
        reference_id = data.get('referenceId') or data.get('externalId', '')
        status       = data.get('status', '')

        if status == 'SUCCESSFUL' and reference_id:
            sub = UserSubscription.objects.filter(gateway_ref=reference_id).first()
            if sub and sub.status == UserSubscription.PENDING:
                sub.activate(
                    gateway    = UserSubscription.GATEWAY_MTN,
                    gateway_ref= reference_id,
                    txn_id     = reference_id,
                    amount     = sub.amount_paid,
                    currency   = 'UGX',
                )
    except Exception:
        pass  # Never expose errors to external callers
    return HttpResponse(status=200)


# ── AIRTEL MONEY ─────────────────────────────────────────────────────────────
@login_required
def airtel_pay(request, plan_slug):
    """Initiate Airtel Money payment."""
    plan  = get_object_or_404(SubscriptionPlan, slug=plan_slug, is_active=True)
    cycle = request.POST.get('cycle', 'monthly')
    phone = request.POST.get('phone_number', '').strip()

    if not phone:
        messages.error(request, 'Please enter your Airtel phone number.')
        return redirect('subscriptions:checkout', plan_slug=plan_slug)

    amount_ugx = int(plan.yearly_ugx if cycle == 'yearly' else plan.monthly_ugx)

    sub, _ = UserSubscription.objects.get_or_create(user=request.user)
    sub.plan          = plan
    sub.billing_cycle = cycle
    sub.status        = UserSubscription.PENDING
    sub.gateway       = UserSubscription.GATEWAY_AIRTEL
    sub.save()

    gw     = AirtelMoneyGateway()
    result = gw.request_payment(
        phone_number=phone,
        amount=amount_ugx,
        plan_name=f'JobHub {plan.name} Plan',
        subscription_id=sub.pk,
    )

    if result['success']:
        sub.gateway_ref   = result['reference_id']
        sub.gateway_txn_id = result.get('transaction_id')
        sub.currency_paid = 'UGX'
        sub.amount_paid   = amount_ugx
        sub.save()
        messages.success(
            request,
            f'✅ Payment request sent! Check your phone ({phone}) for the Airtel Money prompt.'
        )
        return redirect('subscriptions:payment_pending', ref=result['reference_id'])
    else:
        messages.error(request, f'Airtel payment failed: {result["error"]}')
        return redirect('subscriptions:checkout', plan_slug=plan_slug)


@login_required
def airtel_payment_status(request, ref):
    """Poll Airtel payment status."""
    sub = UserSubscription.objects.filter(gateway_ref=ref, user=request.user).first()
    if not sub:
        messages.error(request, 'Transaction not found.')
        return redirect('subscriptions:pricing')

    gw     = AirtelMoneyGateway()
    result = gw.check_payment_status(sub.gateway_txn_id or ref)

    if result['status'] == 'TS':   # TS = Transaction Successful
        sub.activate(
            gateway    = UserSubscription.GATEWAY_AIRTEL,
            gateway_ref= ref,
            txn_id     = sub.gateway_txn_id,
            amount     = sub.amount_paid,
            currency   = 'UGX',
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'SUCCESSFUL'})
        messages.success(request, '🎉 Payment successful! Your plan is now active.')
        return redirect('subscriptions:success')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': result['status']})

    return render(request, 'subscriptions/payment_pending.html', {
        'ref':    ref,
        'status': result['status'],
        'gateway': 'Airtel Money',
    })


@csrf_exempt
def airtel_callback(request):
    """Airtel webhook callback."""
    if request.method != 'POST':
        return HttpResponse(status=405)
    try:
        data      = json.loads(request.body)
        txn       = data.get('transaction', {})
        status    = txn.get('status_code', '')
        txn_id    = txn.get('id', '')

        if status == 'TS' and txn_id:
            sub = UserSubscription.objects.filter(gateway_txn_id=txn_id).first()
            if sub and sub.status == UserSubscription.PENDING:
                sub.activate(
                    gateway    = UserSubscription.GATEWAY_AIRTEL,
                    gateway_ref= sub.gateway_ref,
                    txn_id     = txn_id,
                    amount     = sub.amount_paid,
                    currency   = 'UGX',
                )
    except Exception:
        pass
    return HttpResponse(status=200)


# ── STRIPE ────────────────────────────────────────────────────────────────────
@login_required
def stripe_pay(request, plan_slug):
    """Create Stripe Checkout Session and redirect."""
    plan  = get_object_or_404(SubscriptionPlan, slug=plan_slug, is_active=True)
    cycle = request.POST.get('cycle', 'monthly')

    sub, _ = UserSubscription.objects.get_or_create(user=request.user)
    sub.plan          = plan
    sub.billing_cycle = cycle
    sub.status        = UserSubscription.PENDING
    sub.gateway       = UserSubscription.GATEWAY_STRIPE
    sub.save()

    gw     = StripeGateway()
    result = gw.create_checkout_session(
        request=request,
        plan=plan,
        billing_cycle=cycle,
        subscription_id=sub.pk,
    )

    if result['success']:
        sub.gateway_ref = result['session_id']
        sub.save()
        return redirect(result['checkout_url'])
    else:
        messages.error(request, f'Stripe error: {result["error"]}')
        return redirect('subscriptions:checkout', plan_slug=plan_slug)


@login_required
def stripe_success(request):
    """Stripe redirects here after successful payment."""
    session_id = request.GET.get('session_id')
    sub_id     = request.GET.get('sub_id')

    if not session_id:
        messages.error(request, 'Invalid payment session.')
        return redirect('subscriptions:pricing')

    gw     = StripeGateway()
    result = gw.retrieve_session(session_id)

    if result.get('payment_status') == 'paid':
        try:
            sub = UserSubscription.objects.get(pk=sub_id, user=request.user)
            sub.activate(
                gateway    = UserSubscription.GATEWAY_STRIPE,
                gateway_ref= session_id,
                txn_id     = session_id,
                amount     = result['amount_total'] / 100,  # convert cents
                currency   = result['currency'].upper(),
            )
            messages.success(request, '🎉 Payment successful! Your plan is now active.')
        except UserSubscription.DoesNotExist:
            messages.error(request, 'Subscription not found.')
    else:
        messages.error(request, 'Payment not completed. Please try again.')

    return redirect('subscriptions:success')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Stripe webhook endpoint — verify signature then handle events.
    Register this URL in your Stripe Dashboard → Webhooks.
    """
    payload    = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    gw     = StripeGateway()
    result = gw.verify_webhook(payload, sig_header)

    if not result['success']:
        return HttpResponse(status=400)

    event = result['event']

    if event['type'] == 'checkout.session.completed':
        session  = event['data']['object']
        metadata = session.get('metadata', {})
        sub_id   = metadata.get('subscription_id')

        if session.get('payment_status') == 'paid' and sub_id:
            sub = UserSubscription.objects.filter(pk=sub_id).first()
            if sub and sub.status == UserSubscription.PENDING:
                sub.activate(
                    gateway    = UserSubscription.GATEWAY_STRIPE,
                    gateway_ref= session['id'],
                    txn_id     = session['id'],
                    amount     = session['amount_total'] / 100,
                    currency   = session['currency'].upper(),
                )

    return HttpResponse(status=200)


# ── SHARED VIEWS ──────────────────────────────────────────────────────────────
@login_required
def payment_pending(request, ref):
    """Polling page shown while waiting for Mobile Money confirmation."""
    sub = UserSubscription.objects.filter(gateway_ref=ref, user=request.user).first()
    return render(request, 'subscriptions/payment_pending.html', {
        'ref':     ref,
        'sub':     sub,
        'gateway': sub.get_gateway_display() if sub else 'Mobile Money',
    })


@login_required
def success_view(request):
    return render(request, 'subscriptions/success.html')


@login_required
def cancel_view(request):
    try:
        sub = request.user.subscription
    except UserSubscription.DoesNotExist:
        messages.error(request, 'No active subscription found.')
        return redirect('dashboard:index')

    if request.method == 'POST':
        sub.cancel()
        messages.success(request, 'Your subscription has been cancelled.')
        return redirect('dashboard:index')

    return render(request, 'subscriptions/cancel.html', {'subscription': sub})