"""Master risk analytics service coordinating all metric calculations."""
import logging
from typing import Any

from apps.market_data.models import MarketPrice
from apps.portfolios.models import Portfolio, PortfolioSnapshot
from apps.portfolios.services.accounting import PortfolioCalculationService
from apps.risk.models import RiskMetricSnapshot
from django.utils import timezone

from .beta import calculate_portfolio_beta
from .concentration import calculate_concentration_metrics
from .drawdown import calculate_maximum_drawdown
from .sharpe import calculate_sharpe_ratio
from .var import calculate_historical_var
from .volatility import calculate_annualized_volatility

logger = logging.getLogger(__name__)


class RiskAnalyticsService:
    """
    Central facade for computing portfolio risk profile, exposure distribution, and VaR.
    """

    @classmethod
    def get_historical_returns(cls, portfolio: Portfolio, lookback_days: int = 90) -> list[float]:
        """
        Extracts daily percentage returns from portfolio snapshots.
        """
        snapshots = PortfolioSnapshot.objects.filter(
            portfolio=portfolio
        ).order_by("snapshot_date")[:lookback_days]

        returns = [float(s.day_return_pct) / 100.0 for s in snapshots if s.day_return_pct is not None]
        return returns

    @classmethod
    def get_benchmark_returns(cls, symbol: str = "NIFTY50", lookback_days: int = 90) -> list[float]:
        """
        Fetches historical daily returns for benchmark index.
        """
        prices = MarketPrice.objects.filter(
            instrument__symbol=symbol
        ).order_by("price_timestamp")[:lookback_days]

        returns = [float(p.change_percent) / 100.0 for p in prices if p.change_percent is not None]
        return returns

    @classmethod
    def calculate_portfolio_risk(cls, portfolio: Portfolio) -> dict[str, Any]:
        """
        Calculates complete institutional risk profile for portfolio.
        """
        summary = PortfolioCalculationService.calculate_portfolio_summary(portfolio)
        total_equity = summary["total_equity"]
        portfolio_returns = cls.get_historical_returns(portfolio)
        benchmark_returns = cls.get_benchmark_returns("NIFTY50")

        # Snapshots for equity curve
        snapshots = PortfolioSnapshot.objects.filter(portfolio=portfolio).order_by("snapshot_date")
        equity_series = [float(s.total_equity) for s in snapshots]
        if not equity_series and total_equity > 0:
            equity_series = [float(total_equity)]

        # 1. Volatility
        volatility = calculate_annualized_volatility(portfolio_returns)

        # 2. Sharpe Ratio (6.5% risk free rate)
        sharpe = calculate_sharpe_ratio(portfolio_returns, annual_risk_free_rate=0.065)

        # 3. Beta vs NIFTY50
        beta = calculate_portfolio_beta(portfolio_returns, benchmark_returns)

        # 4. Maximum Drawdown
        drawdown_data = calculate_maximum_drawdown(equity_series)

        # 5. Historical Value at Risk (VaR 95% & 99%)
        var_data = calculate_historical_var(portfolio_returns, total_equity)

        # 6. Concentration & Exposure
        concentration = calculate_concentration_metrics(summary["positions"], total_equity)

        return {
            "portfolio_id": str(portfolio.id),
            "portfolio_name": portfolio.name,
            "calculation_date": timezone.now().date().isoformat(),
            "metrics": {
                "volatility_annualized": volatility,
                "sharpe_ratio": sharpe,
                "beta": beta,
                "max_drawdown_pct": drawdown_data["max_drawdown_pct"],
                "var_95_dollar": var_data["var_95_dollar"],
                "var_95_pct": var_data["var_95_pct"],
                "var_99_dollar": var_data["var_99_dollar"],
                "var_99_pct": var_data["var_99_pct"],
                "herfindahl_index": concentration["herfindahl_index"],
                "top_position_weight_pct": concentration["top_position_weight_pct"],
                "top_3_concentration_pct": concentration["top_3_concentration_pct"],
            },
            "drawdown": drawdown_data,
            "exposure": {
                "sectors": concentration["sector_weights"],
                "asset_classes": concentration["asset_class_weights"],
            },
            "var_details": var_data,
        }

    @classmethod
    def save_daily_risk_snapshot(cls, portfolio: Portfolio, date=None) -> RiskMetricSnapshot:
        """
        Saves today's risk metrics to database for historical auditing and compliance.
        """
        if date is None:
            date = timezone.now().date()

        risk_data = cls.calculate_portfolio_risk(portfolio)
        m = risk_data["metrics"]

        snapshot, _ = RiskMetricSnapshot.objects.update_or_create(
            portfolio=portfolio,
            calculation_date=date,
            defaults={
                "volatility_annualized": m["volatility_annualized"],
                "sharpe_ratio": m["sharpe_ratio"],
                "beta": m["beta"],
                "max_drawdown": m["max_drawdown_pct"],
                "var_95_daily": m["var_95_dollar"],
                "var_99_daily": m["var_99_dollar"],
                "concentration_herfindahl": m["herfindahl_index"],
                "sector_exposure": risk_data["exposure"]["sectors"],
                "asset_exposure": risk_data["exposure"]["asset_classes"],
            },
        )
        return snapshot
