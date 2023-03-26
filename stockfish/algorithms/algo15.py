"""
Algorithm 15
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
    get_vwap_bid,
    get_vwap_ask,
    get_best_ask,
    get_best_bid,
    is_increasing,
    is_decreasing
)


class Algo15:
    """
    Trading a stable and trending market respectively.
    Monitor changes in the bid/ask prices and place limit orders accordingly.
    """
    def __init__(self):
        self.PEARLS = "PEARLS"
        self.BANANAS = "BANANAS"
        self.COCONUTS = "COCONUTS"
        self.PINA_COLADAS = "PINA_COLADAS"
        self.DIVING_GEAR = "DIVING_GEAR"
        self.BERRIES = "BERRIES"
        self.DOLPHIN_SIGHTINGS = "DOLPHIN_SIGHTINGS"

        self.position_limit = {self.PEARLS: 20, self.BANANAS: 20, self.COCONUTS: 600, self.PINA_COLADAS: 300, self.DIVING_GEAR: 50, self.BERRIES: 250}
        self.spread_coefficient = {self.PEARLS: 0.4, self.BANANAS: 0.3, self.COCONUTS: 0.2, self.PINA_COLADAS: 0.1, self.DIVING_GEAR: 0.3, self.BERRIES: 0.45}
        self.trend_coefficient = {self.PEARLS: 0.0, self.BANANAS: 0.0, self.COCONUTS: 0.0, self.PINA_COLADAS: 0.0, self.DIVING_GEAR: 0.0, self.BERRIES: 0.5}
        self.moving_average_window = {self.PEARLS: 5, self.BANANAS: 5, self.COCONUTS: 1, self.PINA_COLADAS: 1, self.DIVING_GEAR: 5, self.BERRIES: 5}
        self.trend_length = {self.PEARLS: 0, self.BANANAS: 0, self.COCONUTS: 9, self.PINA_COLADAS: 7, self.DIVING_GEAR: 0, self.BERRIES: 0}
        self.mid_prices = {self.PEARLS: [], self.BANANAS: [], self.COCONUTS: [], self.PINA_COLADAS: [], self.DIVING_GEAR: [], self.BERRIES: []}
        self.vwap_bid_prices = {self.PEARLS: [], self.BANANAS: [], self.COCONUTS: [], self.PINA_COLADAS: [], self.DIVING_GEAR: [], self.BERRIES: []}
        self.vwap_ask_prices = {self.PEARLS: [], self.BANANAS: [], self.COCONUTS: [], self.PINA_COLADAS: [], self.DIVING_GEAR: [], self.BERRIES: []}
        self.correlation = {self.PEARLS: 0, self.BANANAS: 0, self.COCONUTS: 0, self.PINA_COLADAS: 1.875, self.DIVING_GEAR: 0, self.BERRIES: 0}
        self.dolphin_sightings = []

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """"
        Entry point for the algorithm
        """
        result = {}
        if self.DOLPHIN_SIGHTINGS in state.observations:
            self.dolphin_sightings.append(state.observations[self.DOLPHIN_SIGHTINGS])

        for product, order_depth in state.order_depths.items():
            orders: list[Order] = []

            position = state.position.get(product, 0)
            buy_volume = self.position_limit.get(product, 0) - position
            sell_volume = self.position_limit.get(product, 0) + position
            best_ask, best_ask_volume = get_best_ask(order_depth)
            best_bid, best_bid_volume = get_best_bid(order_depth)
            best_ask_volume = min(-1 * best_ask_volume, buy_volume)
            best_bid_volume = min(best_bid_volume, sell_volume)
            vwap_ask = get_vwap_ask(order_depth)
            vwap_bid = get_vwap_bid(order_depth)
            mid_price = get_mid_price(order_depth)
            self.vwap_bid_prices[product].append(vwap_bid)
            self.vwap_ask_prices[product].append(vwap_ask)
            self.mid_prices[product].append(mid_price)

            if product == self.PEARLS:
                if len(self.mid_prices[product]) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], self.moving_average_window[product])
                    spread = get_spread(order_depth) * self.spread_coefficient[product]
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread), sell_volume)

            if product == self.BANANAS:
                if len(self.mid_prices[product]) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], self.moving_average_window[product])
                    spread = get_spread(order_depth) * self.spread_coefficient[product]
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread), sell_volume)

            if product == self.COCONUTS or product == self.PINA_COLADAS:
                if len(self.vwap_bid_prices[product]) > self.trend_length[product] and self.sell_signal(self.vwap_bid_prices[product], self.trend_length[product]):
                    place_sell_order(product, orders, best_bid, best_bid_volume)
                if len(self.vwap_ask_prices[product]) > self.trend_length[product] and self.buy_signal(self.vwap_ask_prices[product], self.trend_length[product]):
                    place_buy_order(product, orders, best_ask, best_ask_volume)

            if product == self.BERRIES:
                if state.timestamp <= 450000:
                    if len(self.mid_prices[product]) > 0:
                        acceptable_price = get_moving_average(self.mid_prices[product], self.moving_average_window[product])
                        spread = get_spread(order_depth) * self.spread_coefficient[product]
                        place_buy_order(product, orders, math.ceil(acceptable_price - spread * (1 - self.trend_coefficient[product])), buy_volume)
                        place_sell_order(product, orders, math.floor(acceptable_price + spread * (1 + self.trend_coefficient[product])), sell_volume)
                else:
                    if len(self.mid_prices[product]) > 0:
                        acceptable_price = get_moving_average(self.mid_prices[product], self.moving_average_window[product])
                        spread = get_spread(order_depth) * self.spread_coefficient[product]
                        place_buy_order(product, orders, math.ceil(acceptable_price - spread * (1 + self.trend_coefficient[product])), buy_volume)
                        place_sell_order(product, orders, math.floor(acceptable_price + spread * (1 - self.trend_coefficient[product])), sell_volume)

            if product == self.DIVING_GEAR:
                pass

            result[product] = orders

        return result

    def sell_signal(self, vwaps, min_num_of_data):
        return vwaps[-1] < vwaps[-2] and is_increasing(vwaps[-1-min_num_of_data:-1])

    def buy_signal(self, vwaps, min_num_of_data):
        return vwaps[-1] > vwaps[-2] and is_decreasing(vwaps[-1-min_num_of_data:-1])
