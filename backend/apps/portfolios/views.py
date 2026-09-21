"""Views for Portfolio management, dashboard summaries, and holdings."""
from apps.audit.services import record_audit_log
from apps.portfolios.models import Portfolio, PortfolioSnapshot
from apps.portfolios.serializers import PortfolioSerializer, PortfolioSnapshotSerializer
from apps.portfolios.services.accounting import PortfolioCalculationService
from common.permissions.ownership import IsOwner
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class PortfolioViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for portfolios with dashboard summaries and holdings endpoints.
    Strictly isolated to authenticated user.
    """
    serializer_class = PortfolioSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user).order_by("-is_default", "-created_at")

    def perform_create(self, serializer):
        portfolio = serializer.save()
        record_audit_log(
            action="CREATE_PORTFOLIO",
            entity_type="Portfolio",
            entity_id=str(portfolio.id),
            user=self.request.user,
            metadata={"name": portfolio.name, "currency": portfolio.base_currency},
        )

    def perform_destroy(self, instance):
        p_id = str(instance.id)
        p_name = instance.name
        instance.delete()
        record_audit_log(
            action="DELETE_PORTFOLIO",
            entity_type="Portfolio",
            entity_id=p_id,
            user=self.request.user,
            metadata={"name": p_name},
        )

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        """
        Returns high-density 5-second executive summary for dashboard.
        """
        portfolio = self.get_object()
        summary_data = PortfolioCalculationService.calculate_portfolio_summary(portfolio)
        return Response(summary_data)

    @action(detail=True, methods=["get"])
    def positions(self, request, pk=None):
        """
        Returns holdings table with live quote, weighted returns, and allocation metrics.
        """
        portfolio = self.get_object()
        summary_data = PortfolioCalculationService.calculate_portfolio_summary(portfolio)
        return Response({
            "portfolio_id": str(portfolio.id),
            "portfolio_name": portfolio.name,
            "currency": portfolio.base_currency,
            "total_positions": len(summary_data["positions"]),
            "positions": summary_data["positions"],
        })

    @action(detail=True, methods=["get"])
    def snapshots(self, request, pk=None):
        """
        Returns historical equity snapshots for performance charting.
        """
        portfolio = self.get_object()
        limit = int(request.query_params.get("limit", 90))
        snapshots = PortfolioSnapshot.objects.filter(
            portfolio=portfolio
        ).order_by("-snapshot_date")[:limit]
        serializer = PortfolioSnapshotSerializer(reversed(list(snapshots)), many=True)
        return Response(serializer.data)
