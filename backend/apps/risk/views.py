"""Views for portfolio risk metrics, stress testing, and drawdown analysis."""
from rest_framework import views, permissions, status
from rest_framework.response import Response
from apps.portfolios.models import Portfolio
from apps.risk.services.service import RiskAnalyticsService
from apps.risk.services.stress_testing import StressTestingService
from apps.risk.serializers import StressTestRequestSerializer


class RiskMetricsView(views.APIView):
    """
    Returns complete institutional risk metrics (Volatility, Sharpe, Beta, Max Drawdown, VaR 95/99).
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

        risk_data = RiskAnalyticsService.calculate_portfolio_risk(p)
        return Response(risk_data)


class StressTestView(views.APIView):
    """
    Executes macro market shock or custom asset stress test scenario.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = StressTestRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        portfolio_id = serializer.validated_data.get("portfolio_id")
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

        market_shock = serializer.validated_data.get("market_shock_pct", 0.0)
        custom_shocks = serializer.validated_data.get("custom_shocks", {})

        result = StressTestingService.run_scenario(
            portfolio=p,
            market_shock_pct=market_shock,
            custom_shocks=custom_shocks,
        )
        return Response(result)
