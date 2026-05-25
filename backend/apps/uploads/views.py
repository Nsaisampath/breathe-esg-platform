from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from apps.companies.models import Company
from apps.uploads.models import RawDataIngest
from apps.uploads.serializers import RawDataIngestSerializer
from utils.processor import process_sap_upload, process_utility_upload, process_travel_upload


@api_view(['POST'])
def upload_sap_data(request):
    """
    Endpoint: POST /api/uploads/sap/
    
    Receives SAP CSV file content.
    Processes and creates emission records.
    """
    try:
        company_id = request.data.get('company_id')
        filename = request.data.get('filename', 'upload.csv')
        file_content = request.data.get('file_content')
        
        if not all([company_id, file_content]):
            return Response(
                {'error': 'company_id and file_content required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {'error': f'Company {company_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Store raw data first
        raw_ingest = RawDataIngest.objects.create(
            company=company,
            source_type='SAP',
            original_filename=filename,
            raw_payload=file_content
        )
        
        # Process the upload
        results = process_sap_upload(raw_ingest)
        
        # Count successes and failures
        successes = [r for r in results if r[0] == True]
        failures = [r for r in results if r[0] == False]
        
        return Response(
            {
                'message': 'SAP data processed',
                'upload': RawDataIngestSerializer(raw_ingest).data,
                'records_created': len(successes),
                'records_with_errors': len(failures),
                'errors': [f[1] for f in failures] if failures else [],
                'next_step': 'Review flagged records in dashboard'
            },
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def upload_utility_data(request):
    """
    Endpoint: POST /api/uploads/utility/
    
    Receives utility/energy billing CSV file.
    Processes and creates emission records.
    """
    try:
        company_id = request.data.get('company_id')
        filename = request.data.get('filename', 'upload.csv')
        file_content = request.data.get('file_content')
        
        if not all([company_id, file_content]):
            return Response(
                {'error': 'company_id and file_content required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {'error': f'Company {company_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        raw_ingest = RawDataIngest.objects.create(
            company=company,
            source_type='UTILITY',
            original_filename=filename,
            raw_payload=file_content
        )
        
        results = process_utility_upload(raw_ingest)
        
        successes = [r for r in results if r[0] == True]
        failures = [r for r in results if r[0] == False]
        
        return Response(
            {
                'message': 'Utility data processed',
                'upload': RawDataIngestSerializer(raw_ingest).data,
                'records_created': len(successes),
                'records_with_errors': len(failures),
                'errors': [f[1] for f in failures] if failures else [],
            },
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def upload_travel_data(request):
    """
    Endpoint: POST /api/uploads/travel/
    
    Receives travel/flight data as JSON.
    Processes and creates emission records.
    """
    try:
        company_id = request.data.get('company_id')
        filename = request.data.get('filename', 'upload.json')
        file_content = request.data.get('file_content')
        
        if not all([company_id, file_content]):
            return Response(
                {'error': 'company_id and file_content required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response(
                {'error': f'Company {company_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        raw_ingest = RawDataIngest.objects.create(
            company=company,
            source_type='TRAVEL',
            original_filename=filename,
            raw_payload=file_content
        )
        
        results = process_travel_upload(raw_ingest)
        
        successes = [r for r in results if r[0] == True]
        failures = [r for r in results if r[0] == False]
        
        return Response(
            {
                'message': 'Travel data processed',
                'upload': RawDataIngestSerializer(raw_ingest).data,
                'records_created': len(successes),
                'records_with_errors': len(failures),
                'errors': [f[1] for f in failures] if failures else [],
            },
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

