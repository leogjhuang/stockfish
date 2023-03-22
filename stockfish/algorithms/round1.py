"""
Round 1
"""
import math
from typing import Dict, List
from stockfish.datamodel import (
    Order, Symbol, TradingState
)
from stockfish.utils import (
    get_moving_average,
    get_mid_price,
    get_spread,
    place_buy_order,
    place_sell_order,
)


class Round1:
    """
    Round 1 PnL: 2680 (Pearls: 1354, Bananas: 1326)
    Trading a stable and trending market respectively.
    Monitor changes in the bid/ask prices and place limit orders accordingly.
    """
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20}
        self.global_best_ask: Dict[Symbol, int] = {}
        self.global_best_bid: Dict[Symbol, int] = {}
        self.mid_prices: Dict[Symbol, List[int]] = {}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """"
        Entry point for the algorithm
        """
        result = {}

        for product, order_depth in state.order_depths.items():
            orders: list[Order] = []

            position = state.position.get(product, 0)
            buy_volume = self.position_limit.get(product, 0) - position
            sell_volume = self.position_limit.get(product, 0) + position

            if product == "PEARLS":
                if product not in self.mid_prices:
                    self.mid_prices[product] = []
                if get_mid_price(order_depth) is not None:
                    self.mid_prices[product].append(get_mid_price(order_depth))
                if len(self.mid_prices[product]) > 0 and len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], 5)
                    spread = get_spread(order_depth)
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread / 2.5), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread / 2.5), sell_volume)

            if product == "BANANAS":
                if product not in self.mid_prices:
                    self.mid_prices[product] = []
                if get_mid_price(order_depth) is not None:
                    self.mid_prices[product].append(get_mid_price(order_depth))
                if len(self.mid_prices[product]) > 0 and len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], 5)
                    spread = get_spread(order_depth)
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread / 3), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread / 3), sell_volume)

            result[product] = orders

        return result
