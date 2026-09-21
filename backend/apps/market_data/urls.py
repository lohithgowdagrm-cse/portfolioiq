"""URL routes for market data quotes and simulation."""
from django.urls import path

from .views import HistoricalPricesView, LatestQuoteView, SimulateTickView

urlpatterns = [
    path("prices/<str:symbol>/", LatestQuoteView.as_view(), name="latest_quote"),
    path("history/<str:symbol>/", HistoricalPricesView.as_view(), name="historical_prices"),
    path("simulate-tick/", SimulateTickView.as_view(), name="simulate_tick"),
]
