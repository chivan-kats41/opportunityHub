from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    # Pricing & checkout
    path('pricing/',                        views.pricing_view,        name='pricing'),
    path('checkout/<slug:plan_slug>/',       views.checkout_view,       name='checkout'),

    # MTN Mobile Money
    path('mtn/pay/<slug:plan_slug>/',        views.mtn_pay,             name='mtn_pay'),
    path('mtn/status/<str:ref>/',            views.mtn_payment_status,  name='mtn_status'),
    path('mtn/callback/',                    views.mtn_callback,        name='mtn_callback'),

    # Airtel Money
    path('airtel/pay/<slug:plan_slug>/',     views.airtel_pay,          name='airtel_pay'),
    path('airtel/status/<str:ref>/',         views.airtel_payment_status, name='airtel_status'),
    path('airtel/callback/',                 views.airtel_callback,     name='airtel_callback'),

    # Stripe
    path('stripe/pay/<slug:plan_slug>/',     views.stripe_pay,          name='stripe_pay'),
    path('stripe/success/',                  views.stripe_success,      name='stripe_success'),
    path('stripe/webhook/',                  views.stripe_webhook,      name='stripe_webhook'),

    # Shared
    path('pending/<str:ref>/',              views.payment_pending,      name='payment_pending'),
    path('success/',                         views.success_view,        name='success'),
    path('cancel/',                          views.cancel_view,         name='cancel'),
]