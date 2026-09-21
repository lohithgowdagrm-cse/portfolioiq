"""Serializers for financial transactions."""
from rest_framework import serializers
from decimal import Decimal
from apps.transactions.models import Transaction
from apps.instruments.models import Instrument
from apps.portfolios.models import Portfolio
from apps.options.models import OptionContract


class TransactionSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="instrument.symbol", read_only=True)
    instrument_name = serializers.CharField(source="instrument.name", read_only=True)
    option_desc = serializers.SerializerMethodField()
    executed_at = serializers.DateTimeField(required=False)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "portfolio",
            "instrument",
            "symbol",
            "instrument_name",
            "option_contract",
            "option_desc",
            "transaction_type",
            "quantity",
            "price",
            "fees",
            "taxes",
            "total_amount",
            "executed_at",
            "notes",
            "created_at",
        )
        read_only_fields = ("id", "total_amount", "created_at")

    def get_option_desc(self, obj):
        return str(obj.option_contract) if obj.option_contract else None

    def validate(self, attrs):
        # Validate portfolio ownership
        user = self.context["request"].user
        portfolio = attrs.get("portfolio")
        if portfolio and portfolio.user != user:
            raise serializers.ValidationError({"portfolio": "You do not own the specified portfolio."})

        qty = attrs.get("quantity")
        if qty is not None and qty <= Decimal("0"):
            raise serializers.ValidationError({"quantity": "Quantity must be strictly positive."})

        price = attrs.get("price")
        if price is not None and price < Decimal("0"):
            raise serializers.ValidationError({"price": "Price cannot be negative."})

        return attrs
