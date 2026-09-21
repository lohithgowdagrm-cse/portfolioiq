"""Views for options contracts, open options positions, and portfolio Greeks."""
from apps.options.models import OptionContract
from apps.options.serializers import OptionContractSerializer
from apps.options.services.service import OptionsService
from apps.portfolios.models import Portfolio
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response


class OptionContractListView(generics.ListAPIView):
    queryset = OptionContract.objects.all().select_related("underlying")
    serializer_class = OptionContractSerializer
    permission_classes = (permissions.IsAuthenticated,)


class OptionsPositionsView(views.APIView):
    """
    Returns open options positions with live calculated Greeks and expiration countdowns.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        portfolio_id = request.query_params.get("portfolio_id")
        p = (
            Portfolio.objects.filter(user=request.user, id=portfolio_id).first()
            if portfolio_id
            else Portfolio.objects.filter(user=request.user, is_default=True).first()
        )
        if not p:
            p = Portfolio.objects.filter(user=request.user).first()

        if not p:
            return Response(
                {"error": {"code": "PORTFOLIO_NOT_FOUND", "message": "Portfolio not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = OptionsService.get_portfolio_options_breakdown(p)
        return Response(data)


class PortfolioGreeksView(views.APIView):
    """
    Returns aggregated portfolio Greeks (Delta, Gamma, Theta, Vega) and expiration horizon.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        portfolio_id = request.query_params.get("portfolio_id")
        p = (
            Portfolio.objects.filter(user=request.user, id=portfolio_id).first()
            if portfolio_id
            else Portfolio.objects.filter(user=request.user, is_default=True).first()
        )
        if not p:
            p = Portfolio.objects.filter(user=request.user).first()

        if not p:
            return Response(
                {"error": {"code": "PORTFOLIO_NOT_FOUND", "message": "Portfolio not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = OptionsService.get_portfolio_options_breakdown(p)
        return Response({
            "portfolio_id": str(p.id),
            "portfolio_name": p.name,
            "aggregate_greeks": data["aggregate_greeks"],
            "expiration_exposure": data["expiration_exposure"],
        })
