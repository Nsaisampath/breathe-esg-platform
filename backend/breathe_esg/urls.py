"""
URL Configuration for breathe_esg project.

This is the main router - it maps URLs to app-specific URLs.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    """Simple health check endpoint"""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return JsonResponse({
        'status': 'ok',
        'message': 'Django server is running',
        'database': db_status
    })

urlpatterns = [
    path('health/', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('api/uploads/', include('apps.uploads.urls')),
    path('api/records/', include('apps.records.urls')),
    path('api/audit/', include('apps.audit.urls')),
]
