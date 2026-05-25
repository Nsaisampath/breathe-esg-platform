from django.contrib import admin
from .models import RawDataIngest


@admin.register(RawDataIngest)
class RawDataIngestAdmin(admin.ModelAdmin):
    list_display = ['company', 'source_type', 'original_filename', 'uploaded_at']
    list_filter = ['source_type', 'company', 'uploaded_at']
    search_fields = ['original_filename', 'company__name']
    readonly_fields = ['uploaded_at', 'raw_payload']
