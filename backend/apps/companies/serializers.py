from rest_framework import serializers
from apps.companies.models import Company


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializes Company model for API responses.
    
    Used when frontend needs to see company info or create companies.
    """
    class Meta:
        model = Company
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']
