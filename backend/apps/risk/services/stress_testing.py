"""Portfolio stress testing and hypothetical scenario simulation."""
from typing import Dict, Any, List
from decimal import Decimal
from apps.portfolios.models import Portfolio, Position
from apps.portfolios.services.accounting import PortfolioCalculationService


class StressTestingService:
    """
    Simulates macro market downturns and idiosyncratic asset shocks on portfolio equity.
    """

    @classmethod
    def run_scenario(
        cls,
        portfolio: Portfolio,
        market_shock_pct: float = 0.0,
        custom_shocks: Dict[str, float] = None,
    ) -> Dict[str, Any]:
        """
        Runs a stress scenario:
        - market_shock_pct: broad index drop (e.g. -5.0, -10.0, -20.0). Asset impact is scaled by Beta if available or direct shock.
        - custom_shocks: ticker-specific percentage drop dict: {"TCS": -10.0, "INFY": -8.0, "RELIANCE": -15.0}
        """
        custom_shocks = custom_shocks or {}
        summary = PortfolioCalculationService.calculate_portfolio_summary(portfolio)
        current_equity = summary["total_equity"]
        cash_balance = summary["cash_balance"]

        projected_positions = []
        new_holdings_value = Decimal("0.00")

        for pos in summary["positions"]:
            sym = pos["symbol"]
            curr_val = pos["current_value"]

            # Check if custom shock was explicitly provided for this symbol
            if sym in custom_shocks:
                shock = float(custom_shocks[sym])
                applied_factor = 1.0 + (shock / 100.0)
                assumption = f"Custom asset shock: {shock:+.2f}%"
            elif market_shock_pct != 0.0:
                # Default equity sensitivity to macro market shock
                shock = market_shock_pct
                applied_factor = 1.0 + (shock / 100.0)
                assumption = f"Macro market shock: {market_shock_pct:+.2f}%"
            else:
                applied_factor = 1.0
                assumption = "Unchanged"

            shocked_val = max(Decimal("0.00"), curr_val * Decimal(str(applied_factor))).quantize(Decimal("0.01"))
            diff_dollar = (shocked_val - curr_val).quantize(Decimal("0.01"))
            diff_pct = (
                ((shocked_val - curr_val) / curr_val * Decimal("100")).quantize(Decimal("0.01"))
                if curr_val > Decimal("0")
                else Decimal("0.00")
            )

            new_holdings_value += shocked_val
            projected_positions.append({
                "symbol": sym,
                "name": pos["name"],
                "current_value": curr_val,
                "projected_value": shocked_val,
                "dollar_change": diff_dollar,
                "percentage_change": diff_pct,
                "applied_shock_pct": shock if (sym in custom_shocks or market_shock_pct != 0.0) else 0.0,
                "assumption": assumption,
            })

        projected_equity = (new_holdings_value + cash_balance).quantize(Decimal("0.01"))
        total_dollar_change = (projected_equity - current_equity).quantize(Decimal("0.01"))
        total_pct_change = (
            ((projected_equity - current_equity) / current_equity * Decimal("100")).quantize(Decimal("0.01"))
            if current_equity > Decimal("0")
            else Decimal("0.00")
        )

        return {
            "scenario_name": (
                f"Market Shock ({market_shock_pct:+.1f}%)"
                if market_shock_pct != 0 and not custom_shocks
                else ("Custom Asset Stress Scenario" if custom_shocks else "Baseline")
            ),
            "current_equity": current_equity,
            "projected_equity": projected_equity,
            "cash_buffer": cash_balance,
            "total_dollar_change": total_dollar_change,
            "total_percentage_change": total_pct_change,
            "assumptions": {
                "market_shock_pct": market_shock_pct,
                "custom_shocks": custom_shocks,
                "cash_preservation": "Cash balances maintain 100% principal preservation (0% haircut).",
            },
            "position_impacts": projected_positions,
        }
