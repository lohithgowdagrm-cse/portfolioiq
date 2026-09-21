"""Risk engine and Options Greeks mathematical tests."""
import math
from decimal import Decimal

from apps.options.services.greeks import calculate_options_greeks
from apps.options.services.pricing import calculate_black_scholes_price
from apps.risk.services.beta import calculate_portfolio_beta
from apps.risk.services.concentration import calculate_concentration_metrics
from apps.risk.services.drawdown import calculate_maximum_drawdown
from apps.risk.services.sharpe import calculate_sharpe_ratio
from apps.risk.services.var import calculate_historical_var
from apps.risk.services.volatility import calculate_annualized_volatility


def test_annualized_volatility():
    # 0.01 daily std dev * sqrt(252) * 100 ~= 15.8745%
    returns = [0.01, -0.01, 0.01, -0.01, 0.01, -0.01, 0.01, -0.01]
    vol = calculate_annualized_volatility(returns)
    assert vol > Decimal("10.0000")
    assert vol < Decimal("25.0000")


def test_sharpe_ratio():
    # Positive excess return yields positive Sharpe
    returns = [0.005, 0.003, 0.004, 0.006, 0.002, 0.008, 0.001, 0.005, 0.003, 0.004]
    sharpe = calculate_sharpe_ratio(returns, annual_risk_free_rate=0.065)
    assert sharpe > Decimal("0.0000")


def test_portfolio_beta():
    # Perfectly correlated series with identical volatility yields Beta ~ 1.0
    bench = [0.01, -0.02, 0.015, -0.01, 0.02, -0.005, 0.012, -0.018, 0.022, -0.015]
    port = [0.01, -0.02, 0.015, -0.01, 0.02, -0.005, 0.012, -0.018, 0.022, -0.015]
    beta = calculate_portfolio_beta(port, bench)
    assert abs(float(beta) - 1.0) < 0.001

    # Portfolio with double the volatility/returns has Beta ~ 2.0
    port_double = [2.0 * x for x in bench]
    beta_double = calculate_portfolio_beta(port_double, bench)
    assert abs(float(beta_double) - 2.0) < 0.001


def test_maximum_drawdown():
    # Peak is 100, drops to 80 (20% drawdown), recovers to 110, drops to 99 (10% drawdown)
    curve = [100.0, 95.0, 90.0, 80.0, 85.0, 105.0, 110.0, 99.0]
    dd = calculate_maximum_drawdown(curve)
    assert dd["max_drawdown_pct"] == Decimal("20.0000")
    assert dd["peak_value"] == Decimal("100.00")
    assert dd["trough_value"] == Decimal("80.00")


def test_historical_var():
    returns = [-0.04, -0.03, -0.02, -0.01, 0.00, 0.01, 0.02, 0.03, 0.04, 0.05] * 10
    port_val = Decimal("1000000.00")
    var = calculate_historical_var(returns, port_val)
    assert var["var_95_dollar"] > Decimal("0.00")
    assert var["var_99_dollar"] >= var["var_95_dollar"]


def test_concentration_and_herfindahl():
    positions = [
        {"symbol": "TCS", "current_value": Decimal("500000.00"), "sector": "IT", "asset_class": "EQUITY"},
        {"symbol": "INFY", "current_value": Decimal("300000.00"), "sector": "IT", "asset_class": "EQUITY"},
        {"symbol": "RELIANCE", "current_value": Decimal("200000.00"), "sector": "Energy", "asset_class": "EQUITY"},
    ]
    total_eq = Decimal("1000000.00")
    conc = calculate_concentration_metrics(positions, total_eq)
    # Weights: 0.5, 0.3, 0.2 -> HHI = 0.25 + 0.09 + 0.04 = 0.38
    assert conc["herfindahl_index"] == Decimal("0.3800")
    assert conc["top_position_weight_pct"] == Decimal("50.00")
    assert conc["sector_weights"]["IT"] == 80.0


def test_black_scholes_pricing_and_parity():
    spot = 100.0
    strike = 100.0
    t = 1.0
    r = 0.05
    vol = 0.20

    call_price = calculate_black_scholes_price(spot, strike, t, vol, r, is_call=True)
    put_price = calculate_black_scholes_price(spot, strike, t, vol, r, is_call=False)

    # Call and Put should be strictly positive for ATM with 1 yr expiry
    assert call_price > 0.0
    assert put_price > 0.0

    # Put-Call Parity: C - P = S - K * exp(-r*T)
    lhs = call_price - put_price
    rhs = spot - strike * math.exp(-r * t)
    assert abs(lhs - rhs) < 0.001


def test_options_greeks():
    spot = 4000.0
    strike = 4000.0
    t = 30.0 / 365.25  # ~1 month
    r = 0.065
    vol = 0.22

    call_greeks = calculate_options_greeks(spot, strike, t, vol, r, is_call=True)
    put_greeks = calculate_options_greeks(spot, strike, t, vol, r, is_call=False)

    # ATM Call Delta ~ 0.5, ATM Put Delta ~ -0.5
    assert Decimal("0.45") <= call_greeks["delta"] <= Decimal("0.60")
    assert Decimal("-0.55") <= put_greeks["delta"] <= Decimal("-0.40")

    # Gamma is identical for Call and Put, strictly positive
    assert call_greeks["gamma"] > Decimal("0.0000")
    assert call_greeks["gamma"] == put_greeks["gamma"]

    # Vega is strictly positive (increases with volatility)
    assert call_greeks["vega"] > Decimal("0.0000")

    # Theta is negative (option loses value as time elapses)
    assert call_greeks["theta"] < Decimal("0.0000")
