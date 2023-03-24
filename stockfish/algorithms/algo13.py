"""
Algorithm 13
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
    get_vwap,
    get_best_ask,
    get_best_bid,
    is_increasing,
    is_decreasing
)


class Algo13:
    """
    Trading a trending market by analyzing how long the trend has been going on.
    """
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20, "COCONUTS": 600, "PINA_COLADAS": 300}
        self.mid_prices: Dict[Symbol, List[int]] = {}
        self.trend_length = {"PEARLS": 5, "BANANAS": 5, "COCONUTS": 5, "PINA_COLADAS": 5}
        self.spread_threshold = {"PEARLS": 0.1, "BANANAS": 0.1428, "COCONUTS": 0.5, "PINA_COLADAS": 0.5}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Entry point for the algorithm
        """
        result = {}

        for product, order_depth in state.order_depths.items():
            orders: list[Order] = []

            position = state.position.get(product, 0)
            buy_volume = self.position_limit.get(product, 0) - position
            sell_volume = self.position_limit.get(product, 0) + position
            best_ask, best_ask_volume = get_best_ask(order_depth)
            best_bid, best_bid_volume = get_best_bid(order_depth)

            if product == "PEARLS":
                if product not in self.mid_prices:
                    self.mid_prices[product] = []
                if get_mid_price(order_depth) is not None:
                    self.mid_prices[product].append(get_mid_price(order_depth))
                if len(self.mid_prices[product]) > 0 and len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], 5)
                    difference = get_spread(order_depth) * self.spread_threshold[product]
                    place_buy_order(product, orders, math.ceil(acceptable_price - difference), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + difference), sell_volume)

            if product == "BANANAS":
                if product not in self.mid_prices:
                    self.mid_prices[product] = []
                if get_mid_price(order_depth) is not None:
                    self.mid_prices[product].append(get_mid_price(order_depth))
                if len(self.mid_prices[product]) > 0 and len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], 5)
                    difference = get_spread(order_depth) * self.spread_threshold[product]
                    place_buy_order(product, orders, math.ceil(acceptable_price - difference), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + difference), sell_volume)

            if product == "COCONUTS":
                if product not in self.mid_prices:
                    self.mid_prices[product] = []
                if get_mid_price(order_depth) is not None:
                    self.mid_prices[product].append(get_mid_price(order_depth))
                if len(self.mid_prices[product]) > 0 and len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], 5)
                    difference = get_spread(order_depth) * self.spread_threshold[product]
                    place_buy_order(product, orders, math.ceil(acceptable_price - difference), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + difference), sell_volume)

            if product == "PINA_COLADAS":
                if product not in self.mid_prices:
                    self.mid_prices[product] = []
                if get_mid_price(order_depth) is not None:
                    self.mid_prices[product].append(get_mid_price(order_depth))
                if len(self.mid_prices[product]) > 0 and len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], 5)
                    difference = get_spread(order_depth) * self.spread_threshold[product]
                    place_buy_order(product, orders, math.ceil(acceptable_price - difference), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + difference), sell_volume)

            # if product == "COCONUTS" or product == "PINA_COLADAS":
            #     if product not in self.mid_prices:
            #         self.mid_prices[product] = []
            #     if get_mid_price(order_depth) is not None:
            #         self.mid_prices[product].append(get_mid_price(order_depth))
            #     if len(self.mid_prices[product]) > self.trend_length[product] and len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
            #         acceptable_price = get_moving_average(self.mid_prices[product], 5)
            #         if self.is_decreasing(self.mid_prices[product], self.trend_length[product]):
            #             place_buy_order(product, orders, best_ask, min(buy_volume, best_ask_volume))
            #         if self.is_increasing(self.mid_prices[product], self.trend_length[product]):
            #             place_sell_order(product, orders, best_bid, min(sell_volume, best_bid_volume))

            result[product] = orders

        return result

    def is_decreasing(self, data: List[int], trend_length: int) -> bool:
        """
        Check if the data is decreasing
        """
        return sum(x > y for x, y in zip(data[-trend_length:], data[-trend_length - 1:-1])) >= trend_length - 2


    def is_increasing(self, data: List[int], trend_length: int) -> bool:
        """
        Check if the data is increasing
        """
        return sum(x < y for x, y in zip(data[-trend_length:], data[-trend_length - 1:-1])) >= trend_length - 2
