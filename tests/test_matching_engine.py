import unittest
from src.core.order import Order, OrderSide
from src.core.order_book import OrderBook
from src.core.matching_engine import MatchingEngine


class TestMatchingEngine(unittest.TestCase):
    def setUp(self):
        self.order_book = OrderBook()
        self.matching_engine = MatchingEngine(self.order_book)

    def test_match_orders(self):
        """Test basic order matching"""
        # Add a buy order
        buy_order = Order("B1", price=100.0, quantity=10, side=OrderSide.BUY)
        self.order_book.add_order(buy_order)

        # Add a matching sell order
        sell_order = Order("S1", price=100.0, quantity=10, side=OrderSide.SELL)
        self.order_book.add_order(sell_order)

        # Execute matching
        trades = self.matching_engine.match_orders()

        # Verify trade execution
        self.assertEqual(len(trades), 1)
        trade = trades[0]
        self.assertEqual(trade.quantity, 10)
        self.assertEqual(trade.price, 100.0)
        self.assertEqual(trade.buy_order.order_id, "B1")
        self.assertEqual(trade.sell_order.order_id, "S1")

    def test_partial_match(self):
        """Test partial order matching"""
        # Add a large buy order
        buy_order = Order("B1", price=100.0, quantity=20, side=OrderSide.BUY)
        self.order_book.add_order(buy_order)

        # Add a smaller sell order
        sell_order = Order("S1", price=100.0, quantity=10, side=OrderSide.SELL)
        self.order_book.add_order(sell_order)

        # Execute matching
        trades = self.matching_engine.match_orders()

        # Verify partial fill
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].quantity, 10)
        self.assertEqual(buy_order.remaining_quantity, 10)
        self.assertEqual(sell_order.remaining_quantity, 0)
