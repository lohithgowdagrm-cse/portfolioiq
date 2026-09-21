"""WebSocket URL routing for PortfolioIQ."""
from django.urls import re_path

from .consumers import PortfolioUpdatesConsumer

websocket_urlpatterns = [
    re_path(r"^ws/portfolio/(?P<portfolio_id>[0-9a-fA-F-]+)/$", PortfolioUpdatesConsumer.as_asgi()),
]
