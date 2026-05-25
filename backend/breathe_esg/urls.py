"""
URL Configuration for breathe_esg project.

This is the main router - it maps URLs to app-specific URLs.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/uploads/', include('apps.uploads.urls')),
    path('api/records/', include('apps.records.urls')),
    path('api/audit/', include('apps.audit.urls')),
]
