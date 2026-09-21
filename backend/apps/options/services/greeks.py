"""Analytical options Greeks calculation module."""
import math
from decimal import Decimal

from scipy.stats import norm


def calculate_options_greeks(
    spot: float,
    strike: float,
    time_to_expiry_years: float,
    volatility: float = 0.22,
    risk_free_rate: float = 0.065,
    is_call: bool = True,
) -> dict[str, Decimal]:
    """
    Computes analytical first- and second-order Greeks:
    - Delta (Δ): Price sensitivity w.r.t underlying spot
    - Gamma (Γ): Delta sensitivity w.r.t underlying spot
    - Theta (Θ): 1-day time decay (expressed in currency/day per share)
    - Vega (ν): Price sensitivity per 1% change in implied volatility
    - Rho (ρ): Price sensitivity per 1% change in risk-free interest rate
    """
    if spot <= 0 or strike <= 0 or time_to_expiry_years <= 0.0001:
        delta = 1.0 if (is_call and spot > strike) else (-1.0 if (not is_call and spot < strike) else 0.0)
        return {
            "delta": Decimal(str(round(delta, 4))),
            "gamma": Decimal("0.0000"),
            "theta": Decimal("0.0000"),
            "vega": Decimal("0.0000"),
            "rho": Decimal("0.0000"),
        }

    sigma = max(0.01, volatility)
    t = time_to_expiry_years
    r = risk_free_rate
    sqrt_t = math.sqrt(t)

    d1 = (math.log(spot / strike) + (r + 0.5 * sigma ** 2) * t) / (sigma * sqrt_t)
    d2 = d1 - sigma * sqrt_t

    phi_d1 = norm.pdf(d1)  # standard normal probability density

    # 1. Delta
    delta = norm.cdf(d1) if is_call else (norm.cdf(d1) - 1.0)

    # 2. Gamma (identical for Call and Put)
    gamma = phi_d1 / (spot * sigma * sqrt_t)

    # 3. Theta (daily decay = annual theta / 365)
    term1 = -(spot * phi_d1 * sigma) / (2.0 * sqrt_t)
    if is_call:
        term2 = -r * strike * math.exp(-r * t) * norm.cdf(d2)
        annual_theta = term1 + term2
    else:
        term2 = r * strike * math.exp(-r * t) * norm.cdf(-d2)
        annual_theta = term1 + term2
    daily_theta = annual_theta / 365.0

    # 4. Vega (per 1% shift in volatility)
    vega = (spot * sqrt_t * phi_d1) / 100.0

    # 5. Rho (per 1% shift in interest rate)
    if is_call:
        rho = (strike * t * math.exp(-r * t) * norm.cdf(d2)) / 100.0
    else:
        rho = (-strike * t * math.exp(-r * t) * norm.cdf(-d2)) / 100.0

    return {
        "delta": Decimal(str(round(delta, 4))),
        "gamma": Decimal(str(round(gamma, 6))),
        "theta": Decimal(str(round(daily_theta, 4))),
        "vega": Decimal(str(round(vega, 4))),
        "rho": Decimal(str(round(rho, 4))),
    }
