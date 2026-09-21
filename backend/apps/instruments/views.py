"""Views for Sectors and Instruments."""
from rest_framework import filters, generics, permissions

from .models import Instrument, Sector
from .serializers import InstrumentSerializer, SectorSerializer


class SectorListView(generics.ListAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None


class InstrumentListView(generics.ListAPIView):
    serializer_class = InstrumentSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("symbol", "name", "sector__name")
    ordering_fields = ("symbol", "name", "created_at")
    ordering = ("symbol",)

    def get_queryset(self):
        qs = Instrument.objects.filter(is_active=True).select_related("sector")
        asset_class = self.request.query_params.get("asset_class")
        if asset_class:
            qs = qs.filter(asset_class=asset_class.upper())
        return qs


class InstrumentDetailView(generics.RetrieveAPIView):
    queryset = Instrument.objects.all().select_related("sector")
    serializer_class = InstrumentSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "symbol"
