"""Serializers for Portfolio and Position models."""

from apps.portfolios.models import Portfolio, PortfolioSnapshot, Position
from apps.portfolios.services.accounting import PortfolioCalculationService
from rest_framework import serializers


class PositionSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="instrument.symbol", read_only=True)
    instrument_name = serializers.CharField(source="instrument.name", read_only=True)
    asset_class = serializers.CharField(source="instrument.asset_class", read_only=True)
    sector_name = serializers.SerializerMethodField()
    option_desc = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = (
            "id",
            "instrument",
            "symbol",
            "instrument_name",
            "asset_class",
            "sector_name",
            "option_contract",
            "option_desc",
            "quantity",
            "average_buy_price",
            "total_invested",
            "realized_pnl",
            "updated_at",
        )
        read_only_fields = fields

    def get_sector_name(self, obj):
        return obj.instrument.sector.name if obj.instrument.sector else "Unassigned"

    def get_option_desc(self, obj):
        return str(obj.option_contract) if obj.option_contract else None


class PortfolioSerializer(serializers.ModelSerializer):
    total_equity = serializers.SerializerMethodField()
    total_invested = serializers.SerializerMethodField()
    unrealized_pnl = serializers.SerializerMethodField()
    total_return_pct = serializers.SerializerMethodField()
    day_pnl = serializers.SerializerMethodField()
    day_return_pct = serializers.SerializerMethodField()
    positions_count = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = (
            "id",
            "name",
            "description",
            "base_currency",
            "cash_balance",
            "is_default",
            "created_at",
            "updated_at",
            "total_equity",
            "total_invested",
            "unrealized_pnl",
            "total_return_pct",
            "day_pnl",
            "day_return_pct",
            "positions_count",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "total_equity",
            "total_invested",
            "unrealized_pnl",
            "total_return_pct",
            "day_pnl",
            "day_return_pct",
            "positions_count",
        )

    def _get_summary(self, obj):
        if not hasattr(obj, "_cached_summary"):
            obj._cached_summary = PortfolioCalculationService.calculate_portfolio_summary(obj)
        return obj._cached_summary

    def get_total_equity(self, obj):
        return str(self._get_summary(obj)["total_equity"])

    def get_total_invested(self, obj):
        return str(self._get_summary(obj)["invested_capital"])

    def get_unrealized_pnl(self, obj):
        return str(self._get_summary(obj)["unrealized_pnl"])

    def get_total_return_pct(self, obj):
        return float(self._get_summary(obj)["total_return_pct"])

    def get_day_pnl(self, obj):
        return str(self._get_summary(obj)["day_pnl"])

    def get_day_return_pct(self, obj):
        return float(self._get_summary(obj)["day_return_pct"])

    def get_positions_count(self, obj):
        return self._get_summary(obj)["positions_count"]

    def create(self, validated_data):
        user = self.context["request"].user
        # If set to is_default, clear prior default
        if validated_data.get("is_default"):
            Portfolio.objects.filter(user=user, is_default=True).update(is_default=False)
        return Portfolio.objects.create(user=user, **validated_data)


class PortfolioSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioSnapshot
        fields = (
            "id",
            "snapshot_date",
            "total_equity",
            "cash_balance",
            "invested_capital",
            "unrealized_pnl",
            "realized_pnl",
            "day_pnl",
            "day_return_pct",
        )
