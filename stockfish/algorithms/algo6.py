from typing import Dict, List
from datamodel import Order, TradingState
from utils import *


class Algo6:
    """
    Trading a stable market.
    Submit 40 buy orders at the lowest known ask price and 40 sell orders at the highest known bid price.
    """
    def __init__(self):
        self.product = "PEARLS"
        self.best_ask = 9998
        self.best_bid = 10002
        self.position_limit = 20

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}
        orders: list[Order] = []
        position = state.position.get(self.product, 0)
        place_buy_order(self.product, orders, self.best_ask, self.position_limit - position)
        place_sell_order(self.product, orders, self.best_bid, self.position_limit + position)
        result[self.product] = orders
        return result
