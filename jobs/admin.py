from django.contrib import admin
from .models import Category, Job


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display  = ['title', 'company_name', 'location', 'job_type', 'is_active', 'is_featured', 'created_at']
    list_filter   = ['job_type', 'is_active', 'is_featured', 'category']
    search_fields = ['title', 'company_name', 'location']
    list_editable = ['is_active', 'is_featured']
    date_hierarchy = 'created_at'
    raw_id_fields  = ['employer']