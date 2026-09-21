"""Seed command populating realistic financial development dataset."""
import random
from datetime import timedelta
from decimal import Decimal

from apps.accounts.models import User
from apps.alerts.models import AlertEvent, AlertRule
from apps.instruments.models import Instrument, Sector
from apps.market_data.models import MarketPrice
from apps.market_data.providers.mock_provider import (
    BASE_EQUITY_PRICES,
    MockMarketDataProvider,
)
from apps.options.models import OptionContract
from apps.portfolios.models import Portfolio, PortfolioSnapshot, Position
from apps.portfolios.services.accounting import PortfolioCalculationService
from apps.risk.models import RiskMetricSnapshot
from apps.transactions.models import Transaction
from common.utilities.constants import (
    AlertComparator,
    AlertMetricType,
    AssetClass,
    BaseCurrency,
    OptionStyle,
    OptionType,
    TransactionType,
)
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone


class Command(BaseCommand):
    help = "Seeds database with 5 users, 3 portfolios, 16+ instruments, options, 100+ transactions, historical prices, snapshots, and alerts."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Beginning PortfolioIQ database seeding..."))
        provider = MockMarketDataProvider(seed=1337)

        # 1. Clean existing records
        self.stdout.write("Purging prior demo data...")
        AlertEvent.objects.all().delete()
        AlertRule.objects.all().delete()
        RiskMetricSnapshot.objects.all().delete()
        PortfolioSnapshot.objects.all().delete()
        Position.objects.all().delete()
        Transaction.objects.all().delete()
        OptionContract.objects.all().delete()
        MarketPrice.objects.all().delete()
        Instrument.objects.all().delete()
        Sector.objects.all().delete()
        Portfolio.objects.all().delete()
        User.objects.filter(email__endswith="@portfolioiq.io").delete()

        # 2. Create 5 Users
        self.stdout.write("Creating 5 institutional users...")
        users_data = [
            ("demo@portfolioiq.io", "Demo", "Portfolio Manager", "INR"),
            ("risk_analyst@portfolioiq.io", "Elena", "Rostova", "INR"),
            ("quant_lead@portfolioiq.io", "Marcus", "Vance", "USD"),
            ("fund_manager@portfolioiq.io", "Rajesh", "Sharma", "INR"),
            ("compliance_officer@portfolioiq.io", "Sarah", "Jenkins", "USD"),
        ]
        created_users = []
        for email, first, last, curr in users_data:
            user = User.objects.create_user(
                email=email,
                password="Password123!",
                first_name=first,
                last_name=last,
                default_currency=curr,
            )
            created_users.append(user)
        primary_user = created_users[0]

        # 3. Create Sectors
        self.stdout.write("Creating market sectors...")
        sectors_meta = [
            ("Information Technology", "IT", "Software, IT services, and enterprise tech"),
            ("Financial Services", "FIN", "Private banks, public lenders, and NBFCs"),
            ("Energy & Petrochemicals", "ENG", "Oil refining, petrochemicals, renewables"),
            ("Automotive", "AUTO", "Passenger vehicles, commercial EVs, components"),
            ("Consumer Goods", "FMCG", "Packaged foods, consumer essentials, tobacco"),
            ("Infrastructure & Capital Goods", "INFRA", "Heavy engineering, construction, power transmission"),
            ("Healthcare & Pharma", "PHARMA", "Formulations, active pharmaceutical ingredients"),
            ("Broad Market Index", "INDEX", "Benchmark market representation"),
        ]
        sector_map = {}
        for name, code, desc in sectors_meta:
            s, _ = Sector.objects.get_or_create(name=name, code=code, defaults={"description": desc})
            sector_map[code] = s

        # 4. Create 16+ Instruments
        self.stdout.write("Creating instrument universe...")
        instruments_data = [
            ("TCS", "Tata Consultancy Services Ltd.", AssetClass.EQUITY, "IT", "NSE", "INR"),
            ("INFY", "Infosys Ltd.", AssetClass.EQUITY, "IT", "NSE", "INR"),
            ("RELIANCE", "Reliance Industries Ltd.", AssetClass.EQUITY, "ENG", "NSE", "INR"),
            ("HDFCBANK", "HDFC Bank Ltd.", AssetClass.EQUITY, "FIN", "NSE", "INR"),
            ("ICICIBANK", "ICICI Bank Ltd.", AssetClass.EQUITY, "FIN", "NSE", "INR"),
            ("SBIN", "State Bank of India", AssetClass.EQUITY, "FIN", "NSE", "INR"),
            ("TATAMOTORS", "Tata Motors Ltd.", AssetClass.EQUITY, "AUTO", "NSE", "INR"),
            ("BHARTIARTL", "Bharti Airtel Ltd.", AssetClass.EQUITY, "IT", "NSE", "INR"),
            ("ITC", "ITC Ltd.", AssetClass.EQUITY, "FMCG", "NSE", "INR"),
            ("LT", "Larsen & Toubro Ltd.", AssetClass.EQUITY, "INFRA", "NSE", "INR"),
            ("SUNPHARMA", "Sun Pharmaceutical Industries Ltd.", AssetClass.EQUITY, "PHARMA", "NSE", "INR"),
            ("NIFTY50", "NIFTY 50 Index", AssetClass.ETF, "INDEX", "NSE", "INR"),
            ("NIFTYBEES", "Nippon India ETF Nifty BeES", AssetClass.ETF, "INDEX", "NSE", "INR"),
            ("GOLDBEES", "Nippon India ETF Gold BeES", AssetClass.ETF, "INDEX", "NSE", "INR"),
            ("AAPL", "Apple Inc.", AssetClass.EQUITY, "IT", "NASDAQ", "USD"),
            ("MSFT", "Microsoft Corporation", AssetClass.EQUITY, "IT", "NASDAQ", "USD"),
            ("NVDA", "NVIDIA Corporation", AssetClass.EQUITY, "IT", "NASDAQ", "USD"),
        ]
        inst_map = {}
        for sym, name, a_class, s_code, exch, curr in instruments_data:
            inst = Instrument.objects.create(
                symbol=sym,
                name=name,
                asset_class=a_class,
                sector=sector_map[s_code],
                exchange=exch,
                currency=curr,
                is_active=True,
            )
            inst_map[sym] = inst

        # 5. Generate 90 days of historical prices for each instrument
        self.stdout.write("Synthesizing 90 days of historical daily OHLCV prices...")
        end_time = timezone.now()
        start_time = end_time - timedelta(days=90)
        
        all_market_prices = []
        for sym, inst in inst_map.items():
            candles = provider.get_historical_candles(sym, start_time, end_time)
            prev_close = Decimal(str(round(float(BASE_EQUITY_PRICES.get(sym, Decimal("1000.00"))) * 0.75, 2)))
            for c in candles:
                chg_amt = (c["close"] - prev_close).quantize(Decimal("0.01"))
                chg_pct = ((chg_amt / prev_close * Decimal(100)) if prev_close > 0 else Decimal(0)).quantize(Decimal("0.01"))
                all_market_prices.append(MarketPrice(
                    instrument=inst,
                    price=c["close"],
                    open_price=c["open"],
                    high_price=c["high"],
                    low_price=c["low"],
                    previous_close=prev_close,
                    change_amount=chg_amt,
                    change_percent=chg_pct,
                    volume=c["volume"],
                    price_timestamp=c["timestamp"],
                ))
                prev_close = c["close"]

        MarketPrice.objects.bulk_create(all_market_prices)
        self.stdout.write(f"Generated {len(all_market_prices)} historical quote points.")

        # 6. Create Options Contracts
        self.stdout.write("Creating options contracts...")
        expiry_1 = (end_time + timedelta(days=28)).date()
        expiry_2 = (end_time + timedelta(days=56)).date()

        opt_contracts = [
            ("TCS", OptionType.CALL, Decimal("4200.0000"), expiry_1, 100),
            ("TCS", OptionType.PUT, Decimal("4000.0000"), expiry_1, 100),
            ("RELIANCE", OptionType.CALL, Decimal("3000.0000"), expiry_1, 250),
            ("RELIANCE", OptionType.PUT, Decimal("2850.0000"), expiry_1, 250),
            ("INFY", OptionType.CALL, Decimal("1900.0000"), expiry_1, 400),
            ("INFY", OptionType.PUT, Decimal("1800.0000"), expiry_1, 400),
            ("NIFTY50", OptionType.CALL, Decimal("25500.0000"), expiry_2, 50),
            ("NIFTY50", OptionType.PUT, Decimal("25000.0000"), expiry_2, 50),
        ]
        created_options = []
        for sym, o_type, strike, exp, mult in opt_contracts:
            opt = OptionContract.objects.create(
                underlying=inst_map[sym],
                option_type=o_type,
                strike_price=strike,
                expiration_date=exp,
                contract_multiplier=mult,
                style=OptionStyle.EUROPEAN,
            )
            created_options.append(opt)

        # 7. Create 3 Portfolios for Demo User
        self.stdout.write("Creating 3 investment portfolios...")
        p1 = Portfolio.objects.create(
            user=primary_user,
            name="Flagship Tech & Bluechip Alpha",
            description="Core institutional portfolio focusing on top Indian bluechips and compounding tech giants.",
            base_currency=BaseCurrency.INR,
            cash_balance=Decimal("250000.0000"),
            is_default=True,
        )
        p2 = Portfolio.objects.create(
            user=primary_user,
            name="All-Weather Dividend & Value",
            description="Defensive portfolio weighted heavily in dividend-paying financial institutions, energy, and FMCG.",
            base_currency=BaseCurrency.INR,
            cash_balance=Decimal("420000.0000"),
            is_default=False,
        )
        p3 = Portfolio.objects.create(
            user=primary_user,
            name="Derivatives Hedged Strategy",
            description="Alpha generation strategy with active equity long holdings paired with protective index put hedges.",
            base_currency=BaseCurrency.INR,
            cash_balance=Decimal("185000.0000"),
            is_default=False,
        )

        # 8. Seed 110+ Realistic Transactions spanning 80 days
        self.stdout.write("Seeding 110+ transactions across portfolios...")
        random.seed(42)

        # Transactions for Portfolio 1 (Flagship Alpha)
        p1_tickers = ["TCS", "INFY", "RELIANCE", "HDFCBANK", "TATAMOTORS", "LT", "BHARTIARTL"]
        tx_count = 0

        # Start 75 days ago
        for days_ago in range(75, 5, -2):
            tx_date = end_time - timedelta(days=days_ago, hours=random.randint(1, 6), minutes=random.randint(5, 50))
            sym = random.choice(p1_tickers)
            inst = inst_map[sym]
            base_p = BASE_EQUITY_PRICES[sym]
            
            # Historical price around base with some variance
            tx_price = (base_p * Decimal(str(round(random.uniform(0.85, 1.05), 2)))).quantize(Decimal("0.05"))
            qty = Decimal(str(random.randint(5, 25)))
            fees = Decimal("25.0000")
            taxes = Decimal("12.5000")

            Transaction.objects.create(
                portfolio=p1,
                instrument=inst,
                transaction_type=TransactionType.BUY,
                quantity=qty,
                price=tx_price,
                fees=fees,
                taxes=taxes,
                executed_at=tx_date,
                notes=f"Accumulation tranche for {sym}",
            )
            tx_count += 1

        # Add global equity accumulation in P1
        for sym in ["AAPL", "MSFT", "NVDA"]:
            for days_ago in range(60, 5, -6):
                tx_date = end_time - timedelta(days=days_ago, hours=random.randint(1, 3))
                inst = inst_map[sym]
                base_p = BASE_EQUITY_PRICES[sym]
                tx_price = (base_p * Decimal(str(round(random.uniform(0.92, 1.04), 2)))).quantize(Decimal("0.05"))
                qty = Decimal(str(random.randint(10, 40)))
                Transaction.objects.create(
                    portfolio=p1,
                    instrument=inst,
                    transaction_type=TransactionType.BUY,
                    quantity=qty,
                    price=tx_price,
                    fees=Decimal("15.0000"),
                    taxes=Decimal("5.0000"),
                    executed_at=tx_date,
                    notes=f"Global tech accumulation {sym}",
                )
                tx_count += 1

        # Add a couple of profit-taking sales in P1
        Transaction.objects.create(
            portfolio=p1,
            instrument=inst_map["INFY"],
            transaction_type=TransactionType.SELL,
            quantity=Decimal("15.0000"),
            price=Decimal("1910.0000"),
            fees=Decimal("40.0000"),
            taxes=Decimal("20.0000"),
            executed_at=end_time - timedelta(days=12),
            notes="Quarterly rebalancing profit take",
        )
        tx_count += 1

        # Transactions for Portfolio 2 (Dividend & Value)
        p2_tickers = ["HDFCBANK", "ICICIBANK", "SBIN", "ITC", "RELIANCE", "NIFTYBEES", "GOLDBEES"]
        for days_ago in range(70, 3, -2):
            tx_date = end_time - timedelta(days=days_ago, hours=random.randint(2, 5))
            sym = random.choice(p2_tickers)
            inst = inst_map[sym]
            base_p = BASE_EQUITY_PRICES.get(sym, Decimal("500.00"))
            tx_price = (base_p * Decimal(str(round(random.uniform(0.88, 1.02), 2)))).quantize(Decimal("0.05"))
            qty = Decimal(str(random.randint(20, 60) if base_p < Decimal(1000) else random.randint(10, 25)))

            Transaction.objects.create(
                portfolio=p2,
                instrument=inst,
                transaction_type=TransactionType.BUY,
                quantity=qty,
                price=tx_price,
                fees=Decimal("20.0000"),
                taxes=Decimal("10.0000"),
                executed_at=tx_date,
                notes=f"Systematic value accumulation {sym}",
            )
            tx_count += 1

        # Dividend in P2
        Transaction.objects.create(
            portfolio=p2,
            instrument=inst_map["ITC"],
            transaction_type=TransactionType.DIVIDEND,
            quantity=Decimal("120.0000"),
            price=Decimal("7.5000"),  # ₹7.50 dividend per share
            fees=Decimal("0.0000"),
            taxes=Decimal("90.0000"),
            executed_at=end_time - timedelta(days=18),
            notes="Interim Dividend Credit",
        )
        tx_count += 1

        # Transactions for Portfolio 3 (Derivatives Hedged)
        p3_tickers = ["TCS", "RELIANCE", "NIFTY50"]
        for days_ago in range(50, 4, -3):
            tx_date = end_time - timedelta(days=days_ago, hours=random.randint(1, 4))
            sym = random.choice(p3_tickers)
            inst = inst_map[sym]
            base_p = BASE_EQUITY_PRICES[sym]
            tx_price = (base_p * Decimal(str(round(random.uniform(0.90, 1.02), 2)))).quantize(Decimal("0.05"))
            qty = Decimal(str(random.randint(10, 30)))

            Transaction.objects.create(
                portfolio=p3,
                instrument=inst,
                transaction_type=TransactionType.BUY,
                quantity=qty,
                price=tx_price,
                fees=Decimal("30.0000"),
                taxes=Decimal("15.0000"),
                executed_at=tx_date,
                notes="Equity long leg",
            )
            tx_count += 1

        # Options positions in P3
        Transaction.objects.create(
            portfolio=p3,
            instrument=inst_map["NIFTY50"],
            option_contract=created_options[7],  # NIFTY Put 25000
            transaction_type=TransactionType.BUY,
            quantity=Decimal("2.0000"),  # 2 lots
            price=Decimal("185.5000"),  # Option premium
            fees=Decimal("50.0000"),
            taxes=Decimal("25.0000"),
            executed_at=end_time - timedelta(days=20),
            notes="Protective tail-risk Put hedge",
        )
        tx_count += 1

        Transaction.objects.create(
            portfolio=p3,
            instrument=inst_map["TCS"],
            option_contract=created_options[0],  # TCS Call 4200
            transaction_type=TransactionType.BUY,
            quantity=Decimal("1.0000"),  # 1 lot
            price=Decimal("92.4000"),
            fees=Decimal("30.0000"),
            taxes=Decimal("15.0000"),
            executed_at=end_time - timedelta(days=15),
            notes="Covered Call overlay",
        )
        tx_count += 1

        self.stdout.write(f"Total transactions created: {tx_count}")

        # 9. Reconcile Positions for all 3 portfolios
        self.stdout.write("Reconciling position balances and cash reserves from transaction ledger...")
        for p in [p1, p2, p3]:
            PortfolioCalculationService.recalculate_portfolio_from_ledger(p)

        # 10. Generate 60 Daily Historical Snapshots for each portfolio
        self.stdout.write("Generating historical daily equity snapshots for charting...")
        for p in [p1, p2, p3]:
            summary = PortfolioCalculationService.calculate_portfolio_summary(p)
            current_eq = float(summary["total_equity"])
            # Synthesize realistic historical trajectory
            sim_date = (end_time - timedelta(days=60)).date()
            base_sim_eq = current_eq * 0.88  # Portfolio gained ~12% over 60 days
            
            sim_val = base_sim_eq
            while sim_date <= end_time.date():
                if sim_date.weekday() < 5:  # Weekdays only
                    daily_ret = random.gauss(0.0018, 0.008)
                    prev_val = sim_val
                    sim_val = sim_val * (1.0 + daily_ret)
                    day_pnl_val = sim_val - prev_val
                    day_ret_pct = (day_pnl_val / prev_val * 100.0) if prev_val > 0 else 0.0

                    PortfolioSnapshot.objects.create(
                        portfolio=p,
                        snapshot_date=sim_date,
                        total_equity=Decimal(str(round(sim_val, 4))),
                        cash_balance=p.cash_balance,
                        invested_capital=summary["invested_capital"],
                        unrealized_pnl=Decimal(str(round(sim_val - float(summary["invested_capital"]), 4))),
                        realized_pnl=summary["realized_pnl"],
                        day_pnl=Decimal(str(round(day_pnl_val, 4))),
                        day_return_pct=Decimal(str(round(day_ret_pct, 4))),
                    )
                sim_date += timedelta(days=1)

        # 11. Generate Risk Metric Snapshots
        self.stdout.write("Computing and storing risk metric snapshots...")
        for p in [p1, p2, p3]:
            RiskMetricSnapshot.objects.create(
                portfolio=p,
                calculation_date=end_time.date(),
                volatility_annualized=Decimal("16.4200") if p == p1 else Decimal("11.8500"),
                sharpe_ratio=Decimal("1.8400") if p == p1 else Decimal("1.4200"),
                beta=Decimal("1.0800") if p == p1 else Decimal("0.8400"),
                max_drawdown=Decimal("6.7500") if p == p1 else Decimal("4.2000"),
                var_95_daily=Decimal("18500.0000"),
                var_99_daily=Decimal("29400.0000"),
                concentration_herfindahl=Decimal("0.1850"),
                sector_exposure={
                    "Information Technology": 38.5,
                    "Financial Services": 24.2,
                    "Energy & Petrochemicals": 18.1,
                    "Automotive": 10.4,
                    "Infrastructure": 8.8,
                },
                asset_exposure={
                    "Equities": 84.5,
                    "ETFs / Cash": 12.5,
                    "Derivatives": 3.0,
                },
            )

        # 12. Create Alert Rules & Triggered Events
        self.stdout.write("Configuring active risk alert rules and events...")
        r1 = AlertRule.objects.create(
            user=primary_user,
            portfolio=p1,
            metric_type=AlertMetricType.DRAWDOWN,
            comparator=AlertComparator.GT,
            threshold_value=Decimal("8.0000"),  # Drawdown > 8%
            is_active=True,
        )
        r2 = AlertRule.objects.create(
            user=primary_user,
            portfolio=p1,
            metric_type=AlertMetricType.CONCENTRATION,
            comparator=AlertComparator.GT,
            threshold_value=Decimal("25.0000"),  # Single position > 25%
            is_active=True,
        )
        r3 = AlertRule.objects.create(
            user=primary_user,
            portfolio=p1,
            metric_type=AlertMetricType.DAILY_LOSS,
            comparator=AlertComparator.GT,
            threshold_value=Decimal("20000.0000"),  # Day loss > 20,000
            is_active=True,
        )
        r4 = AlertRule.objects.create(
            user=primary_user,
            portfolio=p1,
            metric_type=AlertMetricType.OPTION_EXPIRY,
            comparator=AlertComparator.LTE,
            threshold_value=Decimal("7.0000"),  # Option expiring within 7 days
            is_active=True,
        )

        # Seed realistic triggered alert events
        AlertEvent.objects.create(
            rule=r2,
            triggered_value=Decimal("26.4000"),
            message="TCS position weight reached 26.40%, breaching single-asset limit of 25.00%.",
            is_acknowledged=False,
            created_at=end_time - timedelta(hours=3),
        )
        AlertEvent.objects.create(
            rule=r1,
            triggered_value=Decimal("8.2400"),
            message="Core Tech Portfolio drawdown momentarily breached 8.00% during market pullback.",
            is_acknowledged=True,
            created_at=end_time - timedelta(days=14),
        )

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
        self.stdout.write(self.style.SUCCESS("Demo login: demo@portfolioiq.io / Password123!"))
