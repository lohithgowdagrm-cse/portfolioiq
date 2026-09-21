"""Transaction model storing immutable financial transaction ledger."""
import uuid
from decimal import Decimal

from common.utilities.constants import TransactionType
from django.core.exceptions import ValidationError
from django.db import models


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(
        "portfolios.Portfolio",
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    instrument = models.ForeignKey(
        "instruments.Instrument",
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    option_contract = models.ForeignKey(
        "options.OptionContract",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="transactions",
    )
    transaction_type = models.CharField(
        max_length=15,
        choices=TransactionType.choices,
        db_index=True,
    )
    quantity = models.DecimalField(max_digits=18, decimal_places=4)
    price = models.DecimalField(max_digits=18, decimal_places=4)
    fees = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal("0.0000"))
    taxes = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal("0.0000"))
    total_amount = models.DecimalField(max_digits=18, decimal_places=4)
    executed_at = models.DateTimeField(db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-executed_at", "-created_at"]
        indexes = [
            models.Index(fields=["portfolio", "-executed_at"]),
            models.Index(fields=["instrument", "-executed_at"]),
            models.Index(fields=["transaction_type"]),
        ]

    def clean(self):
        super().clean()
        if self.quantity is not None and self.quantity <= Decimal(0):
            raise ValidationError({"quantity": "Transaction quantity must be strictly greater than zero."})
        if self.price is not None and self.price < Decimal(0):
            raise ValidationError({"price": "Transaction price cannot be negative."})
        if self.fees is not None and self.fees < Decimal(0):
            raise ValidationError({"fees": "Fees cannot be negative."})
        if self.taxes is not None and self.taxes < Decimal(0):
            raise ValidationError({"taxes": "Taxes cannot be negative."})

    def save(self, *args, **kwargs):
        # Auto-compute total_amount if not set
        if self.quantity is not None and self.price is not None:
            gross = self.quantity * self.price
            fees = self.fees or Decimal("0.0000")
            taxes = self.taxes or Decimal("0.0000")
            if self.transaction_type in (TransactionType.BUY, TransactionType.BONUS):
                computed = gross + fees + taxes
            elif self.transaction_type == TransactionType.SELL:
                computed = gross - fees - taxes
            elif self.transaction_type == TransactionType.DIVIDEND:
                computed = gross - taxes
            else:
                computed = gross
            self.total_amount = computed.quantize(Decimal("0.0001"))
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        desc = self.option_contract.__str__() if self.option_contract else self.instrument.symbol
        return f"{self.transaction_type} {self.quantity} {desc} @ {self.price} on {self.executed_at:%Y-%m-%d}"
