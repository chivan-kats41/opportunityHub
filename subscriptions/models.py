from django.db import models
from django.conf import settings
from django.utils import timezone


class SubscriptionPlan(models.Model):
    JOBSEEKER  = 'jobseeker'
    EMPLOYER   = 'employer'
    ROLE_CHOICES = [(JOBSEEKER, 'Job Seeker'), (EMPLOYER, 'Employer')]

    MONTHLY = 'monthly'
    YEARLY  = 'yearly'
    CYCLE_CHOICES = [(MONTHLY, 'Monthly'), (YEARLY, 'Yearly')]

    name           = models.CharField(max_length=100)
    slug           = models.SlugField(unique=True)
    role           = models.CharField(max_length=20, choices=ROLE_CHOICES)
    monthly_usd    = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    yearly_usd     = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    monthly_ugx    = models.IntegerField(default=0)
    yearly_ugx     = models.IntegerField(default=0)
    max_applications = models.IntegerField(default=5, help_text='-1 = unlimited')
    max_job_posts  = models.IntegerField(default=0)
    is_featured_posts = models.BooleanField(default=False)
    cv_storage     = models.BooleanField(default=False)
    direct_messaging = models.BooleanField(default=False)
    analytics      = models.BooleanField(default=False)
    priority_listing = models.BooleanField(default=False)
    is_active      = models.BooleanField(default=True)
    order          = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['role', 'order']

    def __str__(self):
        return f'{self.name} ({self.get_role_display()})'

    @property
    def yearly_savings_pct(self):
        if self.monthly_usd and self.yearly_usd:
            annual_monthly = self.monthly_usd * 12
            saved = annual_monthly - self.yearly_usd
            return round((saved / annual_monthly) * 100)
        return 0


class UserSubscription(models.Model):
    ACTIVE    = 'active'
    CANCELLED = 'cancelled'
    EXPIRED   = 'expired'
    TRIAL     = 'trial'
    PENDING   = 'pending'   # payment initiated, awaiting confirmation
    STATUS_CHOICES = [
        (ACTIVE,    'Active'),
        (CANCELLED, 'Cancelled'),
        (EXPIRED,   'Expired'),
        (TRIAL,     'Trial'),
        (PENDING,   'Pending Payment'),
    ]

    GATEWAY_MTN    = 'mtn_momo'
    GATEWAY_AIRTEL = 'airtel_money'
    GATEWAY_STRIPE = 'stripe'
    GATEWAY_CHOICES = [
        (GATEWAY_MTN,    'MTN Mobile Money'),
        (GATEWAY_AIRTEL, 'Airtel Money'),
        (GATEWAY_STRIPE, 'Stripe (Card)'),
    ]

    user          = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan          = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    billing_cycle = models.CharField(max_length=10, choices=SubscriptionPlan.CYCLE_CHOICES, default='monthly')
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    # Gateway tracking
    gateway         = models.CharField(max_length=20, choices=GATEWAY_CHOICES, blank=True, null=True)
    gateway_ref     = models.CharField(max_length=255, blank=True, null=True,
                                       help_text='MTN/Airtel reference_id or Stripe session_id')
    gateway_txn_id  = models.CharField(max_length=255, blank=True, null=True,
                                       help_text='Final transaction ID after payment confirmed')
    amount_paid     = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency_paid   = models.CharField(max_length=3, default='UGX')

    started_at    = models.DateTimeField(auto_now_add=True)
    ends_at       = models.DateTimeField(null=True, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    cancelled_at  = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} — {self.plan}'

    @property
    def is_active(self):
        if self.status in (self.ACTIVE, self.TRIAL):
            if self.ends_at and self.ends_at < timezone.now():
                return False
            return True
        return False

    def activate(self, gateway, gateway_ref, txn_id, amount, currency):
        """Call this after payment is confirmed by any gateway."""
        from datetime import timedelta
        self.status        = self.ACTIVE
        self.gateway       = gateway
        self.gateway_ref   = gateway_ref
        self.gateway_txn_id = txn_id
        self.amount_paid   = amount
        self.currency_paid = currency
        # Set expiry
        if self.billing_cycle == 'yearly':
            self.ends_at = timezone.now() + timedelta(days=365)
        else:
            self.ends_at = timezone.now() + timedelta(days=30)
        self.save()

    def cancel(self):
        self.status      = self.CANCELLED
        self.cancelled_at = timezone.now()
        self.save()