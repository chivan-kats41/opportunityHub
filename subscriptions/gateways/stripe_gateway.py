"""
Stripe Payment Gateway
Docs: https://stripe.com/docs/api
Uses: Stripe Checkout Sessions (hosted payment page — no PCI scope for us)

Flow:
  1. Create a Checkout Session → redirect user to Stripe's hosted page
  2. User pays with card on Stripe's page
  3. Stripe redirects back to our success/cancel URL
  4. Stripe also sends a webhook event payment_intent.succeeded
  5. We verify webhook signature and activate subscription
"""
import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeGateway:

    # UGX is not supported by Stripe — use USD and convert
    # Stripe amounts are in the smallest currency unit (cents for USD)
    SUPPORTED_CURRENCIES = ['usd', 'eur', 'gbp', 'kes', 'tzs', 'rwf']
    DEFAULT_CURRENCY      = 'usd'

    def create_checkout_session(self, request, plan, billing_cycle: str,
                                 subscription_id: int) -> dict:
        """
        Create a Stripe Checkout Session.

        Args:
            request:         Django request (used to build absolute URLs)
            plan:            SubscriptionPlan instance
            billing_cycle:   'monthly' | 'yearly'
            subscription_id: Our internal UserSubscription PK

        Returns:
            {
              'success':     bool,
              'session_id':  str | None,   # Pass to Stripe.js redirectToCheckout
              'checkout_url': str | None,  # Or redirect directly to this URL
              'error':       str | None,
            }
        """
        amount_usd = plan.yearly_usd if billing_cycle == 'yearly' else plan.monthly_usd
        # Stripe amount in cents
        amount_cents = int(float(amount_usd) * 100)

        if amount_cents == 0:
            return {
                'success':      False,
                'session_id':   None,
                'checkout_url': None,
                'error':        'Free plan — no payment required.',
            }

        success_url = request.build_absolute_uri(
            reverse('subscriptions:stripe_success') + f'?session_id={{CHECKOUT_SESSION_ID}}&sub_id={subscription_id}'
        )
        cancel_url = request.build_absolute_uri(
            reverse('subscriptions:checkout', kwargs={'plan_slug': plan.slug}) + f'?cycle={billing_cycle}&cancelled=1'
        )

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency':     self.DEFAULT_CURRENCY,
                        'unit_amount':  amount_cents,
                        'product_data': {
                            'name':        f'JobHub {plan.name} Plan',
                            'description': (
                                f'{"Annual" if billing_cycle == "yearly" else "Monthly"} '
                                f'subscription — {plan.get_role_display()}'
                            ),
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'subscription_id': str(subscription_id),
                    'plan_id':         str(plan.pk),
                    'plan_name':       plan.name,
                    'billing_cycle':   billing_cycle,
                },
                # Pre-fill email if we have it
                customer_email=getattr(request.user, 'email', None),
            )
            return {
                'success':      True,
                'session_id':   session.id,
                'checkout_url': session.url,
                'error':        None,
            }
        except stripe.error.StripeError as e:
            return {
                'success':      False,
                'session_id':   None,
                'checkout_url': None,
                'error':        str(e.user_message),
            }

    def verify_webhook(self, payload: bytes, sig_header: str) -> dict:
        """
        Verify an incoming Stripe webhook signature and return the event.

        Args:
            payload:    Raw request body bytes
            sig_header: Value of 'Stripe-Signature' header

        Returns:
            {
              'success': bool,
              'event':   stripe.Event | None,
              'error':   str | None,
            }
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return {'success': True, 'event': event, 'error': None}
        except stripe.error.SignatureVerificationError as e:
            return {'success': False, 'event': None, 'error': str(e)}

    def retrieve_session(self, session_id: str) -> dict:
        """Retrieve a completed checkout session to verify payment."""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                'success':        True,
                'payment_status': session.payment_status,  # 'paid' | 'unpaid'
                'amount_total':   session.amount_total,
                'currency':       session.currency,
                'metadata':       dict(session.metadata),
                'customer_email': session.customer_details.email if session.customer_details else None,
            }
        except stripe.error.StripeError as e:
            return {'success': False, 'error': str(e)}