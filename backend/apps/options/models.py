"""Option contract model."""
import uuid

from common.utilities.constants import OptionStyle, OptionType
from django.db import models


class OptionContract(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    underlying = models.ForeignKey(
        "instruments.Instrument",
        on_delete=models.CASCADE,
        related_name="option_contracts",
    )
    option_type = models.CharField(max_length=4, choices=OptionType.choices)
    strike_price = models.DecimalField(max_digits=18, decimal_places=4)
    expiration_date = models.DateField(db_index=True)
    contract_multiplier = models.PositiveIntegerField(default=100)
    style = models.CharField(
        max_length=10,
        choices=OptionStyle.choices,
        default=OptionStyle.EUROPEAN,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "option_contracts"
        ordering = ["expiration_date", "strike_price"]
        unique_together = ("underlying", "option_type", "strike_price", "expiration_date")

    def __str__(self):
        return f"{self.underlying.symbol} {self.expiration_date} {self.strike_price} {self.option_type}"
