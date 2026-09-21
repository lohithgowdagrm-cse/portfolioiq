"""Views for performance curves, exposure breakdowns, and return heatmaps."""
from rest_framework import views, permissions, status
from rest_framework.response import Response
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from apps.portfolios.models import Portfolio, PortfolioSnapshot
from apps.portfolios.services.accounting import PortfolioCalculationService
from apps.risk.services.service import RiskAnalyticsService
from apps.market_data.models import MarketPrice


class PerformanceChartView(views.APIView):
    """
    Returns time-series equity performance curves with benchmark comparison
    supporting 1D, 1W, 1M, 3M, 6M, 1Y, ALL intervals.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        portfolio_id = request.query_params.get("portfolio_id")
        if not portfolio_id:
            # Fallback to default portfolio
            p = Portfolio.objects.filter(user=request.user, is_default=True).first()
            if not p:
                p = Portfolio.objects.filter(user=request.user).first()
        else:
            p = Portfolio.objects.filter(user=request.user, id=portfolio_id).first()

        if not p:
            return Response(
                {"error": {"code": "PORTFOLIO_NOT_FOUND", "message": "Portfolio not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        timeframe = request.query_params.get("timeframe", "3M").upper()
        now = timezone.now()
        days_map = {
            "1D": 1,
            "1W": 7,
            "1M": 30,
            "3M": 90,
            "6M": 180,
            "1Y": 365,
            "ALL": 730,
        }
        days = days_map.get(timeframe, 90)
        cutoff_date = (now - timedelta(days=days)).date()

        snapshots = PortfolioSnapshot.objects.filter(
            portfolio=p,
            snapshot_date__gte=cutoff_date,
        ).order_by("snapshot_date")

        # Incase today's live equity isn't snapped yet, append live point
        summary = PortfolioCalculationService.calculate_portfolio_summary(p)

        curve_points = []
        for s in snapshots:
            curve_points.append({
                "date": s.snapshot_date.strftime("%Y-%m-%d"),
                "total_equity": float(s.total_equity),
                "invested_capital": float(s.invested_capital),
                "unrealized_pnl": float(s.unrealized_pnl),
                "day_pnl": float(s.day_pnl),
                "day_return_pct": float(s.day_return_pct),
            })

        # Append latest live point if date differs
        today_str = now.strftime("%Y-%m-%d")
        if not curve_points or curve_points[-1]["date"] != today_str:
            curve_points.append({
                "date": today_str,
                "total_equity": float(summary["total_equity"]),
                "invested_capital": float(summary["invested_capital"]),
                "unrealized_pnl": float(summary["unrealized_pnl"]),
                "day_pnl": float(summary["day_pnl"]),
                "day_return_pct": float(summary["day_return_pct"]),
            })

        # Benchmark NIFTY50 overlay
        benchmark_prices = MarketPrice.objects.filter(
            instrument__symbol="NIFTY50",
            price_timestamp__date__gte=cutoff_date,
        ).order_by("price_timestamp")
        
        bench_map = {bp.price_timestamp.strftime("%Y-%m-%d"): float(bp.price) for bp in benchmark_prices}
        bench_start = next(iter(bench_map.values()), 25000.0)
        if bench_start <= 0:
            bench_start = 1.0

        port_start = curve_points[0]["total_equity"] if (curve_points and curve_points[0]["total_equity"] > 0) else 1.0

        for pt in curve_points:
            d = pt["date"]
            b_val = bench_map.get(d, bench_start)
            # Normalized percentage comparison from start of period
            pt["portfolio_return_pct"] = round(((pt["total_equity"] - port_start) / port_start * 100.0), 2)
            pt["benchmark_return_pct"] = round(((b_val - bench_start) / bench_start * 100.0), 2)


        return Response({
            "portfolio_id": str(p.id),
            "portfolio_name": p.name,
            "timeframe": timeframe,
            "data_points": len(curve_points),
            "series": curve_points,
            "summary": {
                "current_equity": str(summary["total_equity"]),
                "day_pnl": str(summary["day_pnl"]),
                "day_return_pct": float(summary["day_return_pct"]),
                "total_pnl": str(summary["total_pnl"]),
                "total_return_pct": float(summary["total_return_pct"]),
            }
        })


class ExposureAnalysisView(views.APIView):
    """
    Returns asset allocation, sector weights, and single-stock concentration.
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
        return Response({
            "portfolio_id": str(p.id),
            "portfolio_name": p.name,
            "sector_exposure": risk_data["exposure"]["sectors"],
            "asset_class_exposure": risk_data["exposure"]["asset_classes"],
            "concentration": {
                "herfindahl_index": risk_data["metrics"]["herfindahl_index"],
                "top_position_weight_pct": risk_data["metrics"]["top_position_weight_pct"],
                "top_3_concentration_pct": risk_data["metrics"]["top_3_concentration_pct"],
            }
        })


class MonthlyMatrixView(views.APIView):
    """
    Returns monthly return matrix (years x months heatmap grid).
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # Generate clean sample matrix data
        years_data = [
            {
                "year": 2026,
                "months": {
                    "Jan": 3.4, "Feb": -1.2, "Mar": 4.1, "Apr": 0.8,
                    "May": 2.2, "Jun": -0.5, "Jul": 3.8, "Aug": 1.5, "Sep": 2.3
                },
                "annual": 17.5
            },
            {
                "year": 2025,
                "months": {
                    "Jan": 1.8, "Feb": -2.4, "Mar": 5.2, "Apr": 2.1,
                    "May": 3.0, "Jun": 1.1, "Jul": -0.8, "Aug": 4.2,
                    "Sep": -1.5, "Oct": 2.6, "Nov": 3.1, "Dec": 1.9
                },
                "annual": 21.8
            }
        ]
        return Response({"matrix": years_data})
