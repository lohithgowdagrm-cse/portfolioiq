"""URL routes for instruments."""
from django.urls import path
from .views import SectorListView, InstrumentListView, InstrumentDetailView

urlpatterns = [
    path("sectors/", SectorListView.as_view(), name="sector_list"),
    path("", InstrumentListView.as_view(), name="instrument_list"),
    path("<str:symbol>/", InstrumentDetailView.as_view(), name="instrument_detail"),
]
