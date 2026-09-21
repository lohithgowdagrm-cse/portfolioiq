"""WebSocket consumers for real-time market data and portfolio updates."""
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class PortfolioUpdatesConsumer(AsyncWebsocketConsumer):
    """
    Subscribes client to real-time portfolio ticks, P&L adjustments, and risk breaches.
    """
    async def connect(self):
        self.portfolio_id = self.scope["url_route"]["kwargs"]["portfolio_id"]
        self.room_group_name = f"portfolio_{self.portfolio_id}"

        # Join portfolio group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        logger.info("WebSocket connected for portfolio %s", self.portfolio_id)

    async def disconnect(self, close_code):
        # Leave portfolio group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info("WebSocket disconnected for portfolio %s", self.portfolio_id)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get("action")
            if action == "PING":
                await self.send(text_data=json.dumps({"type": "PONG"}))
        except Exception as exc:
            logger.error("Error parsing websocket incoming message: %s", exc)

    async def broadcast_tick(self, event):
        """Handler for tick updates from Celery / MarketDataProvider."""
        await self.send(text_data=json.dumps({
            "type": "TICK_UPDATE",
            "data": event["data"]
        }))

    async def broadcast_portfolio_update(self, event):
        """Handler for aggregated portfolio equity and P&L changes."""
        await self.send(text_data=json.dumps({
            "type": "PORTFOLIO_UPDATE",
            "data": event["data"]
        }))

    async def broadcast_risk_alert(self, event):
        """Handler for newly triggered risk breaches."""
        await self.send(text_data=json.dumps({
            "type": "RISK_ALERT",
            "data": event["data"]
        }))
