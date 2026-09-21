"""Celery background tasks for evaluating risk alerts."""
import logging
from decimal import Decimal

from apps.alerts.models import AlertEvent, AlertRule
from apps.portfolios.services.accounting import PortfolioCalculationService
from apps.risk.services.service import RiskAnalyticsService
from celery import shared_task
from common.utilities.constants import AlertComparator, AlertMetricType
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_alerts_task(self):
    """
    Evaluates active AlertRule conditions and generates AlertEvents for breaches.
    """
    rules = AlertRule.objects.filter(is_active=True).select_related("portfolio", "user")
    events_triggered = 0

    for rule in rules:
        try:
            p = rule.portfolio
            summary = PortfolioCalculationService.calculate_portfolio_summary(p)
            breached = False
            current_val = Decimal("0.00")
            msg = ""

            if rule.metric_type == AlertMetricType.DRAWDOWN:
                risk_data = RiskAnalyticsService.calculate_portfolio_risk(p)
                current_val = risk_data["metrics"]["max_drawdown_pct"]
                if rule.comparator == AlertComparator.GT and current_val > rule.threshold_value:
                    breached = True
                    msg = f"Drawdown reached {current_val}%, exceeding threshold of {rule.threshold_value}%."

            elif rule.metric_type == AlertMetricType.CONCENTRATION:
                risk_data = RiskAnalyticsService.calculate_portfolio_risk(p)
                current_val = risk_data["metrics"]["top_position_weight_pct"]
                if rule.comparator == AlertComparator.GT and current_val > rule.threshold_value:
                    breached = True
                    msg = f"Top position weight reached {current_val}%, exceeding limit of {rule.threshold_value}%."

            elif rule.metric_type == AlertMetricType.DAILY_LOSS:
                day_pnl = summary["day_pnl"]
                if day_pnl < Decimal("0.00"):
                    current_val = abs(day_pnl)
                    if rule.comparator == AlertComparator.GT and current_val > rule.threshold_value:
                        breached = True
                        msg = f"Daily portfolio loss reached ₹{current_val:,.2f}, breaching daily stop limit of ₹{rule.threshold_value:,.2f}."

            if breached:
                # Deduplication: check if unacknowledged alert for this rule exists within last 2 hours
                two_hours_ago = timezone.now() - timezone.timedelta(hours=2)
                recent_exists = AlertEvent.objects.filter(
                    rule=rule,
                    is_acknowledged=False,
                    created_at__gte=two_hours_ago,
                ).exists()

                if not recent_exists:
                    event = AlertEvent.objects.create(
                        rule=rule,
                        triggered_value=current_val,
                        message=msg,
                        is_acknowledged=False,
                    )
                    events_triggered += 1
                    logger.warning("Alert triggered for rule %s: %s", rule.id, msg)
        except Exception as exc:
            logger.error("Error evaluating alert rule %s: %s", rule.id, exc)

    return {"events_triggered": events_triggered}
