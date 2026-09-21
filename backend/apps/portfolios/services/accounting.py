"""Portfolio accounting and calculation services."""
import logging
from decimal import Decimal
from typing import Dict, Any, List, Optional
from django.db import transaction
from django.utils import timezone
from common.exceptions.base import (
    InsufficientPositionException,
    FinancialValidationException,
    InvalidPriceException,
)
from common.utilities.constants import TransactionType
from apps.portfolios.models import Portfolio, Position, PortfolioSnapshot
from apps.transactions.models import Transaction
from apps.market_data.models import MarketPrice

logger = logging.getLogger(__name__)


class PortfolioCalculationService:
    """
    Deterministic domain service for portfolio accounting, position cost-basis reconciliation,
    realized/unrealized P&L calculations, and snapshot aggregation.
    """

    @staticmethod
    def get_latest_market_price(instrument) -> Optional[MarketPrice]:
        """Fetches the latest recorded market price for an instrument."""
        return MarketPrice.objects.filter(instrument=instrument).order_by("-price_timestamp").first()

    @classmethod
    def apply_transaction_to_position(
        cls,
        portfolio: Portfolio,
        instrument,
        tx_type: str,
        quantity: Decimal,
        price: Decimal,
        fees: Decimal = Decimal("0.0000"),
        taxes: Decimal = Decimal("0.0000"),
        option_contract=None,
    ) -> Position:
        """
        Applies a single transaction to update or create a Position record.
        Maintains weighted average cost, realized P&L, and invested capital.
        """
        if quantity <= Decimal("0"):
            raise FinancialValidationException(
                message="Transaction quantity must be strictly greater than zero.",
                code="INVALID_QUANTITY"
            )
        if price < Decimal("0"):
            raise InvalidPriceException("Transaction price cannot be negative.")

        position, _ = Position.objects.get_or_create(
            portfolio=portfolio,
            instrument=instrument,
            option_contract=option_contract,
            defaults={
                "quantity": Decimal("0.0000"),
                "average_buy_price": Decimal("0.0000"),
                "total_invested": Decimal("0.0000"),
                "realized_pnl": Decimal("0.0000"),
            },
        )

        prior_qty = position.quantity
        prior_avg = position.average_buy_price
        prior_invested = position.total_invested
        prior_realized = position.realized_pnl

        if tx_type in (TransactionType.BUY, TransactionType.BONUS):
            # For BUY:
            # New total quantity = prior_qty + quantity
            # Total capital allocated = (prior_qty * prior_avg) + (quantity * price) + fees + taxes
            new_qty = prior_qty + quantity
            if tx_type == TransactionType.BONUS:
                # Bonus shares: price is 0, only fees/taxes if any
                cost_addition = fees + taxes
            else:
                cost_addition = (quantity * price) + fees + taxes

            new_invested = prior_invested + cost_addition
            new_avg = (new_invested / new_qty) if new_qty > Decimal("0") else Decimal("0.0000")

            position.quantity = new_qty
            position.average_buy_price = new_avg.quantize(Decimal("0.0001"))
            position.total_invested = new_invested.quantize(Decimal("0.0001"))

        elif tx_type == TransactionType.SELL:
            if quantity > prior_qty:
                raise InsufficientPositionException(
                    message=f"Cannot sell {quantity} shares of {instrument.symbol}. Available position is only {prior_qty}.",
                    code="INSUFFICIENT_POSITION"
                )

            # Gross proceeds minus transaction costs
            gross_proceeds = quantity * price
            net_proceeds = gross_proceeds - fees - taxes
            cost_of_sold_shares = quantity * prior_avg

            # Realized P&L on this sale
            trade_realized_pnl = net_proceeds - cost_of_sold_shares
            new_qty = prior_qty - quantity

            if new_qty == Decimal("0"):
                # Entire position closed
                new_invested = Decimal("0.0000")
                new_avg = Decimal("0.0000")
            else:
                new_invested = (prior_invested - cost_of_sold_shares).quantize(Decimal("0.0001"))
                new_avg = prior_avg  # Average cost per remaining share remains constant on sell

            position.quantity = new_qty
            position.average_buy_price = new_avg.quantize(Decimal("0.0001"))
            position.total_invested = max(Decimal("0.0000"), new_invested)
            position.realized_pnl = (prior_realized + trade_realized_pnl).quantize(Decimal("0.0001"))

        elif tx_type == TransactionType.SPLIT:
            # Stock split (e.g. 2-for-1 or 1-for-2): price is the split factor (new_shares / old_shares)
            # If price=2.0, 100 shares become 200, average cost halves.
            if price <= Decimal("0"):
                raise FinancialValidationException("Split factor must be strictly greater than zero.")
            new_qty = prior_qty * price
            new_avg = prior_avg / price if price > Decimal("0") else prior_avg
            position.quantity = new_qty.quantize(Decimal("0.0001"))
            position.average_buy_price = new_avg.quantize(Decimal("0.0001"))

        elif tx_type == TransactionType.DIVIDEND:
            # Dividend: credited directly as realized gain or cash balance
            net_div = (quantity * price) - taxes
            position.realized_pnl = (prior_realized + net_div).quantize(Decimal("0.0001"))

        position.save()
        return position

    @classmethod
    def recalculate_portfolio_from_ledger(cls, portfolio: Portfolio) -> Dict[str, Any]:
        """
        Deterministic full reconciliation: wipes temporary position balances and replays
        the entire chronological transaction ledger to guarantee 100% mathematical consistency.
        """
        with transaction.atomic():
            # Reset all positions in portfolio
            Position.objects.filter(portfolio=portfolio).update(
                quantity=Decimal("0.0000"),
                average_buy_price=Decimal("0.0000"),
                total_invested=Decimal("0.0000"),
                realized_pnl=Decimal("0.0000"),
            )

            # Replay all transactions chronologically
            txs = Transaction.objects.filter(portfolio=portfolio).order_by("executed_at", "created_at")
            for tx in txs:
                cls.apply_transaction_to_position(
                    portfolio=portfolio,
                    instrument=tx.instrument,
                    tx_type=tx.transaction_type,
                    quantity=tx.quantity,
                    price=tx.price,
                    fees=tx.fees,
                    taxes=tx.taxes,
                    option_contract=tx.option_contract,
                )

            # Clean up zero-quantity positions where realized P&L is 0
            Position.objects.filter(
                portfolio=portfolio,
                quantity=Decimal("0.0000"),
                realized_pnl=Decimal("0.0000"),
            ).delete()

            return cls.calculate_portfolio_summary(portfolio)

    @classmethod
    def calculate_portfolio_summary(cls, portfolio: Portfolio) -> Dict[str, Any]:
        """
        Computes real-time portfolio aggregate metrics:
        - Invested Capital
        - Current Market Value (Holdings + Cash)
        - Unrealized P&L & Return %
        - Realized P&L
        - Today's P&L & Return %
        - Holdings with computed weights, day P&L, and returns
        """
        positions = Position.objects.filter(
            portfolio=portfolio,
            quantity__gt=Decimal("0.0000")
        ).select_related("instrument", "instrument__sector", "option_contract")

        total_invested = Decimal("0.0000")
        current_holdings_value = Decimal("0.0000")
        total_day_pnl = Decimal("0.0000")
        total_realized_pnl = Decimal("0.0000")

        # Also sum realized P&L from closed positions
        all_positions = Position.objects.filter(portfolio=portfolio)
        for pos in all_positions:
            total_realized_pnl += pos.realized_pnl

        position_details: List[Dict[str, Any]] = []

        for pos in positions:
            if pos.option_contract:
                from apps.options.services.service import OptionsService
                opt_data = OptionsService.evaluate_contract(pos.option_contract)
                ltp = Decimal(str(opt_data["theoretical_price"])).quantize(Decimal("0.0001"))
                prev_close = ltp
                mult = Decimal(str(pos.option_contract.contract_multiplier))
                market_val = (pos.quantity * ltp * mult).quantize(Decimal("0.0001"))
            else:
                latest_quote = cls.get_latest_market_price(pos.instrument)
                ltp = latest_quote.price if latest_quote else pos.average_buy_price
                prev_close = latest_quote.previous_close if latest_quote else ltp
                market_val = pos.quantity * ltp

            unrealized_pnl = market_val - pos.total_invested
            unrealized_pct = (
                (unrealized_pnl / pos.total_invested * Decimal("100"))
                if pos.total_invested > Decimal("0")
                else Decimal("0.0000")
            )

            # Day P&L for this position
            day_pnl = (ltp - prev_close) * pos.quantity
            day_pct = (
                ((ltp - prev_close) / prev_close * Decimal("100"))
                if prev_close > Decimal("0")
                else Decimal("0.0000")
            )

            total_invested += pos.total_invested
            current_holdings_value += market_val
            total_day_pnl += day_pnl

            position_details.append({
                "id": str(pos.id),
                "instrument_id": str(pos.instrument.id),
                "symbol": pos.instrument.symbol,
                "name": pos.instrument.name,
                "asset_class": pos.instrument.asset_class,
                "sector": pos.instrument.sector.name if pos.instrument.sector else "Unassigned",
                "quantity": pos.quantity,
                "average_buy_price": pos.average_buy_price,
                "ltp": ltp,
                "prev_close": prev_close,
                "invested_capital": pos.total_invested,
                "current_value": market_val.quantize(Decimal("0.0001")),
                "day_pnl": day_pnl.quantize(Decimal("0.0001")),
                "day_change_pct": day_pct.quantize(Decimal("0.01")),
                "unrealized_pnl": unrealized_pnl.quantize(Decimal("0.0001")),
                "total_return_pct": unrealized_pct.quantize(Decimal("0.01")),
                "realized_pnl": pos.realized_pnl,
                "weight_pct": Decimal("0.0000"),  # calculated below
            })

        cash = portfolio.cash_balance
        total_equity = current_holdings_value + cash
        total_unrealized_pnl = current_holdings_value - total_invested
        total_pnl = total_unrealized_pnl + total_realized_pnl
        total_return_pct = (
            (total_unrealized_pnl / total_invested * Decimal("100"))
            if total_invested > Decimal("0")
            else Decimal("0.0000")
        )

        # Baseline equity yesterday for day return %
        prev_equity = total_equity - total_day_pnl
        day_return_pct = (
            (total_day_pnl / prev_equity * Decimal("100"))
            if prev_equity > Decimal("0")
            else Decimal("0.0000")
        )

        # Calculate position weights
        for p in position_details:
            if total_equity > Decimal("0"):
                p["weight_pct"] = (
                    (p["current_value"] / total_equity * Decimal("100")).quantize(Decimal("0.01"))
                )

        return {
            "portfolio_id": str(portfolio.id),
            "portfolio_name": portfolio.name,
            "currency": portfolio.base_currency,
            "total_equity": total_equity.quantize(Decimal("0.01")),
            "cash_balance": cash.quantize(Decimal("0.01")),
            "holdings_value": current_holdings_value.quantize(Decimal("0.01")),
            "invested_capital": total_invested.quantize(Decimal("0.01")),
            "unrealized_pnl": total_unrealized_pnl.quantize(Decimal("0.01")),
            "realized_pnl": total_realized_pnl.quantize(Decimal("0.01")),
            "total_pnl": total_pnl.quantize(Decimal("0.01")),
            "total_return_pct": total_return_pct.quantize(Decimal("0.01")),
            "day_pnl": total_day_pnl.quantize(Decimal("0.01")),
            "day_return_pct": day_return_pct.quantize(Decimal("0.01")),
            "positions_count": len(position_details),
            "positions": position_details,
        }

    @classmethod
    def record_daily_snapshot(cls, portfolio: Portfolio, date=None) -> PortfolioSnapshot:
        """
        Creates or updates a daily historical snapshot for performance charting.
        """
        if date is None:
            date = timezone.now().date()

        summary = cls.calculate_portfolio_summary(portfolio)
        snapshot, _ = PortfolioSnapshot.objects.update_or_create(
            portfolio=portfolio,
            snapshot_date=date,
            defaults={
                "total_equity": summary["total_equity"],
                "cash_balance": summary["cash_balance"],
                "invested_capital": summary["invested_capital"],
                "unrealized_pnl": summary["unrealized_pnl"],
                "realized_pnl": summary["realized_pnl"],
                "day_pnl": summary["day_pnl"],
                "day_return_pct": summary["day_return_pct"],
            },
        )
        return snapshot
