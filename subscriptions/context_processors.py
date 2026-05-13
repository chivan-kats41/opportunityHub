def user_subscription(request):
    """Inject current user's subscription into every template context."""
    if request.user.is_authenticated:
        try:
            sub = request.user.subscription
            return {
                'user_subscription': sub,
                'user_plan': sub.plan,
                'subscription_active': sub.is_active,
            }
        except Exception:
            pass
    return {
        'user_subscription': None,
        'user_plan': None,
        'subscription_active': False,
    }