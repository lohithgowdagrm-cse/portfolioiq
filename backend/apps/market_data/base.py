"""Abstract base class for all market data providers."""
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Any


class MarketDataProvider(ABC):
    """
    Standard interface for market data ingestion, supporting live quotes,
    streaming ticks, and historical OHLCV candle lookups.
    """

    @abstractmethod
    def get_latest_quote(self, symbol: str) -> dict[str, Any]:
        """
        Returns latest quote:
        {
            "symbol": "TCS",
            "price": Decimal("4120.50"),
            "open": Decimal("4090.00"),
            "high": Decimal("4150.00"),
            "low": Decimal("4085.00"),
            "previous_close": Decimal("4088.00"),
            "change_amount": Decimal("32.50"),
            "change_percent": Decimal("0.79"),
            "volume": 1205340,
            "timestamp": datetime
        }
        """

    @abstractmethod
    def get_historical_candles(
        self, symbol: str, start_date: datetime, end_date: datetime, interval: str = "1d"
    ) -> list[dict[str, Any]]:
        """
        Returns historical candle list with OHLCV data.
        """

    @abstractmethod
    def simulate_tick(self, symbol: str, current_price: Decimal, volatility: float = 0.015) -> dict[str, Any]:
        """
        Generates a realistic stochastic tick step using geometric Brownian motion.
        """
