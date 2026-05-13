from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'email', 'role', 'first_name', 'last_name', 'is_active']
    list_filter   = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'company_name']
    fieldsets     = UserAdmin.fieldsets + (
        ('JobHub Profile', {'fields': ('role', 'phone', 'bio', 'profile_photo', 'company_name', 'website')}),
    )