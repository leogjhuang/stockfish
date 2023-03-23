"""
Algorithm 10
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
    get_best_bid
)


class Algo10:
    """
    Trading a stable and trending market respectively.
    Monitor changes in the bid/ask prices and place limit orders accordingly.
    """
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20, "COCONUTS": 600, "PINA_COLADAS": 300}
        self.global_best_ask: Dict[Symbol, int] = {}
        self.global_best_bid: Dict[Symbol, int] = {}
        self.mid_prices: Dict[Symbol, List[int]] = {}

        #vwap data
        self.ask_price = {}
        self.bid_price = {}
        self.vwap_bid_prices = {}
        self.vwap_ask_prices = {}
        self.mid_prices = {}

        # moving average data
        self.large_ask_averages = {}
        self.small_ask_averages = {}
        self.large_bid_averages = {}
        self.small_bid_averages = {}
        self.window_size_small = 5
        self.window_size_large = 8

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

            elif product == "BANANAS":
                if product not in self.mid_prices:
                    self.mid_prices[product] = []
                if get_mid_price(order_depth) is not None:
                    self.mid_prices[product].append(get_mid_price(order_depth))
                if len(self.mid_prices[product]) > 0 and len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], 5)
                    spread = get_spread(order_depth)
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread / 3), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread / 3), sell_volume)

            else:
                test_threshold = 5
                # best_ask, best_ask_volume = get_best_ask(order_depth)
                # best_bid, best_bid_volume = get_best_bid(order_depth)
                # best_ask_volume = min(-best_ask_volume, buy_volume)
                # best_bid_volume = min(best_bid_volume, sell_volume)
                # self.ask_price[product] = min(self.ask_price.get(product, best_ask), best_ask)
                # self.bid_price[product] = max(self.bid_price.get(product, best_bid), best_bid)
                self.init_list(product, self.mid_prices)
                self.mid_prices[product].append(get_mid_price(order_depth))
                acceptable_price = get_moving_average(self.mid_prices[product], test_threshold)
                spread = get_spread(order_depth)

                self.order_by_vwap(
                    product=product,
                    prices=self.vwap_bid_prices,
                    large_averages=self.large_bid_averages,
                    small_averages=self.small_bid_averages,
                    book=order_depth.buy_orders,
                    order_condition=lambda : self.sell_signal(product),
                    place_order_function=lambda : place_sell_order(product, orders, math.floor(acceptable_price + spread / 2), sell_volume)
                )

                self.order_by_vwap(
                    product=product,
                    prices=self.vwap_ask_prices,
                    large_averages=self.large_ask_averages,
                    small_averages=self.small_ask_averages,
                    book=order_depth.sell_orders,
                    order_condition=lambda : self.buy_signal(product),
                    place_order_function=lambda : place_buy_order(product, orders, math.ceil(acceptable_price - spread / 2), buy_volume)
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
