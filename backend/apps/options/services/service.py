"""Options service orchestrating contract evaluation, Greeks aggregation, and expiration exposure."""
import logging
from typing import Dict, Any, List
from decimal import Decimal
from datetime import date
from django.utils import timezone
from apps.options.models import OptionContract
from apps.portfolios.models import Portfolio, Position
from apps.market_data.models import MarketPrice
from apps.market_data.providers.mock_provider import BASE_EQUITY_PRICES
from .pricing import calculate_black_scholes_price
from .greeks import calculate_options_greeks

logger = logging.getLogger(__name__)


class OptionsService:
    @classmethod
    def get_spot_price(cls, underlying) -> Decimal:
        latest = MarketPrice.objects.filter(instrument=underlying).order_by("-price_timestamp").first()
        if latest:
            return latest.price
        return BASE_EQUITY_PRICES.get(underlying.symbol, Decimal("1000.00"))

    @classmethod
    def evaluate_contract(cls, contract: OptionContract) -> Dict[str, Any]:
        """
        Computes analytical pricing, market metrics, and Greeks for a single OptionContract.
        """
        today = timezone.now().date()
        days_to_expiry = max(0, (contract.expiration_date - today).days)
        time_to_expiry_years = max(0.0001, days_to_expiry / 365.25)

        spot = float(cls.get_spot_price(contract.underlying))
        strike = float(contract.strike_price)
        is_call = contract.option_type == "CALL"

        # Theoretical price via Black-Scholes
        volatility = 0.24  # 24% baseline IV
        risk_free = 0.065
        theo_price = calculate_black_scholes_price(
            spot=spot,
            strike=strike,
            time_to_expiry_years=time_to_expiry_years,
            volatility=volatility,
            risk_free_rate=risk_free,
            is_call=is_call,
        )

        # Analytical Greeks
        greeks = calculate_options_greeks(
            spot=spot,
            strike=strike,
            time_to_expiry_years=time_to_expiry_years,
            volatility=volatility,
            risk_free_rate=risk_free,
            is_call=is_call,
        )

        # Moneyness & Intrinsic/Extrinsic Value
        if is_call:
            intrinsic = max(0.0, spot - strike)
            moneyness = "ITM" if spot > strike else ("ATM" if abs(spot - strike) / strike < 0.015 else "OTM")
        else:
            intrinsic = max(0.0, strike - spot)
            moneyness = "ITM" if strike > spot else ("ATM" if abs(spot - strike) / strike < 0.015 else "OTM")
        extrinsic = max(0.0, theo_price - intrinsic)

        return {
            "contract_id": str(contract.id),
            "symbol": contract.underlying.symbol,
            "underlying_name": contract.underlying.name,
            "option_type": contract.option_type,
            "strike_price": contract.strike_price,
            "expiration_date": contract.expiration_date.isoformat(),
            "days_to_expiry": days_to_expiry,
            "contract_multiplier": contract.contract_multiplier,
            "spot_price": Decimal(str(round(spot, 2))),
            "theoretical_price": Decimal(str(round(theo_price, 2))),
            "intrinsic_value": Decimal(str(round(intrinsic, 2))),
            "extrinsic_value": Decimal(str(round(extrinsic, 2))),
            "moneyness": moneyness,
            "implied_volatility_pct": Decimal(str(round(volatility * 100.0, 2))),
            "greeks": greeks,
        }

    @classmethod
    def get_portfolio_options_breakdown(cls, portfolio: Portfolio) -> Dict[str, Any]:
        """
        Evaluates all option positions in portfolio, aggregates portfolio-level Greeks,
        and computes expiration exposure buckets.
        """
        option_positions = Position.objects.filter(
            portfolio=portfolio,
            option_contract__isnull=False,
            quantity__gt=Decimal("0.0000"),
        ).select_related("option_contract", "option_contract__underlying")

        positions_list: List[Dict[str, Any]] = []
        total_delta = Decimal("0.0000")
        total_gamma = Decimal("0.0000")
        total_theta = Decimal("0.0000")
        total_vega = Decimal("0.0000")
        total_market_value = Decimal("0.0000")

        exp_near = 0  # < 7 days
        exp_medium = 0  # 7-30 days
        exp_far = 0  # > 30 days

        for pos in option_positions:
            eval_data = cls.evaluate_contract(pos.option_contract)
            qty = pos.quantity
            mult = Decimal(str(pos.option_contract.contract_multiplier))
            shares_equivalent = qty * mult

            # Theoretical value of this position
            pos_theo_val = eval_data["theoretical_price"] * shares_equivalent
            total_market_value += pos_theo_val

            # Scaled Greeks: Greek * Quantity * Multiplier
            pos_delta = eval_data["greeks"]["delta"] * shares_equivalent
            pos_gamma = eval_data["greeks"]["gamma"] * shares_equivalent
            pos_theta = eval_data["greeks"]["theta"] * shares_equivalent
            pos_vega = eval_data["greeks"]["vega"] * shares_equivalent

            total_delta += pos_delta
            total_gamma += pos_gamma
            total_theta += pos_theta
            total_vega += pos_vega

            # Expiration bucketing
            dte = eval_data["days_to_expiry"]
            if dte <= 7:
                exp_near += 1
            elif dte <= 30:
                exp_medium += 1
            else:
                exp_far += 1

            positions_list.append({
                "position_id": str(pos.id),
                "contract": eval_data,
                "quantity": pos.quantity,
                "average_price": pos.average_buy_price,
                "total_invested": pos.total_invested,
                "market_value": pos_theo_val.quantize(Decimal("0.01")),
                "unrealized_pnl": (pos_theo_val - pos.total_invested).quantize(Decimal("0.01")),
                "position_delta": pos_delta.quantize(Decimal("0.01")),
                "position_gamma": pos_gamma.quantize(Decimal("0.0001")),
                "position_theta": pos_theta.quantize(Decimal("0.01")),
                "position_vega": pos_vega.quantize(Decimal("0.01")),
            })

        return {
            "portfolio_id": str(portfolio.id),
            "portfolio_name": portfolio.name,
            "open_options_count": len(positions_list),
            "aggregate_greeks": {
                "portfolio_delta": total_delta.quantize(Decimal("0.01")),
                "portfolio_gamma": total_gamma.quantize(Decimal("0.0001")),
                "portfolio_theta": total_theta.quantize(Decimal("0.01")),
                "portfolio_vega": total_vega.quantize(Decimal("0.01")),
                "total_options_market_value": total_market_value.quantize(Decimal("0.01")),
            },
            "expiration_exposure": {
                "expiring_within_7_days": exp_near,
                "expiring_8_to_30_days": exp_medium,
                "expiring_beyond_30_days": exp_far,
            },
            "positions": positions_list,
        }
