from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ──────────────────────────────────────────────────────────────
# SECURITY: /admin/ is a honeypot — fake login that logs bots.
#           The real admin lives at /secret-admin/
#           Change the secret path before deploying to production!
# ──────────────────────────────────────────────────────────────
urlpatterns = [
    path('admin/',         include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('secret-admin/',  admin.site.urls),

    path('', include('jobs.urls')),
    path('accounts/', include('accounts.urls')),
    path('applications/', include('applications.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('dashboard/', include('accounts.dashboard_urls')),
]  
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)