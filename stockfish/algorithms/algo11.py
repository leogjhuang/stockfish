"""
Algorithm 11
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


class Algo11:
    """
    Trading a stable and trending market respectively.
    Monitor changes in the bid/ask prices and place limit orders accordingly.
    """
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20, "COCONUTS": 600, "PINA_COLADAS": 300}
        self.global_best_ask: Dict[Symbol, int] = {}
        self.global_best_bid: Dict[Symbol, int] = {}
        self.mid_prices: Dict[Symbol, List[int]] = {}

        #min num of data [buy, sell]
        self.coco_min_num_of_data = [9, 9]
        self.pina_min_num_of_data = [7, 7]

        #vwap data
        self.vwap_bid_prices = {}
        self.vwap_ask_prices = {}

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

            elif product == "COCONUTS" or product == "PINA_COLADAS":
                best_ask, best_ask_volume = get_best_ask(order_depth)
                best_bid, best_bid_volume = get_best_bid(order_depth)
                best_ask_volume = min(-best_ask_volume, buy_volume)
                best_bid_volume = min(best_bid_volume, sell_volume)

                if product == "COCONUTS":
                    min_num_of_data = self.coco_min_num_of_data
                else:
                    min_num_of_data = self.pina_min_num_of_data

                self.order_by_vwap(
                    product=product,
                    prices=self.vwap_bid_prices,
                    book=order_depth.buy_orders,
                    min_num_of_data=min_num_of_data[1],
                    order_condition=lambda : self.sell_signal(product, min_num_of_data[1]),
                    place_order_function=lambda : place_sell_order(product, orders, best_bid, best_bid_volume)
                )

                self.order_by_vwap(
                    product=product,
                    prices=self.vwap_ask_prices,
                    book=order_depth.sell_orders,
                    min_num_of_data=min_num_of_data[0],
                    order_condition=lambda : self.buy_signal(product, min_num_of_data[0]),
                    place_order_function=lambda : place_buy_order(product, orders, best_ask, best_ask_volume)
                )

            result[product] = orders

        return result

    def sell_signal(self, product, min_num_of_data):
        vwaps = self.vwap_bid_prices[product]
        return vwaps[-1] < vwaps[-2] and is_increasing(vwaps[-1-min_num_of_data:-1])

    def buy_signal(self, product, min_num_of_data):
        vwaps = self.vwap_ask_prices[product]
        return vwaps[-1] > vwaps[-2] and is_decreasing(vwaps[-1-min_num_of_data:-1])

    def order_by_vwap(self, product, prices, 
                      book,
                      min_num_of_data,
                      order_condition, 
                      place_order_function):
        self.init_list(product, prices)
        prices[product].append(get_vwap(book))
        if self.not_enough_data(product, prices, min_num_of_data):
            return
        if order_condition():
            place_order_function()

    def init_list(self, product, lst):
        if product not in lst:
            lst[product] = []
    
    def not_enough_data(self, product, prices, min_num_of_data):
        return len(prices[product]) <= min_num_of_data

    
