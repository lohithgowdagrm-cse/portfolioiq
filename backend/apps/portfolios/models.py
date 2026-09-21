"""Portfolio, Position, and PortfolioSnapshot models."""
import uuid
from decimal import Decimal

from common.utilities.constants import BaseCurrency
from django.conf import settings
from django.db import models


class Portfolio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolios",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    base_currency = models.CharField(
        max_length=3,
        choices=BaseCurrency.choices,
        default=BaseCurrency.INR,
    )
    cash_balance = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "portfolios"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.user.email})"


class Position(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="positions",
    )
    instrument = models.ForeignKey(
        "instruments.Instrument",
        on_delete=models.PROTECT,
        related_name="positions",
    )
    option_contract = models.ForeignKey(
        "options.OptionContract",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="positions",
    )
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )
    average_buy_price = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )
    total_invested = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )
    realized_pnl = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal("0.0000"),
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "positions"
        indexes = [
            models.Index(fields=["portfolio", "instrument"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["portfolio", "instrument"],
                condition=models.Q(option_contract__isnull=True),
                name="unique_equity_position_per_portfolio",
            ),
            models.UniqueConstraint(
                fields=["portfolio", "instrument", "option_contract"],
                condition=models.Q(option_contract__isnull=False),
                name="unique_option_position_per_portfolio",
            ),
        ]

    def __str__(self):
        desc = self.option_contract.__str__() if self.option_contract else self.instrument.symbol
        return f"{self.portfolio.name} - {desc}: {self.quantity} shares"


class PortfolioSnapshot(models.Model):
    """Daily equity, cash, and P&L snapshot for historical analytics."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name="snapshots",
    )
    snapshot_date = models.DateField(db_index=True)
    total_equity = models.DecimalField(max_digits=18, decimal_places=4)
    cash_balance = models.DecimalField(max_digits=18, decimal_places=4)
    invested_capital = models.DecimalField(max_digits=18, decimal_places=4)
    unrealized_pnl = models.DecimalField(max_digits=18, decimal_places=4)
    realized_pnl = models.DecimalField(max_digits=18, decimal_places=4)
    day_pnl = models.DecimalField(max_digits=18, decimal_places=4)
    day_return_pct = models.DecimalField(max_digits=8, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "portfolio_snapshots"
        ordering = ["-snapshot_date"]
        unique_together = ("portfolio", "snapshot_date")
        indexes = [
            models.Index(fields=["portfolio", "-snapshot_date"]),
        ]

    def __str__(self):
        return f"{self.portfolio.name} [{self.snapshot_date}] Equity: {self.total_equity}"
