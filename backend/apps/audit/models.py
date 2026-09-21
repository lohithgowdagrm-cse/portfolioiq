"""AuditLog model tracking critical portfolio and financial operations."""
from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=100, db_index=True)
    entity_type = models.CharField(max_length=50, db_index=True)
    entity_id = models.CharField(max_length=100, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "-timestamp"]),
            models.Index(fields=["entity_type", "entity_id"]),
        ]

    def __str__(self):
        user_str = self.user.email if self.user else "Anonymous"
        return f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] {user_str} - {self.action} on {self.entity_type}:{self.entity_id}"
