"""URL routes for portfolio analytics."""
from django.urls import path
from .views import PerformanceChartView, ExposureAnalysisView, MonthlyMatrixView

urlpatterns = [
    path("performance/", PerformanceChartView.as_view(), name="performance_chart"),
    path("exposure/", ExposureAnalysisView.as_view(), name="exposure_analysis"),
    path("monthly-matrix/", MonthlyMatrixView.as_view(), name="monthly_matrix"),
]
