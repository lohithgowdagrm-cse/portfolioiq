"""Serializers for Risk metrics and stress test requests."""
from rest_framework import serializers
from apps.risk.models import RiskMetricSnapshot


class RiskMetricSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskMetricSnapshot
        fields = (
            "id",
            "calculation_date",
            "volatility_annualized",
            "sharpe_ratio",
            "beta",
            "max_drawdown",
            "var_95_daily",
            "var_99_daily",
            "concentration_herfindahl",
            "sector_exposure",
            "asset_exposure",
            "created_at",
        )


class StressTestRequestSerializer(serializers.Serializer):
    portfolio_id = serializers.UUIDField(required=False)
    market_shock_pct = serializers.FloatField(required=False, default=0.0)
    custom_shocks = serializers.DictField(
        child=serializers.FloatField(),
        required=False,
        default=dict,
    )
