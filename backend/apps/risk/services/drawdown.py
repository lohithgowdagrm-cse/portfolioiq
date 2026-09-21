"""Maximum Drawdown and underwater curve calculation."""
from decimal import Decimal
from typing import Any


def calculate_maximum_drawdown(equity_series: list[float]) -> dict[str, Any]:
    """
    Computes maximum peak-to-trough decline over an equity curve:
    Drawdown_t = (Peak_t - Value_t) / Peak_t
    MaxDrawdown = max(Drawdown_t)
    """
    if not equity_series or len(equity_series) < 2:
        return {
            "max_drawdown_pct": Decimal("0.0000"),
            "peak_value": Decimal("0.0000"),
            "trough_value": Decimal("0.0000"),
            "drawdown_series": [],
        }

    peak = equity_series[0]
    max_dd = 0.0
    peak_at_max = peak
    trough_at_max = peak
    dd_series = []

    for val in equity_series:
        peak = max(peak, val)
        dd = (peak - val) / peak if peak > 0 else 0.0
        dd_series.append(round(dd * 100.0, 2))
        if dd > max_dd:
            max_dd = dd
            peak_at_max = peak
            trough_at_max = val

    return {
        "max_drawdown_pct": Decimal(str(round(max_dd * 100.0, 4))),
        "peak_value": Decimal(str(round(peak_at_max, 2))),
        "trough_value": Decimal(str(round(trough_at_max, 2))),
        "drawdown_series": dd_series,
    }
