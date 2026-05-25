from django.contrib import admin
from .models import EmissionRecord


@admin.register(EmissionRecord)
class EmissionRecordAdmin(admin.ModelAdmin):
    list_display = ['company', 'activity_type', 'scope_category', 'status', 'calculated_co2e', 'created_at']
    list_filter = ['status', 'scope_category', 'company', 'created_at']
    search_fields = ['activity_type', 'company__name', 'anomaly_notes']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Company & Source', {
            'fields': ('company', 'raw_data_ref')
        }),
        ('Activity Details', {
            'fields': ('activity_type', 'scope_category')
        }),
        ('Original Data', {
            'fields': ('original_value', 'original_unit')
        }),
        ('Normalized Data', {
            'fields': ('normalized_value', 'normalized_unit')
        }),
        ('CO2e Calculation', {
            'fields': ('calculated_co2e',)
        }),
        ('Status & Notes', {
            'fields': ('status', 'anomaly_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
