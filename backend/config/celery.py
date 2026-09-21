"""Celery application configuration for PortfolioIQ."""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("portfolioiq")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks([
    "apps.market_data",
    "apps.portfolios",
    "apps.risk",
    "apps.alerts",
])

# Ensure task registration on worker startup
try:
    import apps.market_data.tasks  # noqa
    import apps.portfolios.tasks
    import apps.risk.tasks
    import apps.alerts.tasks  # noqa
except Exception:
    pass


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
