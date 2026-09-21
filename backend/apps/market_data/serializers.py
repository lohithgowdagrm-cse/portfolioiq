"""Serializers for MarketPrice and historical quote data."""
from apps.market_data.models import MarketPrice
from rest_framework import serializers


class MarketPriceSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="instrument.symbol", read_only=True)

    class Meta:
        model = MarketPrice
        fields = (
            "id",
            "symbol",
            "price",
            "open_price",
            "high_price",
            "low_price",
            "previous_close",
            "change_amount",
            "change_percent",
            "volume",
            "price_timestamp",
        )
