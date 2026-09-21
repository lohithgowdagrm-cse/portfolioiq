"""Audit logging service."""
import logging

from common.middleware.audit_middleware import get_client_ip, get_current_request

from .models import AuditLog

logger = logging.getLogger(__name__)


def record_audit_log(action: str, entity_type: str, entity_id: str, user=None, metadata: dict = None, ip_address: str = None):
    """
    Records an immutable audit trail entry.
    """
    try:
        request = get_current_request()
        if user is None and request and request.user.is_authenticated:
            user = request.user
        if ip_address is None and request:
            ip_address = get_client_ip(request)

        log_entry = AuditLog.objects.create(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            metadata=metadata or {},
            ip_address=ip_address,
        )
        return log_entry
    except Exception as exc:
        logger.error("Failed to create audit log entry: %s", exc)
        return None
