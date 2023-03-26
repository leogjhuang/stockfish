"""
Round 3
"""
import math
from typing import Dict, List
import numpy as np
from stockfish.datamodel import (
    Order, TradingState
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
    buy_signal,
    sell_signal,
)


class Algo15:
    """
    Round 3 PnL: 15024 (Pearls: 1233, Bananas: 1213, Coconuts: 3972, Pina Coladas: 1727, Diving Gear: 4057, Berries: 2822)
    Trading a stable, trending, correlated, lead-lag, and seasonal asset respectively.
    """
    def __init__(self):
        self.pearls = "PEARLS"
        self.bananas = "BANANAS"
        self.coconuts = "COCONUTS"
        self.pina_coladas = "PINA_COLADAS"
        self.diving_gear = "DIVING_GEAR"
        self.berries = "BERRIES"
        self.dolphin_sightings = "DOLPHIN_SIGHTINGS"

        self.position_limit = {self.pearls: 20, self.bananas: 20, self.coconuts: 600, self.pina_coladas: 300, self.diving_gear: 50, self.berries: 250}
        self.spread_coefficient = {self.pearls: 0.4, self.bananas: 0.35, self.berries: 0.3}
        self.moving_average_window = {self.pearls: 5, self.bananas: 5, self.berries: 5, self.dolphin_sightings: 9}
        self.trend_length = {self.coconuts: 9, self.pina_coladas: 7}
        self.mid_prices = {self.pearls: [], self.bananas: [], self.coconuts: [], self.pina_coladas: [], self.diving_gear: [], self.berries: []}
        self.vwap_bid_prices = {self.pearls: [], self.bananas: [], self.coconuts: [], self.pina_coladas: [], self.diving_gear: [], self.berries: []}
        self.vwap_ask_prices = {self.pearls: [], self.bananas: [], self.coconuts: [], self.pina_coladas: [], self.diving_gear: [], self.berries: []}
        self.correlation = {self.pearls: 0, self.bananas: 0, self.coconuts: 0, self.pina_coladas: 1.9, self.diving_gear: 0, self.berries: 0}
        self.dolphin_sightings_list = []
        self.dolphin_sightings_diff = []

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """"
        Entry point for the algorithm
        """
        result = {}

        if self.dolphin_sightings in state.observations:
            self.dolphin_sightings_list.append(state.observations[self.dolphin_sightings])

        if len(self.dolphin_sightings_list) > 1:
            self.dolphin_sightings_diff.append(self.dolphin_sightings_list[-1] - self.dolphin_sightings_list[-2])

        for product, order_depth in sorted(state.order_depths.items()):
            orders: list[Order] = []

            position = state.position.get(product, 0)
            buy_volume = self.position_limit.get(product, 0) - position
            sell_volume = self.position_limit.get(product, 0) + position
            best_ask, _ = get_best_ask(order_depth)
            best_bid, _ = get_best_bid(order_depth)
            vwap_ask = get_vwap_ask(order_depth)
            vwap_bid = get_vwap_bid(order_depth)
            mid_price = get_mid_price(order_depth)
            self.vwap_bid_prices[product].append(vwap_bid)
            self.vwap_ask_prices[product].append(vwap_ask)
            self.mid_prices[product].append(mid_price)

            if product == self.pearls:
                if len(self.mid_prices[product]) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], self.moving_average_window[product])
                    spread = get_spread(order_depth) * self.spread_coefficient[product]
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread), sell_volume)

            if product == self.bananas:
                if len(self.mid_prices[product]) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], self.moving_average_window[product])
                    spread = get_spread(order_depth) * self.spread_coefficient[product]
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread), sell_volume)

            if product == self.coconuts:
                if len(self.vwap_bid_prices[product]) > self.trend_length[product] and sell_signal(self.vwap_bid_prices[product], self.trend_length[product]):
                    place_sell_order(product, orders, best_bid, sell_volume)
                if len(self.vwap_ask_prices[product]) > self.trend_length[product] and buy_signal(self.vwap_ask_prices[product], self.trend_length[product]):
                    place_buy_order(product, orders, best_ask, buy_volume)

            if product == self.pina_coladas:
                target_correlation = 1.8761
                mid_price_coco = get_mid_price(state.order_depths["COCONUTS"])
                actual_correlation = mid_price / mid_price_coco
                if actual_correlation < target_correlation and len(self.mid_prices["COCONUTS"]) >= 2 and self.mid_prices["COCONUTS"][-1] < self.mid_prices["COCONUTS"][-2]:
                    place_buy_order(product, orders, best_ask, buy_volume)
                if actual_correlation > target_correlation and len(self.mid_prices["COCONUTS"]) >= 2 and self.mid_prices["COCONUTS"][-1] > self.mid_prices["COCONUTS"][-2]:
                    place_sell_order(product, orders, best_bid, sell_volume)

            if product == self.berries:
                peak_start = 450000
                trend_coefficient = 0.5
                if state.timestamp <= peak_start:
                    if len(self.mid_prices[product]) > 0:
                        acceptable_price = get_moving_average(self.mid_prices[product], self.moving_average_window[product])
                        spread = get_spread(order_depth) * self.spread_coefficient[product]
                        place_buy_order(product, orders, math.ceil(acceptable_price - spread * (1 - trend_coefficient)), buy_volume)
                        place_sell_order(product, orders, math.floor(acceptable_price + spread * (1 + trend_coefficient)), sell_volume)
                else:
                    if len(self.mid_prices[product]) > 0:
                        acceptable_price = get_moving_average(self.mid_prices[product], self.moving_average_window[product])
                        spread = get_spread(order_depth) * self.spread_coefficient[product]
                        place_buy_order(product, orders, math.ceil(acceptable_price - spread * (1 + trend_coefficient)), buy_volume)
                        place_sell_order(product, orders, math.floor(acceptable_price + spread * (1 - trend_coefficient)), sell_volume)

            if product == self.diving_gear:
                window = self.moving_average_window[self.dolphin_sightings]
                volatility_coefficient = 2.5
                if len(self.dolphin_sightings_diff) >= window:
                    volatility = np.std(self.dolphin_sightings_diff[-window:])
                    upper_bound = np.mean(self.dolphin_sightings_diff[-window:]) + volatility * volatility_coefficient
                    lower_bound = np.mean(self.dolphin_sightings_diff[-window:]) - volatility * volatility_coefficient
                    if self.dolphin_sightings_diff[-1] > upper_bound:
                        place_sell_order(product, orders, best_bid, sell_volume)
                    elif self.dolphin_sightings_diff[-1] < lower_bound:
                        place_buy_order(product, orders, best_ask, buy_volume)

            result[product] = orders

        return result
