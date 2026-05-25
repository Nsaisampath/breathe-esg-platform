from rest_framework import serializers
from apps.records.models import EmissionRecord
from apps.companies.serializers import CompanySerializer


class EmissionRecordListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing emission records.
    
    Used in table views - only essential fields to keep response lightweight.
    """
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = EmissionRecord
        fields = [
            'id',
            'company_name',
            'activity_type',
            'scope_category',
            'normalized_value',
            'normalized_unit',
            'calculated_co2e',
            'status',
            'created_at'
        ]


class EmissionRecordDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for detailed emission record views.
    
    Used when analyst reviews a specific record.
    Shows original values, normalized values, and anomaly notes.
    """
    company = CompanySerializer(read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.companies.models', fromlist=['Company']).Company.objects.all(),
        write_only=True,
        source='company'
    )
    
    class Meta:
        model = EmissionRecord
        fields = [
            'id',
            'company',
            'company_id',
            'raw_data_ref',
            'activity_type',
            'scope_category',
            'original_value',
            'original_unit',
            'normalized_value',
            'normalized_unit',
            'calculated_co2e',
            'status',
            'anomaly_notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmissionRecordApprovalSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for approval actions.
    
    Analyst only updates status and possibly anomaly_notes.
    """
    class Meta:
        model = EmissionRecord
        fields = ['id', 'status', 'anomaly_notes']
        read_only_fields = ['id']

