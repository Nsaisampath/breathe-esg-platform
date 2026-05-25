from django.db import models
from apps.companies.models import Company
from apps.uploads.models import RawDataIngest


class EmissionRecord(models.Model):
    """
    Stores normalized emission records ready for review.
    
    Workflow:
    1. File uploaded → RawDataIngest created
    2. File parsed → EmissionRecord created (PENDING)
    3. Check for anomalies (negative values, missing data, spikes)
    4. If anomalies found → status=SUSPICIOUS
    5. Analyst reviews → APPROVED or REJECTED
    """
    
    SCOPE_CHOICES = [
        ('SCOPE_1', 'Scope 1 - Direct'),
        ('SCOPE_2', 'Scope 2 - Indirect (Energy)'),
        ('SCOPE_3', 'Scope 3 - Indirect (Other)'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('SUSPICIOUS', 'Flagged for Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    # Link back to company and original upload
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='emission_records'
    )
    raw_data_ref = models.ForeignKey(
        RawDataIngest,
        on_delete=models.SET_NULL,
        null=True,
        related_name='emission_records'
    )
    
    # Activity type (e.g., "Fuel Consumption", "Electricity Usage")
    activity_type = models.CharField(max_length=255)
    
    # Emissions scope (Scope 1, 2, or 3)
    scope_category = models.CharField(
        max_length=20,
        choices=SCOPE_CHOICES
    )
    
    # Original data before normalization
    original_value = models.DecimalField(max_digits=15, decimal_places=4)
    original_unit = models.CharField(max_length=50)
    
    # Normalized data (standardized units)
    # E.g., all volumes → liters, all energy → kWh
    normalized_value = models.DecimalField(max_digits=15, decimal_places=4)
    normalized_unit = models.CharField(max_length=50)
    
    # Calculated CO2e in kg
    # Example: 1000L diesel = 2680 kg CO2e
    calculated_co2e = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        help_text="CO2e in kilograms"
    )
    
    # Status in approval workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Notes on why record was flagged as suspicious
    anomaly_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company.name} - {self.activity_type} - {self.normalized_value} {self.normalized_unit}"
