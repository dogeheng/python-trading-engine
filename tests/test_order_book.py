import unittest
from src.core.order import Order, OrderSide
from src.core.order_book import OrderBook


class TestOrderBook(unittest.TestCase):
    def setUp(self):
        """Run before each test method"""
        self.order_book = OrderBook()

    def test_add_order(self):
        """Test adding orders to the order book"""
        # Create a test order
        order = Order("TEST1", price=100.0, quantity=10, side=OrderSide.BUY)

        # Add order and verify it was successful
        success = self.order_book.add_order(order)
        self.assertTrue(success)

        # Verify order is in the book
        self.assertIn(order.order_id, self.order_book.orders)
        self.assertEqual(len(self.order_book.bids[100.0]), 1)

    def test_cancel_order(self):
        """Test cancelling orders"""
        # Add an order first
        order = Order("TEST1", price=100.0, quantity=10, side=OrderSide.SELL)
        self.order_book.add_order(order)

        # Cancel the order
        cancelled_order = self.order_book.cancel_order("TEST1")

        # Verify cancellation
        self.assertIsNotNone(cancelled_order)
        self.assertNotIn("TEST1", self.order_book.orders)
        self.assertEqual(len(self.order_book.asks[100.0]), 0)

    def test_best_bid_ask(self):
        """Test getting best bid/ask prices"""
        # Add some test orders
        self.order_book.add_order(Order("B1", 100.0, 10, OrderSide.BUY))
        self.order_book.add_order(Order("B2", 101.0, 10, OrderSide.BUY))
        self.order_book.add_order(Order("S1", 102.0, 10, OrderSide.SELL))
        self.order_book.add_order(Order("S2", 103.0, 10, OrderSide.SELL))

        # Verify best prices
        self.assertEqual(self.order_book.get_best_bid(), 101.0)
        self.assertEqual(self.order_book.get_best_ask(), 102.0)
