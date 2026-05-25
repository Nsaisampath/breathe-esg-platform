from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['emission_record', 'action', 'performed_by', 'timestamp']
    list_filter = ['action', 'timestamp', 'performed_by']
    search_fields = ['emission_record__activity_type', 'performed_by__username']
    readonly_fields = ['timestamp', 'emission_record', 'action', 'previous_state', 'new_state', 'performed_by']
