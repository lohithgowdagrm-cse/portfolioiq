"""Serializers for Sector and Instrument models."""
from rest_framework import serializers
from .models import Sector, Instrument


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ("id", "name", "code", "description")


class InstrumentSerializer(serializers.ModelSerializer):
    sector_name = serializers.CharField(source="sector.name", read_only=True)
    latest_price = serializers.SerializerMethodField()
    change_percent = serializers.SerializerMethodField()

    class Meta:
        model = Instrument
        fields = (
            "id",
            "symbol",
            "name",
            "asset_class",
            "sector",
            "sector_name",
            "exchange",
            "currency",
            "is_active",
            "latest_price",
            "change_percent",
            "created_at",
        )

    def get_latest_price(self, obj):
        price_obj = getattr(obj, "latest_market_price", None)
        if price_obj:
            return str(price_obj.price)
        latest = obj.market_prices.order_by("-price_timestamp").first()
        return str(latest.price) if latest else None

    def get_change_percent(self, obj):
        price_obj = getattr(obj, "latest_market_price", None)
        if price_obj:
            return float(price_obj.change_percent)
        latest = obj.market_prices.order_by("-price_timestamp").first()
        return float(latest.change_percent) if latest else 0.0
