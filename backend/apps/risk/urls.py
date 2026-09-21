"""URL routes for risk analytics and stress tests."""
from django.urls import path

from .views import RiskMetricsView, StressTestView

urlpatterns = [
    path("metrics/", RiskMetricsView.as_view(), name="risk_metrics"),
    path("stress-test/", StressTestView.as_view(), name="stress_test"),
]
