"""MarketPrice model storing tick and historical quote prices."""
from django.db import models


class MarketPrice(models.Model):
    id = models.BigAutoField(primary_key=True)
    instrument = models.ForeignKey(
        "instruments.Instrument",
        on_delete=models.CASCADE,
        related_name="market_prices",
        db_index=True,
    )
    price = models.DecimalField(max_digits=18, decimal_places=4)
    open_price = models.DecimalField(max_digits=18, decimal_places=4)
    high_price = models.DecimalField(max_digits=18, decimal_places=4)
    low_price = models.DecimalField(max_digits=18, decimal_places=4)
    previous_close = models.DecimalField(max_digits=18, decimal_places=4)
    change_amount = models.DecimalField(max_digits=18, decimal_places=4)
    change_percent = models.DecimalField(max_digits=8, decimal_places=4)
    volume = models.BigIntegerField(default=0)
    price_timestamp = models.DateTimeField(db_index=True)

    class Meta:
        db_table = "market_prices"
        ordering = ["-price_timestamp"]
        indexes = [
            models.Index(fields=["instrument", "-price_timestamp"]),
        ]

    def __str__(self):
        return f"{self.instrument.symbol}: {self.price} ({self.change_percent}%) @ {self.price_timestamp:%Y-%m-%d %H:%M}"
