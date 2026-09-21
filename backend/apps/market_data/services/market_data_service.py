"""Market data service orchestrating providers, caching, and WebSocket dispatch."""
import logging
from decimal import Decimal
from typing import Any

from apps.instruments.models import Instrument
from apps.market_data.base import MarketDataProvider
from apps.market_data.models import MarketPrice
from apps.market_data.providers.mock_provider import MockMarketDataProvider
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class MarketDataService:
    _provider_instance: MarketDataProvider | None = None

    @classmethod
    def get_provider(cls) -> MarketDataProvider:
        if cls._provider_instance is None:
            # Pluggable provider selection
            provider_type = getattr(settings, "MARKET_DATA_PROVIDER", "mock")
            if provider_type == "mock":
                cls._provider_instance = MockMarketDataProvider()
            else:
                # Default fallback
                cls._provider_instance = MockMarketDataProvider()
        return cls._provider_instance

    @classmethod
    def fetch_and_record_quote(cls, symbol: str) -> MarketPrice | None:
        """
        Fetches latest quote, updates database record, and invalidates cache.
        """
        provider = cls.get_provider()
        quote = provider.get_latest_quote(symbol)

        try:
            instrument = Instrument.objects.get(symbol=symbol.upper())
        except Instrument.DoesNotExist:
            logger.warning("Instrument %s not found in universe.", symbol)
            return None

        # Record new market price quote
        market_price = MarketPrice.objects.create(
            instrument=instrument,
            price=quote["price"],
            open_price=quote["open"],
            high_price=quote["high"],
            low_price=quote["low"],
            previous_close=quote["previous_close"],
            change_amount=quote["change_amount"],
            change_percent=quote["change_percent"],
            volume=quote["volume"],
            price_timestamp=quote["timestamp"],
        )

        # Cache latest price quote for fast O(1) reads
        cache_key = f"quote:{symbol.upper()}"
        cache.set(cache_key, {
            "symbol": symbol.upper(),
            "price": str(quote["price"]),
            "change_percent": float(quote["change_percent"]),
            "change_amount": str(quote["change_amount"]),
            "timestamp": quote["timestamp"].isoformat(),
        }, timeout=300)

        # Broadcast tick update to any interested WebSockets
        cls.broadcast_tick_update(symbol.upper(), quote)

        return market_price

    @classmethod
    def broadcast_tick_update(cls, symbol: str, quote: dict[str, Any]):
        """
        Broadcasts quote to portfolio channels whose holdings include this symbol.
        """
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                from apps.portfolios.models import Position
                portfolios = Position.objects.filter(
                    instrument__symbol=symbol,
                    quantity__gt=Decimal("0.0000"),
                ).values_list("portfolio_id", flat=True).distinct()

                payload = {
                    "symbol": symbol,
                    "price": str(quote["price"]),
                    "change_amount": str(quote["change_amount"]),
                    "change_percent": float(quote["change_percent"]),
                    "timestamp": quote["timestamp"].isoformat(),
                }

                for p_id in portfolios:
                    group_name = f"portfolio_{p_id}"
                    async_to_sync(channel_layer.group_send)(
                        group_name,
                        {
                            "type": "broadcast_tick",
                            "data": payload,
                        }
                    )
        except Exception as exc:
            logger.debug("Channel broadcast skipped or error: %s", exc)
