from typing import List, Tuple, Optional
from .order_book import OrderBook
from .order import Order, OrderSide
import logging


class Trade:
    def __init__(self, buy_order: Order, sell_order: Order,
                 price: float, quantity: int):
        self.buy_order = buy_order
        self.sell_order = sell_order
        self.price = price
        self.quantity = quantity


class MatchingEngine:
    def __init__(self, order_book: OrderBook):
        self.order_book = order_book
        self.logger = logging.getLogger(__name__)

    def match_orders(self) -> List[Trade]:
        trades = []

        while True:
            best_bid = self.order_book.get_best_bid()
            best_ask = self.order_book.get_best_ask()

            if not (best_bid and best_ask and best_bid >= best_ask):
                break

            bid_orders = self.order_book.bids[best_bid]
            ask_orders = self.order_book.asks[best_ask]

            if not (bid_orders and ask_orders):
                break

            trade = self._match_orders_at_price(bid_orders[0], ask_orders[0])
            if trade:
                trades.append(trade)

            # Clean up filled orders
            self._cleanup_filled_orders()

        return trades

    def _match_orders_at_price(self, bid: Order, ask: Order) -> Optional[Trade]:
        quantity = min(bid.remaining_quantity, ask.remaining_quantity)
        price = ask.price  # Using ask price for this example

        bid.filled_quantity += quantity
        ask.filled_quantity += quantity

        self.logger.info(
            f"Matched: {bid.order_id} with {ask.order_id} "
            f"at {price} x {quantity}"
        )

        return Trade(bid, ask, price, quantity)

    def _cleanup_filled_orders(self):
        for order_dict in [self.order_book.bids, self.order_book.asks]:
            for price in list(order_dict.keys()):
                order_dict[price] = [
                    order for order in order_dict[price]
                    if not order.is_filled
                ]
                if not order_dict[price]:
                    del order_dict[price]
