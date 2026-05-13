from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display  = ['name', 'role', 'monthly_usd', 'yearly_usd', 'monthly_ugx', 'is_active', 'order']
    list_filter   = ['role', 'is_active']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display  = ['user', 'plan', 'billing_cycle', 'status', 'started_at', 'ends_at']
    list_filter   = ['status', 'billing_cycle']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']