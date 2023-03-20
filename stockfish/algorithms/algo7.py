"""
Algorithm 7
"""

from typing import Dict, List
from datamodel import Order, TradingState
from stockfish.utils import place_buy_order, place_sell_order, get_best_ask, get_best_bid, get_mid_price, get_moving_average


class Algo7:
    """
    Trading a trending market.
    Monitor changes in the bid/ask prices and place limit orders accordingly.
    """
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20}
        self.ask_price = {}
        self.bid_price = {}
        self.prices = {}
        self.acceptable_price = {}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """"
        Main entry point for the algorithm
        """
        result = {}

        for product, order_depth in state.order_depths.items():
            orders: list[Order] = []
            position = state.position.get(product, 0)
            buy_volume = self.position_limit.get(product, 0) - position
            sell_volume = self.position_limit.get(product, 0) + position
            best_ask, best_ask_volume = get_best_ask(order_depth)
            best_bid, best_bid_volume = get_best_bid(order_depth)
            self.ask_price[product] = min(self.ask_price.get(product, best_ask), best_ask)
            self.bid_price[product] = max(self.bid_price.get(product, best_bid), best_bid)

            if product == "PEARLS":
                if self.ask_price[product] < self.bid_price[product]:
                    place_buy_order(product, orders, self.ask_price[product], buy_volume)
                    place_sell_order(product, orders, self.bid_price[product], sell_volume)
            elif product == "BANANAS":
                best_ask_volume = min(-best_ask_volume, buy_volume)
                best_bid_volume = min(best_bid_volume, sell_volume)
                if product not in self.prices:
                    self.prices[product] = []
                self.prices[product].append(get_mid_price(order_depth))
                self.acceptable_price[product] = get_moving_average(self.prices[product], 5)
                if best_ask < self.acceptable_price[product]:
                    place_buy_order(product, orders, best_ask, best_ask_volume)
                if best_bid > self.acceptable_price[product]:
                    place_sell_order(product, orders, best_bid, best_bid_volume)

            result[product] = orders

        return result
