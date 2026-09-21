"""Annualized historical volatility calculation."""
import numpy as np
from typing import List
from decimal import Decimal


def calculate_annualized_volatility(returns: List[float], periods_per_year: int = 252) -> Decimal:
    """
    Computes annualized historical volatility from a series of daily returns:
    sigma_annualized = std(returns, ddof=1) * sqrt(periods_per_year) * 100
    Assumptions: 252 trading days per year, stationary daily return distribution.
    """
    if not returns or len(returns) < 2:
        return Decimal("0.0000")

    ret_arr = np.array(returns, dtype=np.float64)
    daily_std = float(np.std(ret_arr, ddof=1))
    ann_vol = daily_std * np.sqrt(periods_per_year) * 100.0
    return Decimal(str(round(ann_vol, 4)))
