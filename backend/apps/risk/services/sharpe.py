"""Sharpe ratio calculation with configurable risk-free benchmark."""
import numpy as np
from typing import List
from decimal import Decimal


def calculate_sharpe_ratio(
    returns: List[float],
    annual_risk_free_rate: float = 0.065,  # 6.5% standard Indian sovereign 91-day T-bill baseline
    periods_per_year: int = 252,
) -> Decimal:
    """
    Computes annualized Sharpe ratio:
    Sharpe = (Annualized Return - Risk Free Rate) / Annualized Volatility
    """
    if not returns or len(returns) < 5:
        return Decimal("0.0000")

    ret_arr = np.array(returns, dtype=np.float64)
    daily_mean = float(np.mean(ret_arr))
    daily_std = float(np.std(ret_arr, ddof=1))

    if daily_std == 0:
        return Decimal("0.0000")

    daily_rf = annual_risk_free_rate / periods_per_year
    excess_daily_mean = daily_mean - daily_rf
    sharpe = (excess_daily_mean / daily_std) * np.sqrt(periods_per_year)

    return Decimal(str(round(sharpe, 4)))
