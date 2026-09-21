"""Portfolio concentration and diversification metrics."""
from typing import List, Dict, Any
from decimal import Decimal


def calculate_concentration_metrics(positions: List[Dict[str, Any]], total_equity: Decimal) -> Dict[str, Any]:
    """
    Computes single-position, sector, and asset class concentration alongside
    the Herfindahl-Hirschman Index (HHI) for portfolio diversification assessment.
    """
    if not positions or total_equity <= Decimal("0"):
        return {
            "herfindahl_index": Decimal("0.0000"),
            "top_position_symbol": "N/A",
            "top_position_weight_pct": Decimal("0.00"),
            "top_3_concentration_pct": Decimal("0.00"),
            "top_5_concentration_pct": Decimal("0.00"),
            "sector_weights": {},
            "asset_class_weights": {},
        }

    total_eq_float = float(total_equity)
    hhi = 0.0
    sector_exposure: Dict[str, float] = {}
    asset_exposure: Dict[str, float] = {}
    weights: List[float] = []

    for pos in positions:
        curr_val = float(pos.get("current_value", 0))
        weight = curr_val / total_eq_float if total_eq_float > 0 else 0.0
        weights.append(weight)
        hhi += (weight ** 2)

        sec = pos.get("sector") or "Unassigned"
        sector_exposure[sec] = sector_exposure.get(sec, 0.0) + (weight * 100.0)

        a_class = pos.get("asset_class") or "EQUITY"
        asset_exposure[a_class] = asset_exposure.get(a_class, 0.0) + (weight * 100.0)

    weights.sort(reverse=True)
    top_pos_weight = (weights[0] * 100.0) if weights else 0.0
    top_3_conc = sum(weights[:3]) * 100.0
    top_5_conc = sum(weights[:5]) * 100.0

    return {
        "herfindahl_index": Decimal(str(round(hhi, 4))),
        "top_position_weight_pct": Decimal(str(round(top_pos_weight, 2))),
        "top_3_concentration_pct": Decimal(str(round(top_3_conc, 2))),
        "top_5_concentration_pct": Decimal(str(round(top_5_conc, 2))),
        "sector_weights": {k: round(v, 2) for k, v in sector_exposure.items()},
        "asset_class_weights": {k: round(v, 2) for k, v in asset_exposure.items()},
    }
