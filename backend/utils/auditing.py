"""
Audit logging utilities.

Creates audit trail entries for all significant record changes.
"""

from apps.audit.models import AuditLog
from apps.records.models import EmissionRecord
from django.contrib.auth.models import User
from typing import Dict, Any, Optional
import json


def log_record_creation(
    emission_record: EmissionRecord,
    performed_by: Optional[User] = None
) -> AuditLog:
    """
    Log creation of a new emission record.
    
    Args:
        emission_record: The newly created record
        performed_by: User who performed the action (None = system)
    
    Returns:
        The AuditLog entry created
    """
    log_entry = AuditLog.objects.create(
        emission_record=emission_record,
        action='CREATED',
        previous_state=None,
        new_state={
            'status': emission_record.status,
            'normalized_value': str(emission_record.normalized_value),
            'calculated_co2e': str(emission_record.calculated_co2e),
            'scope': emission_record.scope_category,
        },
        performed_by=performed_by
    )
    return log_entry


def log_record_flagged(
    emission_record: EmissionRecord,
    anomalies: list,
    performed_by: Optional[User] = None
) -> AuditLog:
    """
    Log record being flagged as suspicious.
    
    Args:
        emission_record: The record being flagged
        anomalies: List of anomaly reasons
        performed_by: User who performed the action (usually None = system)
    
    Returns:
        The AuditLog entry created
    """
    previous_status = emission_record.status
    
    log_entry = AuditLog.objects.create(
        emission_record=emission_record,
        action='FLAGGED',
        previous_state={
            'status': previous_status,
            'anomaly_notes': emission_record.anomaly_notes,
        },
        new_state={
            'status': 'SUSPICIOUS',
            'anomaly_notes': '\n'.join(anomalies),
        },
        performed_by=performed_by
    )
    return log_entry


def log_record_approval(
    emission_record: EmissionRecord,
    new_status: str,
    notes: str = "",
    performed_by: Optional[User] = None
) -> AuditLog:
    """
    Log record approval or rejection.
    
    Args:
        emission_record: The record being approved/rejected
        new_status: 'APPROVED' or 'REJECTED'
        notes: Analyst notes on the decision
        performed_by: User who performed the approval
    
    Returns:
        The AuditLog entry created
    """
    old_status = emission_record.status
    
    action = 'APPROVED' if new_status == 'APPROVED' else 'REJECTED'
    
    log_entry = AuditLog.objects.create(
        emission_record=emission_record,
        action=action,
        previous_state={
            'status': old_status,
            'anomaly_notes': emission_record.anomaly_notes,
        },
        new_state={
            'status': new_status,
            'anomaly_notes': notes,
        },
        performed_by=performed_by
    )
    return log_entry


def log_record_update(
    emission_record: EmissionRecord,
    changes: Dict[str, tuple],
    performed_by: Optional[User] = None
) -> AuditLog:
    """
    Log data updates to a record.
    
    Args:
        emission_record: The record being updated
        changes: Dict of {field: (old_value, new_value)}
        performed_by: User who performed the update
    
    Returns:
        The AuditLog entry created
    
    Example:
        changes = {
            'calculated_co2e': ('2680', '2700'),
            'anomaly_notes': ('Old notes', 'New notes')
        }
    """
    previous_state = {}
    new_state = {}
    
    for field, (old_val, new_val) in changes.items():
        previous_state[field] = str(old_val)
        new_state[field] = str(new_val)
    
    log_entry = AuditLog.objects.create(
        emission_record=emission_record,
        action='UPDATED',
        previous_state=previous_state,
        new_state=new_state,
        performed_by=performed_by
    )
    return log_entry


def get_record_history(emission_record: EmissionRecord) -> list:
    """
    Get complete change history for a record.
    
    Args:
        emission_record: The record to get history for
    
    Returns:
        List of audit logs in chronological order
    """
    return list(AuditLog.objects.filter(
        emission_record=emission_record
    ).order_by('timestamp'))


def get_formatted_history(emission_record: EmissionRecord) -> str:
    """
    Get human-readable history of all changes.
    
    Args:
        emission_record: The record to get history for
    
    Returns:
        Formatted string with timeline
    """
    logs = get_record_history(emission_record)
    
    if not logs:
        return "No history available"
    
    lines = []
    for i, log in enumerate(logs, 1):
        performer = log.performed_by.username if log.performed_by else "System"
        action_display = log.get_action_display()
        
        lines.append(f"{i}. {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {performer}")
        lines.append(f"   Action: {action_display}")
        
        if log.previous_state:
            lines.append(f"   Before: {log.previous_state}")
        lines.append(f"   After: {log.new_state}")
        lines.append("")
    
    return "\n".join(lines)
