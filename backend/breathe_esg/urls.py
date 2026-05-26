"""
URL Configuration for breathe_esg project.

This is the main router - it maps URLs to app-specific URLs.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({'status': 'ok', 'message': 'Django server is running'})

urlpatterns = [
    path('health/', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('api/uploads/', include('apps.uploads.urls')),
    path('api/records/', include('apps.records.urls')),
    path('api/audit/', include('apps.audit.urls')),
]
