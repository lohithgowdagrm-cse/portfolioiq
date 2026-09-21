"""Serializers for OptionContract and options positions."""
from rest_framework import serializers
from apps.options.models import OptionContract


class OptionContractSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="underlying.symbol", read_only=True)
    underlying_name = serializers.CharField(source="underlying.name", read_only=True)

    class Meta:
        model = OptionContract
        fields = (
            "id",
            "underlying",
            "symbol",
            "underlying_name",
            "option_type",
            "strike_price",
            "expiration_date",
            "contract_multiplier",
            "style",
            "created_at",
        )
