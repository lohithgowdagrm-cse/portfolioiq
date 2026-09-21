"""AlertRule and AlertEvent models for proactive portfolio risk management."""
import uuid

from common.utilities.constants import AlertComparator, AlertMetricType
from django.conf import settings
from django.db import models


class AlertRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="alert_rules",
    )
    portfolio = models.ForeignKey(
        "portfolios.Portfolio",
        on_delete=models.CASCADE,
        related_name="alert_rules",
    )
    metric_type = models.CharField(
        max_length=30,
        choices=AlertMetricType.choices,
        db_index=True,
    )
    comparator = models.CharField(
        max_length=10,
        choices=AlertComparator.choices,
        default=AlertComparator.GT,
    )
    threshold_value = models.DecimalField(max_digits=18, decimal_places=4)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alert_rules"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["portfolio", "is_active"]),
        ]

    def __str__(self):
        return f"{self.portfolio.name}: {self.metric_type} {self.comparator} {self.threshold_value}"


class AlertEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(
        AlertRule,
        on_delete=models.CASCADE,
        related_name="events",
    )
    triggered_value = models.DecimalField(max_digits=18, decimal_places=4)
    message = models.TextField()
    is_acknowledged = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "alert_events"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["rule", "-created_at"]),
            models.Index(fields=["is_acknowledged", "-created_at"]),
        ]

    def __str__(self):
        return f"Alert: {self.rule.metric_type} breached at {self.triggered_value} [{self.created_at:%Y-%m-%d %H:%M}]"
