"""Serializers for AlertRule and AlertEvent."""
from apps.alerts.models import AlertEvent, AlertRule
from rest_framework import serializers


class AlertRuleSerializer(serializers.ModelSerializer):
    portfolio_name = serializers.CharField(source="portfolio.name", read_only=True)

    class Meta:
        model = AlertRule
        fields = (
            "id",
            "portfolio",
            "portfolio_name",
            "metric_type",
            "comparator",
            "threshold_value",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate_portfolio(self, value):
        user = self.context["request"].user
        if value.user != user:
            raise serializers.ValidationError("You do not own this portfolio.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        return AlertRule.objects.create(user=user, **validated_data)


class AlertEventSerializer(serializers.ModelSerializer):
    metric_type = serializers.CharField(source="rule.metric_type", read_only=True)
    portfolio_name = serializers.CharField(source="rule.portfolio.name", read_only=True)
    threshold_value = serializers.CharField(source="rule.threshold_value", read_only=True)

    class Meta:
        model = AlertEvent
        fields = (
            "id",
            "rule",
            "metric_type",
            "portfolio_name",
            "threshold_value",
            "triggered_value",
            "message",
            "is_acknowledged",
            "created_at",
        )
        read_only_fields = fields
