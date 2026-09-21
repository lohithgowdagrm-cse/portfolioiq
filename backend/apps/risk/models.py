"""RiskMetricSnapshot model for historical risk tracking."""
import uuid

from django.db import models


class RiskMetricSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(
        "portfolios.Portfolio",
        on_delete=models.CASCADE,
        related_name="risk_snapshots",
    )
    calculation_date = models.DateField(db_index=True)
    volatility_annualized = models.DecimalField(max_digits=10, decimal_places=4)
    sharpe_ratio = models.DecimalField(max_digits=10, decimal_places=4)
    beta = models.DecimalField(max_digits=10, decimal_places=4)
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=4)
    var_95_daily = models.DecimalField(max_digits=18, decimal_places=4)
    var_99_daily = models.DecimalField(max_digits=18, decimal_places=4)
    concentration_herfindahl = models.DecimalField(max_digits=10, decimal_places=4)
    sector_exposure = models.JSONField(default=dict)
    asset_exposure = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "risk_metric_snapshots"
        ordering = ["-calculation_date"]
        unique_together = ("portfolio", "calculation_date")
        indexes = [
            models.Index(fields=["portfolio", "-calculation_date"]),
        ]

    def __str__(self):
        return f"{self.portfolio.name} [{self.calculation_date}] Sharpe: {self.sharpe_ratio}, Beta: {self.beta}"
