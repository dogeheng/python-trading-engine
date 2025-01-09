import unittest
import asyncio
from src.config.settings import ServerSettings
from src.core.order import Order, OrderSide
from src.server.trading_server import TradingServer


class TestTradingServer(unittest.TestCase):
    def setUp(self):
        # Create test settings
        self.settings = ServerSettings(
            port=12000,
            host="localhost",
            max_order_size=100,
            min_price=0.01
        )
        self.server = TradingServer(self.settings)

    def test_order_validation(self):
        """Test order validation rules"""
        # Test order size limit
        large_order = Order("TEST1", 100.0, 1000, OrderSide.BUY)
        success = self.server.add_order(large_order)
        self.assertFalse(
            success, "Should reject orders larger than max_order_size")

        # Test minimum price
        cheap_order = Order("TEST2", 0.001, 10, OrderSide.SELL)
        success = self.server.add_order(cheap_order)
        self.assertFalse(success, "Should reject orders below min_price")

        # Test valid order
        valid_order = Order("TEST3", 100.0, 50, OrderSide.BUY)
        success = self.server.add_order(valid_order)
        self.assertTrue(success, "Should accept valid orders")

    async def test_server_lifecycle(self):
        """Test server start/stop"""
        # Start server
        await self.server.start()
        self.assertTrue(self.server._running)

        # Stop server
        await self.server.stop()
        self.assertFalse(self.server._running)

    def test_server_lifecycle_sync(self):
        """Synchronous wrapper for async lifecycle test"""
        asyncio.run(self.test_server_lifecycle())
