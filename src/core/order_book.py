from typing import Dict, List, Optional
from collections import defaultdict
from .order import Order, OrderSide
import logging


class OrderBook:
    def __init__(self):
        # Price level -> Orders at that price
        self.bids: Dict[float, List[Order]] = defaultdict(list)
        self.asks: Dict[float, List[Order]] = defaultdict(list)
        self.orders: Dict[str, Order] = {}  # Order ID -> Order
        self.logger = logging.getLogger(__name__)

    def add_order(self, order: Order) -> bool:
        if order.order_id in self.orders:
            self.logger.warning(f"Duplicate order ID: {order.order_id}")
            return False

        self.orders[order.order_id] = order
        order_dict = self.bids if order.side == OrderSide.BUY else self.asks
        order_dict[order.price].append(order)
        return True

    def cancel_order(self, order_id: str) -> Optional[Order]:
        if order_id not in self.orders:
            return None

        order = self.orders[order_id]
        order_dict = self.bids if order.side == OrderSide.BUY else self.asks

        if order.price in order_dict:
            order_dict[order.price].remove(order)
            if not order_dict[order.price]:
                del order_dict[order.price]

        del self.orders[order_id]
        return order

    def get_best_bid(self) -> Optional[float]:
        return max(self.bids.keys()) if self.bids else None

    def get_best_ask(self) -> Optional[float]:
        return min(self.asks.keys()) if self.asks else None
