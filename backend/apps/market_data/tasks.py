"""Celery background tasks for market data ingestion and price polling."""
import logging
from celery import shared_task
from apps.instruments.models import Instrument
from apps.market_data.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def fetch_market_prices(self):
    """
    Periodically refreshes quotes for all active universe instruments.
    """
    instruments = Instrument.objects.filter(is_active=True).values_list("symbol", flat=True)
    success_count = 0
    for sym in instruments:
        try:
            MarketDataService.fetch_and_record_quote(sym)
            success_count += 1
        except Exception as exc:
            logger.warning("Error fetching quote for %s: %s", sym, exc)

    logger.info("Market price ingestion finished for %d instruments.", success_count)
    return {"ingested": success_count}


@shared_task(bind=True, max_retries=2)
def simulate_market_tick_task(self, symbol=None):
    """
    Simulates a stochastic tick event and dispatches over WebSocket.
    """
    try:
        if not symbol:
            first_inst = Instrument.objects.filter(is_active=True).first()
            symbol = first_inst.symbol if first_inst else "TCS"
        MarketDataService.fetch_and_record_quote(symbol)
        return {"status": "ok", "symbol": symbol}
    except Exception as exc:
        logger.error("Error in simulate_market_tick_task: %s", exc)
        raise self.retry(exc=exc)
