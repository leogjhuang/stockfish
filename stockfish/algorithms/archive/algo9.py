"""
Algorithm 9
"""

from typing import Dict, List
from datamodel import Order, TradingState
from stockfish.utils import *


class Algo9:
    """
    Trading a stable and trending market respectively by comparing two different moving averages.
    Monitor changes in the bid/ask prices and place limit orders accordingly.
    """
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20}
        self.ask_price = {}
        self.bid_price = {}
        self.vwap_bid_prices = {}
        self.vwap_ask_prices = {}

        # moving average data
        self.large_ask_averages = {}
        self.small_ask_averages = {}
        self.large_bid_averages = {}
        self.small_bid_averages = {}
        self.window_size_small = 500
        self.window_size_large = 2000

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
                    large_averages=self.large_bid_averages,
                    small_averages=self.small_bid_averages,
                    book=order_depth.buy_orders,
                    order_condition=lambda : self.sell_signal(product),
                    place_order_function=lambda : place_sell_order(product, orders, best_bid, best_bid_volume)
                )

                self.order_by_vwap(
                    product=product,
                    prices=self.vwap_ask_prices,
                    large_averages=self.large_ask_averages,
                    small_averages=self.small_ask_averages,
                    book=order_depth.sell_orders,
                    order_condition=lambda : self.buy_signal(product),
                    place_order_function=lambda : place_buy_order(product, orders, best_ask, best_ask_volume)
                )

            result[product] = orders

        return result

    def sell_signal(self, product):
        large_averages = self.large_bid_averages[product]
        small_averages = self.small_bid_averages[product]
        if len(large_averages) < self.window_size_small:
            return False
        cur_roc_large, cur_roc_small, past_roc_large, past_roc_small = self.get_crossover_data(large_averages, small_averages)
        return cur_roc_large > cur_roc_small and past_roc_large < past_roc_small

    def buy_signal(self, product):
        large_averages = self.large_ask_averages[product]
        small_averages = self.small_ask_averages[product]
        if len(large_averages) < self.window_size_small:
            return False
        cur_roc_large, cur_roc_small, past_roc_large, past_roc_small = self.get_crossover_data(large_averages, small_averages)
        return cur_roc_large < cur_roc_small and past_roc_large > past_roc_small

    def get_crossover_data(self, large_averages, small_averages):
        cur_roc_large = large_averages[-1]
        cur_roc_small = small_averages[-1]
        past_roc_large = large_averages[-2]
        past_roc_small = small_averages[-2]
        return cur_roc_large, cur_roc_small, past_roc_large, past_roc_small  

    def get_roc_data(self, large_averages, small_averages):
        cur_roc_large = self.get_average_roc(large_averages)
        cur_roc_small = self.get_average_roc(small_averages)
        past_roc_large = self.get_average_roc(large_averages[:-1])
        past_roc_small = self.get_average_roc(small_averages[:-1])
        return cur_roc_large, cur_roc_small, past_roc_large, past_roc_small 

    def get_average_roc(self, data):
        roc = []
        for i in range(1, len(data)):
            new_val = data[i]
            old_val = data[i-1]
            rate = (new_val - old_val) / old_val * 100
            roc.append(rate)
        return sum(roc) / len(roc)

    def order_by_vwap(self, product, prices, 
                      large_averages, 
                      small_averages, 
                      book, 
                      order_condition, 
                      place_order_function):
        self.init_list(product, prices)
        self.init_list(product, large_averages)
        self.init_list(product, small_averages)
        prices[product].append(get_vwap(book))
        if self.not_enough_data(product, prices):
            return
        large_averages[product].append(get_moving_average(prices[product], self.window_size_large))
        small_averages[product].append(get_moving_average(prices[product], self.window_size_small))
        if order_condition():
            place_order_function()

    def init_list(self, product, lst):
        if product not in lst:
            lst[product] = []
    
    def not_enough_data(self, product, prices):
        return len(prices[product]) < self.window_size_large

    
