"""Black-Scholes analytical options pricing model."""
import math

from scipy.stats import norm


def calculate_black_scholes_price(
    spot: float,
    strike: float,
    time_to_expiry_years: float,
    volatility: float = 0.22,  # 22% annualized implied volatility baseline
    risk_free_rate: float = 0.065,  # 6.5% risk-free rate
    is_call: bool = True,
) -> float:
    """
    Computes theoretical European option price via Black-Scholes-Merton formula.
    """
    if spot <= 0 or strike <= 0:
        return 0.0

    if time_to_expiry_years <= 0.0001:
        # At expiration intrinsic value
        return max(0.0, spot - strike) if is_call else max(0.0, strike - spot)

    sigma = max(0.01, volatility)
    t = time_to_expiry_years
    r = risk_free_rate

    d1 = (math.log(spot / strike) + (r + 0.5 * sigma ** 2) * t) / (sigma * math.sqrt(t))
    d2 = d1 - sigma * math.sqrt(t)

    if is_call:
        price = spot * norm.cdf(d1) - strike * math.exp(-r * t) * norm.cdf(d2)
    else:
        price = strike * math.exp(-r * t) * norm.cdf(-d2) - spot * norm.cdf(-d1)

    return max(0.0, price)
