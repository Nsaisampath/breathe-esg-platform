from django.db import models
from django.contrib.auth.models import User
from apps.records.models import EmissionRecord


class AuditLog(models.Model):
    """
    Tracks every action on emission records.
    
    Why audit logs?
    - Compliance: Regulators require change tracking
    - Accountability: Who approved what, when
    - Dispute resolution: What was the original state?
    - Debugging: Trace the history of changes
    """
    
    ACTION_CHOICES = [
        ('CREATED', 'Record Created'),
        ('FLAGGED', 'Flagged as Suspicious'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('UPDATED', 'Data Updated'),
    ]
    
    emission_record = models.ForeignKey(
        EmissionRecord,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )
    
    # Store state snapshots as JSON
    # Example: {"status": "PENDING", "co2e": "2680.00"}
    previous_state = models.JSONField(null=True, blank=True)
    new_state = models.JSONField()
    
    # Who performed the action (null = system)
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_actions'
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        performer = self.performed_by.username if self.performed_by else "System"
        return f"{performer} {self.get_action_display()} on {self.emission_record}"
