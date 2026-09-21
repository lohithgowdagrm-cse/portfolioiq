"""Serializers for MarketPrice and historical quote data."""
from rest_framework import serializers
from apps.market_data.models import MarketPrice


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
