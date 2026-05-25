from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from apps.records.models import EmissionRecord
from apps.records.serializers import (
    EmissionRecordListSerializer,
    EmissionRecordDetailSerializer,
    EmissionRecordApprovalSerializer
)
from apps.audit.models import AuditLog
import json


class EmissionRecordPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
def list_records(request):
    """
    Endpoint: GET /api/records/
    
    List all emission records with filtering.
    
    Query parameters:
    - company_id: Filter by company
    - status: Filter by status (PENDING, APPROVED, SUSPICIOUS, REJECTED)
    - scope: Filter by scope (SCOPE_1, SCOPE_2, SCOPE_3)
    - page: Page number (default 1)
    - page_size: Records per page (default 50)
    
    Example:
    GET /api/records/?status=SUSPICIOUS&page=1
    """
    # Start with all records
    queryset = EmissionRecord.objects.all()
    
    # Filter by company
    company_id = request.query_params.get('company_id')
    if company_id:
        queryset = queryset.filter(company_id=company_id)
    
    # Filter by status
    status_filter = request.query_params.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    # Filter by scope
    scope_filter = request.query_params.get('scope')
    if scope_filter:
        queryset = queryset.filter(scope_category=scope_filter)
    
    # Paginate
    paginator = EmissionRecordPagination()
    page = paginator.paginate_queryset(queryset, request)
    
    if page is not None:
        serializer = EmissionRecordListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = EmissionRecordListSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def record_detail(request, record_id):
    """
    Endpoint: GET /api/records/{record_id}/
    
    Get full details of a single emission record.
    
    Shows:
    - Original values from upload
    - Normalized values
    - CO2e calculation
    - Status and anomaly notes
    - Related audit history
    """
    try:
        record = EmissionRecord.objects.get(id=record_id)
    except EmissionRecord.DoesNotExist:
        return Response(
            {'error': f'Record {record_id} not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get audit history
    audit_logs = AuditLog.objects.filter(emission_record=record)
    audit_data = []
    for log in audit_logs:
        audit_data.append({
            'action': log.get_action_display(),
            'timestamp': log.timestamp,
            'performed_by': log.performed_by.username if log.performed_by else 'System',
            'new_state': log.new_state
        })
    
    serializer = EmissionRecordDetailSerializer(record)
    return Response({
        'record': serializer.data,
        'audit_history': audit_data
    })


@api_view(['POST'])
def approve_record(request, record_id):
    """
    Endpoint: POST /api/records/{record_id}/approve/
    
    Analyst approves or rejects a record.
    
    Request body:
    {
        "status": "APPROVED",  # or "REJECTED"
        "anomaly_notes": "Looks good after review"
    }
    
    This endpoint:
    1. Updates record status
    2. Creates audit log entry
    3. Records who approved it
    4. Returns updated record
    """
    try:
        record = EmissionRecord.objects.get(id=record_id)
    except EmissionRecord.DoesNotExist:
        return Response(
            {'error': f'Record {record_id} not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    new_status = request.data.get('status')
    anomaly_notes = request.data.get('anomaly_notes', '')
    
    # Validate status
    valid_statuses = ['APPROVED', 'REJECTED', 'PENDING']
    if new_status not in valid_statuses:
        return Response(
            {'error': f'Invalid status. Must be one of: {valid_statuses}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Store previous state for audit
    previous_state = {
        'status': record.status,
        'anomaly_notes': record.anomaly_notes
    }
    
    # Update record
    record.status = new_status
    record.anomaly_notes = anomaly_notes
    record.save()
    
    # Create audit log
    AuditLog.objects.create(
        emission_record=record,
        action='APPROVED' if new_status == 'APPROVED' else 'REJECTED',
        previous_state=previous_state,
        new_state={
            'status': record.status,
            'anomaly_notes': record.anomaly_notes
        },
        performed_by=request.user if request.user.is_authenticated else None
    )
    
    serializer = EmissionRecordDetailSerializer(record)
    return Response({
        'message': f'Record {new_status.lower()}',
        'record': serializer.data
    })


@api_view(['GET'])
def get_summary(request):
    """
    Endpoint: GET /api/records/summary/
    
    Get dashboard summary stats.
    
    Returns counts of:
    - Total records
    - Pending review
    - Flagged as suspicious
    - Approved
    - By company
    """
    company_id = request.query_params.get('company_id')
    
    if company_id:
        records = EmissionRecord.objects.filter(company_id=company_id)
    else:
        records = EmissionRecord.objects.all()
    
    return Response({
        'total_records': records.count(),
        'pending': records.filter(status='PENDING').count(),
        'suspicious': records.filter(status='SUSPICIOUS').count(),
        'approved': records.filter(status='APPROVED').count(),
        'rejected': records.filter(status='REJECTED').count(),
        'total_co2e': float(sum(r.calculated_co2e for r in records)) if records else 0
    })

