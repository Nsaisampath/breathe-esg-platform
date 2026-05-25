from rest_framework import serializers
from apps.uploads.models import RawDataIngest
from apps.companies.serializers import CompanySerializer


class RawDataIngestSerializer(serializers.ModelSerializer):
    """
    Serializes RawDataIngest model.
    
    Used when uploading files or reviewing upload history.
    - company: Nested company info (read-only in response)
    - raw_payload: Contains the original file content (CSV text, JSON, etc.)
    """
    company = CompanySerializer(read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.companies.models', fromlist=['Company']).Company.objects.all(),
        write_only=True,
        source='company'
    )
    
    class Meta:
        model = RawDataIngest
        fields = ['id', 'company', 'company_id', 'source_type', 'original_filename', 'raw_payload', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

