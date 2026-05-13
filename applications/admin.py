from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display  = ['applicant', 'job', 'status', 'applied_at']
    list_filter   = ['status', 'applied_at']
    search_fields = ['applicant__username', 'applicant__email', 'job__title']
    list_editable = ['status']
    raw_id_fields = ['applicant', 'job']
    date_hierarchy = 'applied_at'