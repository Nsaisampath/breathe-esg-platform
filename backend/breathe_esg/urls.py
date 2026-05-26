"""
URL Configuration for breathe_esg project.

This is the main router - it maps URLs to app-specific URLs.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection
from django.db.utils import ProgrammingError

def health_check(request):
    """Simple health check endpoint"""
    db_status = "disconnected"
    tables_status = {}
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "connected"
            
            # Check if table exists
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'records_emissionrecord'
            """)
            if cursor.fetchone():
                tables_status['emission_record'] = 'exists'
            else:
                tables_status['emission_record'] = 'missing'
    except ProgrammingError as e:
        db_status = f"programming error: {str(e)[:100]}"
    except Exception as e:
        db_status = f"error: {str(e)[:100]}"
    
    return JsonResponse({
        'status': 'ok',
        'message': 'Django server is running',
        'database': db_status,
        'tables': tables_status
    })

urlpatterns = [
    path('health/', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('api/uploads/', include('apps.uploads.urls')),
    path('api/records/', include('apps.records.urls')),
    path('api/audit/', include('apps.audit.urls')),
]
