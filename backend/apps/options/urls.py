"""URL routes for options contracts and Greeks."""
from django.urls import path

from .views import OptionContractListView, OptionsPositionsView, PortfolioGreeksView

urlpatterns = [
    path("contracts/", OptionContractListView.as_view(), name="options_contracts"),
    path("positions/", OptionsPositionsView.as_view(), name="options_positions"),
    path("portfolio-greeks/", PortfolioGreeksView.as_view(), name="portfolio_greeks"),
]
