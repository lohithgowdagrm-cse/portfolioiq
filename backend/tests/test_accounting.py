"""Accounting engine unit and integration tests."""
from decimal import Decimal

import pytest
from apps.accounts.models import User
from apps.instruments.models import Instrument, Sector
from apps.market_data.models import MarketPrice
from apps.portfolios.models import Portfolio, Position
from apps.portfolios.services.accounting import PortfolioCalculationService
from apps.transactions.services.transaction_service import TransactionService
from common.exceptions.base import (
    InsufficientPositionException,
)
from django.utils import timezone


@pytest.mark.django_db
class TestPortfolioAccountingEngine:
    @pytest.fixture(autouse=True)
    def setup_entities(self):
        self.user = User.objects.create_user(
            email="trader@portfolioiq.io",
            password="TestPassword123!",
            first_name="Alpha",
            last_name="Trader",
        )
        self.tech_sector = Sector.objects.create(name="Information Technology", code="IT")
        self.tcs = Instrument.objects.create(
            symbol="TCS",
            name="Tata Consultancy Services Ltd.",
            sector=self.tech_sector,
            exchange="NSE",
            currency="INR",
        )
        self.infy = Instrument.objects.create(
            symbol="INFY",
            name="Infosys Ltd.",
            sector=self.tech_sector,
            exchange="NSE",
            currency="INR",
        )
        self.portfolio = Portfolio.objects.create(
            user=self.user,
            name="Core Tech Portfolio",
            cash_balance=Decimal("1000000.0000"),
            base_currency="INR",
        )

    def test_single_buy_creates_position(self):
        tx = TransactionService.record_transaction(
            portfolio=self.portfolio,
            instrument=self.tcs,
            tx_type="BUY",
            quantity=Decimal("10.0000"),
            price=Decimal("4000.0000"),
            fees=Decimal("20.0000"),
            taxes=Decimal("10.0000"),
        )
        pos = Position.objects.get(portfolio=self.portfolio, instrument=self.tcs)
        assert pos.quantity == Decimal("10.0000")
        assert pos.total_invested == Decimal("40030.0000")  # (10 * 4000) + 20 + 10
        assert pos.average_buy_price == Decimal("4003.0000")
        assert pos.realized_pnl == Decimal("0.0000")

    def test_multiple_buys_calculates_weighted_average_cost(self):
        # 1st Buy: 10 @ 4000 (no fees for clarity)
        TransactionService.record_transaction(
            portfolio=self.portfolio,
            instrument=self.tcs,
            tx_type="BUY",
            quantity=Decimal("10.0000"),
            price=Decimal("4000.0000"),
        )
        # 2nd Buy: 10 @ 5000
        TransactionService.record_transaction(
            portfolio=self.portfolio,
            instrument=self.tcs,
            tx_type="BUY",
            quantity=Decimal("10.0000"),
            price=Decimal("5000.0000"),
        )

        pos = Position.objects.get(portfolio=self.portfolio, instrument=self.tcs)
        assert pos.quantity == Decimal("20.0000")
        assert pos.total_invested == Decimal("90000.0000")
        assert pos.average_buy_price == Decimal("4500.0000")

    def test_partial_sell_calculates_realized_pnl_correctly(self):
        # Buy 20 @ 4500 = 90,000 invested
        TransactionService.record_transaction(
            portfolio=self.portfolio,
            instrument=self.tcs,
            tx_type="BUY",
            quantity=Decimal("20.0000"),
            price=Decimal("4500.0000"),
        )
        # Sell 5 @ 5000 (gain of 500 per share = 2,500 gross gain) with 50 fees
        TransactionService.record_transaction(
            portfolio=self.portfolio,
            instrument=self.tcs,
            tx_type="SELL",
            quantity=Decimal("5.0000"),
            price=Decimal("5000.0000"),
            fees=Decimal("50.0000"),
        )

        pos = Position.objects.get(portfolio=self.portfolio, instrument=self.tcs)
        assert pos.quantity == Decimal("15.0000")
        # Avg cost stays 4500
        assert pos.average_buy_price == Decimal("4500.0000")
        # Total invested drops by cost of 5 shares (5 * 4500 = 22,500), so 90000 - 22500 = 67500
        assert pos.total_invested == Decimal("67500.0000")
        # Realized P&L = (5 * 5000) - 50 - (5 * 4500) = 25000 - 50 - 22500 = 2450.0000
        assert pos.realized_pnl == Decimal("2450.0000")

    def test_cannot_sell_more_than_held_quantity(self):
        TransactionService.record_transaction(
            portfolio=self.portfolio,
            instrument=self.tcs,
            tx_type="BUY",
            quantity=Decimal("10.0000"),
            price=Decimal("4000.0000"),
        )

        with pytest.raises(InsufficientPositionException):
            TransactionService.record_transaction(
                portfolio=self.portfolio,
                instrument=self.tcs,
                tx_type="SELL",
                quantity=Decimal("11.0000"),
                price=Decimal("4100.0000"),
            )

    def test_zero_or_negative_quantity_raises_error(self):
        with pytest.raises(Exception):
            TransactionService.record_transaction(
                portfolio=self.portfolio,
                instrument=self.tcs,
                tx_type="BUY",
                quantity=Decimal("0.0000"),
                price=Decimal("4000.0000"),
            )

    def test_delete_transaction_triggers_ledger_recalculation(self):
        tx1 = TransactionService.record_transaction(
            portfolio=self.portfolio,
            instrument=self.tcs,
            tx_type="BUY",
            quantity=Decimal("10.0000"),
            price=Decimal("4000.0000"),
        )
        tx2 = TransactionService.record_transaction(
            portfolio=self.portfolio,
            instrument=self.tcs,
            tx_type="BUY",
            quantity=Decimal("10.0000"),
            price=Decimal("5000.0000"),
        )

        pos = Position.objects.get(portfolio=self.portfolio, instrument=self.tcs)
        assert pos.quantity == Decimal("20.0000")
        assert pos.average_buy_price == Decimal("4500.0000")

        # Delete tx2
        TransactionService.delete_transaction(tx2)

        pos.refresh_from_db()
        assert pos.quantity == Decimal("10.0000")
        assert pos.average_buy_price == Decimal("4000.0000")
        assert pos.total_invested == Decimal("40000.0000")

    def test_portfolio_summary_and_snapshot(self):
        TransactionService.record_transaction(
            portfolio=self.portfolio,
            instrument=self.tcs,
            tx_type="BUY",
            quantity=Decimal("10.0000"),
            price=Decimal("4000.0000"),
        )
        # Create a market price quote
        MarketPrice.objects.create(
            instrument=self.tcs,
            price=Decimal("4200.0000"),
            open_price=Decimal("4050.0000"),
            high_price=Decimal("4250.0000"),
            low_price=Decimal("4050.0000"),
            previous_close=Decimal("4100.0000"),
            change_amount=Decimal("100.0000"),
            change_percent=Decimal("2.44"),
            volume=500000,
            price_timestamp=timezone.now(),
        )

        summary = PortfolioCalculationService.calculate_portfolio_summary(self.portfolio)
        assert summary["positions_count"] == 1
        assert summary["invested_capital"] == Decimal("40000.00")
        assert summary["holdings_value"] == Decimal("42000.00")
        assert summary["unrealized_pnl"] == Decimal("2000.00")
        assert summary["total_return_pct"] == Decimal("5.00")
        # Day P&L: (4200 - 4100) * 10 = +1000
        assert summary["day_pnl"] == Decimal("1000.00")

        # Snapshot
        snapshot = PortfolioCalculationService.record_daily_snapshot(self.portfolio)
        assert snapshot.total_equity == summary["total_equity"]
        assert snapshot.unrealized_pnl == Decimal("2000.0000")
