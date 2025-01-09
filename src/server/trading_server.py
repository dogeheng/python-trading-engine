import asyncio
import logging
from typing import Optional
from ..config.settings import ServerSettings
from ..core.order_book import OrderBook
from ..core.matching_engine import MatchingEngine
from ..core.order import Order


class TradingServer:
    def __init__(self, settings: ServerSettings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.order_book = OrderBook()
        self.matching_engine = MatchingEngine(self.order_book)
        self._running = False
        self._match_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the trading server and initialize background tasks."""
        if self._running:
            return

        self._running = True
        self.logger.info(
            f"Starting trading server on {self.settings.host}:{self.settings.port}")

        # Start the matching loop as a background task
        self._match_task = asyncio.create_task(self._matching_loop())

        # Here you would typically also start your network listeners
        # For example:
        # self._server = await asyncio.start_server(
        #     self._handle_client, self.settings.host, self.settings.port
        # )

    async def stop(self):
        """Gracefully stop the trading server."""
        if not self._running:
            return

        self.logger.info("Stopping trading server...")
        self._running = False

        # Cancel the matching loop
        if self._match_task:
            self._match_task.cancel()
            try:
                await self._match_task
            except asyncio.CancelledError:
                pass

        self.logger.info("Trading server stopped")

    async def _matching_loop(self):
        """Background task that continuously matches orders."""
        try:
            while self._running:
                trades = self.matching_engine.match_orders()
                if trades:
                    self.logger.info(f"Executed {len(trades)} trades")
                await asyncio.sleep(0.1)  # Adjust frequency as needed
        except asyncio.CancelledError:
            self.logger.info("Matching loop cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Error in matching loop: {e}", exc_info=True)
            raise

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle individual client connections."""
        # This is a placeholder for handling client connections
        # You would implement your protocol here
        pass

    def add_order(self, order: Order) -> bool:
        """
        Add a new order to the order book.

        Returns:
            bool: True if order was successfully added, False otherwise
        """
        if order.quantity > self.settings.max_order_size:
            self.logger.warning(f"Order {order.order_id} exceeds maximum size")
            return False

        if order.price < self.settings.min_price:
            self.logger.warning(f"Order {order.order_id} price below minimum")
            return False

        return self.order_book.add_order(order)

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an existing order.

        Returns:
            bool: True if order was found and cancelled, False otherwise
        """
        order = self.order_book.cancel_order(order_id)
        if order:
            self.logger.info(f"Cancelled order {order_id}")
            return True
        return False
