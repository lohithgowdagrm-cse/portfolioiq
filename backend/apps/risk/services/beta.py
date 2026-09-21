"""Portfolio Beta calculation against market benchmark."""
import numpy as np
from typing import List
from decimal import Decimal


def calculate_portfolio_beta(portfolio_returns: List[float], benchmark_returns: List[float]) -> Decimal:
    """
    Computes Beta against benchmark:
    Beta = Cov(R_p, R_b) / Var(R_b)
    """
    min_len = min(len(portfolio_returns), len(benchmark_returns))
    if min_len < 10:
        return Decimal("1.0000")

    p_rets = np.array(portfolio_returns[:min_len], dtype=np.float64)
    b_rets = np.array(benchmark_returns[:min_len], dtype=np.float64)

    b_var = np.var(b_rets, ddof=1)
    if b_var == 0:
        return Decimal("1.0000")

    cov_matrix = np.cov(p_rets, b_rets, ddof=1)
    covariance = cov_matrix[0, 1]
    beta = covariance / b_var

    return Decimal(str(round(beta, 4)))
