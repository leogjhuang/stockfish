"""
Algorithm 8
"""

from typing import Dict, List
from datamodel import Order, TradingState
from stockfish.utils import *


class Algo8:
    """
    Algo7 but gets moving average of VWAP rather than mid price of best ask and bid prices.
    Monitor changes in the bid/ask prices and place limit orders accordingly.
    """
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20}
        self.ask_price = {}
        self.bid_price = {}
        self.vwap_bid_prices = {}
        self.vwap_ask_prices = {}
        self.acceptable_ask_price = {}
        self.acceptable_bid_price = {}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """"
        Main entry point for the algorithm
        """
        result = {}

        for product, order_depth in state.order_depths.items():
            orders: list[Order] = []
            position = state.position.get(product, 0)
            position_limit = self.position_limit.get(product, 0)
            buy_volume = position_limit - position
            sell_volume = position_limit + position
            best_ask, best_ask_volume = get_best_ask(order_depth)
            best_bid, best_bid_volume = get_best_bid(order_depth)
            best_ask_volume = min(-best_ask_volume, buy_volume)
            best_bid_volume = min(best_bid_volume, sell_volume)
            self.ask_price[product] = min(self.ask_price.get(product, best_ask), best_ask)
            self.bid_price[product] = max(self.bid_price.get(product, best_bid), best_bid)

            if product == "PEARLS":
                if self.ask_price[product] < self.bid_price[product]:
                    place_buy_order(product, orders, self.ask_price[product], buy_volume)
                    place_sell_order(product, orders, self.bid_price[product], sell_volume)
            elif product == "BANANAS":
                self.order_by_vwap(
                    product=product,
                    prices=self.vwap_bid_prices,
                    acceptable_price=self.acceptable_bid_price,
                    book=order_depth.buy_orders,
                    window_size=5,
                    order_condition=lambda : best_bid > self.acceptable_bid_price[product],
                    place_order_function=lambda : place_sell_order(product, orders, best_bid, best_bid_volume)
                )

                self.order_by_vwap(
                    product=product,
                    prices=self.vwap_ask_prices,
                    acceptable_price=self.acceptable_ask_price,
                    book=order_depth.sell_orders,
                    window_size=5,
                    order_condition=lambda : best_ask < self.acceptable_ask_price[product],
                    place_order_function=lambda : place_buy_order(product, orders, best_ask, best_ask_volume)
                )

            result[product] = orders

        return result

    def order_by_vwap(self, product, prices, 
                      acceptable_price, book, 
                      window_size, order_condition, 
                      place_order_function):
        if product not in prices:
            prices[product] = []
        prices[product].append(get_vwap(book))
        acceptable_price[product] = get_moving_average(prices[product], window_size)
        if order_condition():
            place_order_function()
    
