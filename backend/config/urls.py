"""Root URL Configuration for PortfolioIQ."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

api_v1_patterns = [
    path("auth/", include("apps.accounts.urls")),
    path("instruments/", include("apps.instruments.urls")),
    path("portfolios/", include("apps.portfolios.urls")),
    path("transactions/", include("apps.transactions.urls")),
    path("market-data/", include("apps.market_data.urls")),
    path("analytics/", include("apps.analytics.urls")),
    path("risk/", include("apps.risk.urls")),
    path("options/", include("apps.options.urls")),
    path("alerts/", include("apps.alerts.urls")),
    path("audit/", include("apps.audit.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((api_v1_patterns, "api-v1"))),
    # OpenAPI Schema & Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
