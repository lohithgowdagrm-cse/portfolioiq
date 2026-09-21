"""Views for Market Data quotes, historical series, and tick simulation."""
from rest_framework import views, permissions, status
from rest_framework.response import Response
from apps.market_data.models import MarketPrice
from apps.market_data.serializers import MarketPriceSerializer
from apps.market_data.services.market_data_service import MarketDataService
from apps.instruments.models import Instrument


class LatestQuoteView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, symbol):
        price_obj = MarketPrice.objects.filter(
            instrument__symbol__iexact=symbol
        ).order_by("-price_timestamp").first()

        if not price_obj:
            price_obj = MarketDataService.fetch_and_record_quote(symbol)

        if not price_obj:
            return Response(
                {"error": {"code": "QUOTE_NOT_FOUND", "message": f"Quote for symbol {symbol} not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MarketPriceSerializer(price_obj)
        return Response(serializer.data)


class HistoricalPricesView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, symbol):
        limit = int(request.query_params.get("limit", 90))
        quotes = MarketPrice.objects.filter(
            instrument__symbol__iexact=symbol
        ).order_by("-price_timestamp")[:limit]

        serializer = MarketPriceSerializer(reversed(list(quotes)), many=True)
        return Response(serializer.data)


class SimulateTickView(views.APIView):
    """
    Triggers a live price tick simulation step and broadcasts the update
    via WebSockets to active clients.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        symbol = request.data.get("symbol")
        if not symbol:
            # Pick a default active symbol like TCS or RELIANCE
            first_inst = Instrument.objects.filter(is_active=True).first()
            symbol = first_inst.symbol if first_inst else "TCS"

        try:
            inst = Instrument.objects.get(symbol__iexact=symbol)
        except Instrument.DoesNotExist:
            return Response(
                {"error": {"code": "INSTRUMENT_NOT_FOUND", "message": f"Instrument {symbol} does not exist."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        latest_price = inst.market_prices.order_by("-price_timestamp").first()
        current_p = latest_price.price if latest_price else 1000.0

        provider = MarketDataService.get_provider()
        tick = provider.simulate_tick(symbol=inst.symbol, current_price=current_p)

        # Record new market price
        new_quote = MarketPrice.objects.create(
            instrument=inst,
            price=tick["price"],
            open_price=latest_price.open_price if latest_price else tick["price"],
            high_price=max(tick["price"], latest_price.high_price if latest_price else tick["price"]),
            low_price=min(tick["price"], latest_price.low_price if latest_price else tick["price"]),
            previous_close=latest_price.previous_close if latest_price else tick["price"],
            change_amount=tick["change_amount"],
            change_percent=tick["change_percent"],
            volume=(latest_price.volume if latest_price else 100000) + 1500,
            price_timestamp=tick["timestamp"],
        )

        # Broadcast via WebSockets
        MarketDataService.broadcast_tick_update(inst.symbol, {
            "price": new_quote.price,
            "change_amount": new_quote.change_amount,
            "change_percent": new_quote.change_percent,
            "timestamp": new_quote.price_timestamp,
        })

        return Response(MarketPriceSerializer(new_quote).data)
