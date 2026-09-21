"""Historical Value at Risk (VaR) calculation."""
from decimal import Decimal
from typing import Any

import numpy as np


def calculate_historical_var(
    returns: list[float],
    portfolio_value: Decimal,
    confidence_levels: list[float] = [0.95, 0.99],
) -> dict[str, Any]:
    """
    Computes non-parametric Historical Value at Risk (VaR):
    Sorts empirical returns and takes the (1 - confidence_level) quantile.
    VaR ($) = -quantile * portfolio_value
    """
    if not returns or len(returns) < 10 or portfolio_value <= Decimal(0):
        return {
            "var_95_dollar": Decimal("0.00"),
            "var_95_pct": Decimal("0.00"),
            "var_99_dollar": Decimal("0.00"),
            "var_99_pct": Decimal("0.00"),
            "methodology": "Historical Simulation (Empirical Quantile)",
            "sample_size": len(returns),
        }

    ret_arr = np.array(returns, dtype=np.float64)
    results = {
        "methodology": "Historical Simulation (Empirical Quantile)",
        "sample_size": len(returns),
    }

    port_val_float = float(portfolio_value)

    for conf in confidence_levels:
        alpha = (1.0 - conf) * 100.0
        cutoff_ret = float(np.percentile(ret_arr, alpha))
        loss_pct = max(0.0, -cutoff_ret)
        loss_dollar = loss_pct * port_val_float

        tag = str(int(conf * 100))
        results[f"var_{tag}_pct"] = Decimal(str(round(loss_pct * 100.0, 2)))
        results[f"var_{tag}_dollar"] = Decimal(str(round(loss_dollar, 2)))

    return results
