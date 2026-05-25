from django.db import models
from apps.companies.models import Company


class RawDataIngest(models.Model):
    """
    Stores untouched raw uploaded data.
    
    Why keep original files?
    - Audit trail: Can always trace back to what was uploaded
    - Re-processing: Can re-normalize if logic changes
    - Compliance: Regulatory requirements
    - Debugging: Can investigate discrepancies
    """
    
    SOURCE_CHOICES = [
        ('SAP', 'SAP ERP'),
        ('UTILITY', 'Utility Billing'),
        ('TRAVEL', 'Travel Data'),
    ]
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='raw_ingests'
    )
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES
    )
    original_filename = models.CharField(max_length=255)
    
    # Store the raw payload as JSON text
    # Could be CSV text, JSON, etc.
    raw_payload = models.TextField()
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.source_type} - {self.original_filename}"
