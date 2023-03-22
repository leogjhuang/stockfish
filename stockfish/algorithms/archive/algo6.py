from typing import Dict, List
from datamodel import Order, TradingState
from stockfish.utils import place_buy_order, place_sell_order, get_best_ask, get_best_bid, place_buy_orders_up_to, place_sell_orders_up_to


class Algo6:
    """
    Trading a stable market.
    Submit 40 buy orders at the lowest known ask price and 40 sell orders at the highest known bid price.
    """
    def __init__(self):
        self.product = "PEARLS"
        self.best_ask = 9998
        self.mid_price = 10000
        self.best_bid = 10002
        self.position_limit = 20

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}
        position_threshold = 15
        orders: list[Order] = []
        position = state.position.get(self.product, 0)
        order_depth = state.order_depths[self.product]
        if position < -position_threshold:
            place_buy_orders_up_to(self.product, orders, -position - position_threshold, order_depth)
        else:
            place_buy_order(self.product, orders, self.best_ask, self.position_limit - position)
        # if position > position_threshold:
        #     place_sell_orders_up_to(self.product, orders, position - position_threshold, order_depth)
        # else:
        place_sell_order(self.product, orders, self.best_bid, self.position_limit + position)
        result[self.product] = orders
        return result
