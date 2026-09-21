"""Celery background tasks for scheduled risk calculations."""
import logging

from apps.portfolios.models import Portfolio
from apps.risk.services.service import RiskAnalyticsService
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def calculate_daily_risk_task(self):
    """
    Computes daily risk snapshots (volatility, Sharpe, beta, VaR) for all portfolios.
    """
    portfolios = Portfolio.objects.all()
    count = 0
    for p in portfolios:
        try:
            RiskAnalyticsService.save_daily_risk_snapshot(p)
            count += 1
        except Exception as exc:
            logger.error("Failed to compute risk snapshot for portfolio %s: %s", p.id, exc)

    logger.info("Daily risk calculations completed for %d portfolios.", count)
    return {"calculated": count}
