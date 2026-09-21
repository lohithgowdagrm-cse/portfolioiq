"""Celery background tasks for portfolio calculations and snapshot generation."""
import logging

from apps.portfolios.models import Portfolio
from apps.portfolios.services.accounting import PortfolioCalculationService
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def recalculate_portfolio_task(self, portfolio_id: str):
    """
    Asynchronously recalculates portfolio positions and aggregates.
    """
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id)
        summary = PortfolioCalculationService.recalculate_portfolio_from_ledger(portfolio)
        logger.info("Portfolio %s successfully recalculated.", portfolio_id)
        return {"portfolio_id": portfolio_id, "total_equity": str(summary["total_equity"])}
    except Portfolio.DoesNotExist:
        logger.warning("Portfolio %s does not exist.", portfolio_id)
        return {"error": "PORTFOLIO_NOT_FOUND"}
    except Exception as exc:
        logger.exception("Failed to recalculate portfolio %s: %s", portfolio_id, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True)
def generate_daily_snapshot_task(self):
    """
    Nightly cron task taking equity and P&L snapshots for all portfolios.
    """
    portfolios = Portfolio.objects.all()
    count = 0
    for p in portfolios:
        try:
            PortfolioCalculationService.record_daily_snapshot(p)
            count += 1
        except Exception as exc:
            logger.error("Failed to record snapshot for portfolio %s: %s", p.id, exc)

    logger.info("Daily snapshots recorded for %d portfolios.", count)
    return {"snapshots_recorded": count}
