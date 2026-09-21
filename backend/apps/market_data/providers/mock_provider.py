"""Mock market data provider using geometric Brownian motion and curated seed prices."""
import math
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from apps.market_data.base import MarketDataProvider
from django.utils import timezone

# Curated reference baseline quotes
BASE_EQUITY_PRICES = {
    "RELIANCE": Decimal("2950.40"),
    "TCS": Decimal("4150.25"),
    "INFY": Decimal("1875.50"),
    "HDFCBANK": Decimal("1640.80"),
    "ICICIBANK": Decimal("1220.15"),
    "TATAMOTORS": Decimal("985.60"),
    "BHARTIARTL": Decimal("1540.30"),
    "ITC": Decimal("510.75"),
    "SBIN": Decimal("815.20"),
    "LT": Decimal("3620.00"),
    "NIFTY50": Decimal("25380.00"),
    "AAPL": Decimal("225.50"),
    "MSFT": Decimal("448.20"),
    "NVDA": Decimal("128.40"),
    "GOOGL": Decimal("176.80"),
    "SPY": Decimal("565.30"),
}


class MockMarketDataProvider(MarketDataProvider):
    """
    Realistic simulated market data provider supporting high-fidelity historical candle
    reconstruction and stochastic price progression.
    """

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)

    def get_latest_quote(self, symbol: str) -> dict[str, Any]:
        base = BASE_EQUITY_PRICES.get(symbol.upper(), Decimal("1000.00"))
        # Introduce small intraday variance (+- 1.5%)
        pct_change = Decimal(str(round(self.random.uniform(-1.5, 1.8), 2)))
        change_amt = (base * pct_change / Decimal(100)).quantize(Decimal("0.05"))
        ltp = (base + change_amt).quantize(Decimal("0.05"))
        open_price = (base + Decimal(str(round(self.random.uniform(-0.5, 0.5), 2)))).quantize(Decimal("0.05"))
        high = max(ltp, open_price) + Decimal(str(round(self.random.uniform(5.0, 20.0), 2)))
        low = min(ltp, open_price) - Decimal(str(round(self.random.uniform(5.0, 20.0), 2)))

        return {
            "symbol": symbol.upper(),
            "price": ltp,
            "open": open_price,
            "high": high.quantize(Decimal("0.05")),
            "low": low.quantize(Decimal("0.05")),
            "previous_close": base,
            "change_amount": change_amt,
            "change_percent": pct_change,
            "volume": self.random.randint(150000, 3500000),
            "timestamp": timezone.now(),
        }

    def simulate_tick(self, symbol: str, current_price: Decimal, volatility: float = 0.015) -> dict[str, Any]:
        """
        Step current price forward using geometric Brownian motion:
        dS = S * (mu*dt + sigma*sqrt(dt)*Z)
        """
        curr = float(current_price)
        dt = 1.0 / 252.0 / 390.0  # 1-minute step in trading year
        drift = 0.08 * dt  # 8% annual drift
        diffusion = volatility * math.sqrt(dt) * self.random.gauss(0, 1)
        new_val = curr * math.exp(drift - 0.5 * (volatility ** 2) * dt + diffusion)
        new_price = Decimal(str(round(new_val, 2)))

        change_amt = (new_price - current_price).quantize(Decimal("0.01"))
        change_pct = (
            (change_amt / current_price * Decimal(100)).quantize(Decimal("0.01"))
            if current_price > Decimal(0)
            else Decimal("0.00")
        )

        return {
            "symbol": symbol.upper(),
            "price": new_price,
            "change_amount": change_amt,
            "change_percent": change_pct,
            "timestamp": timezone.now(),
        }

    def get_historical_candles(
        self, symbol: str, start_date: datetime, end_date: datetime, interval: str = "1d"
    ) -> list[dict[str, Any]]:
        """
        Synthesizes realistic historical OHLCV data between start_date and end_date.
        """
        candles = []
        base_price = float(BASE_EQUITY_PRICES.get(symbol.upper(), Decimal("1000.00")))
        curr = base_price * 0.75  # Start from 25% lower historical baseline

        # Generate day by day
        curr_date = start_date
        while curr_date <= end_date:
            # Skip weekends
            if curr_date.weekday() < 5:
                daily_return = self.random.gauss(0.0004, 0.012)
                open_p = curr
                close_p = curr * math.exp(daily_return)
                high_p = max(open_p, close_p) * (1.0 + abs(self.random.gauss(0, 0.006)))
                low_p = min(open_p, close_p) * (1.0 - abs(self.random.gauss(0, 0.006)))
                vol = self.random.randint(200000, 2500000)

                candles.append({
                    "timestamp": curr_date,
                    "date": curr_date.strftime("%Y-%m-%d"),
                    "open": Decimal(str(round(open_p, 2))),
                    "high": Decimal(str(round(high_p, 2))),
                    "low": Decimal(str(round(low_p, 2))),
                    "close": Decimal(str(round(close_p, 2))),
                    "volume": vol,
                })
                curr = close_p
            curr_date += timedelta(days=1)

        return candles
