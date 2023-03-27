"""
Algorithm 16
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
    PEARLS,
    BANANAS,
    COCONUTS,
    PINA_COLADAS,
    DIVING_GEAR,
    BERRIES,
    DOLPHIN_SIGHTINGS,
    BAGUETTE,
    DIP,
    UKELELE,
    PICNIC_BASKET,
)


class Algo16:
    """
    Using stable, trending, correlated, lead-lag, seasonal, and ETF strategies to trade.
    """
    def __init__(self):
        self.position_limit = {
            PEARLS: 20,
            BANANAS: 20,
            COCONUTS: 600,
            PINA_COLADAS: 300,
            DIVING_GEAR: 50,
            BERRIES: 250,
            BAGUETTE: 150,
            DIP: 300,
            UKELELE: 70,
            PICNIC_BASKET: 70}
        self.spread_coefficient = {PEARLS: 0.4, BANANAS: 0.35, BERRIES: 0.3}
        self.moving_average_window = {PEARLS: 5, BANANAS: 5, BERRIES: 5, DOLPHIN_SIGHTINGS: 9}
        self.trend_length = {COCONUTS: 9, PINA_COLADAS: 7}
        self.vwap_ask_prices = {}
        self.vwap_bid_prices = {}
        self.mid_prices = {}
        self.dolphin_sightings_list = []
        self.dolphin_sightings_diff = []

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """"
        Entry point for the algorithm
        """
        result = {}

        if DOLPHIN_SIGHTINGS in state.observations:
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

            if product not in self.vwap_ask_prices:
                self.vwap_ask_prices[product] = []
            if product not in self.vwap_bid_prices:
                self.vwap_bid_prices[product] = []
            if product not in self.mid_prices:
                self.mid_prices[product] = []
            self.vwap_ask_prices[product].append(vwap_ask)
            self.vwap_bid_prices[product].append(vwap_bid)
            self.mid_prices[product].append(mid_price)

            if product == PEARLS:
                if len(self.mid_prices[product]) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], self.moving_average_window[product])
                    spread = get_spread(order_depth) * self.spread_coefficient[product]
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread), sell_volume)

            if product == BANANAS:
                if len(self.mid_prices[product]) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], self.moving_average_window[product])
                    spread = get_spread(order_depth) * self.spread_coefficient[product]
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread), sell_volume)

            if product == COCONUTS:
                if len(self.vwap_bid_prices[product]) > self.trend_length[product] and sell_signal(self.vwap_bid_prices[product], self.trend_length[product]):
                    place_sell_order(product, orders, best_bid, sell_volume)
                if len(self.vwap_ask_prices[product]) > self.trend_length[product] and buy_signal(self.vwap_ask_prices[product], self.trend_length[product]):
                    place_buy_order(product, orders, best_ask, buy_volume)

            if product == PINA_COLADAS:
                target_correlation = 1.8761
                mid_price_coco = get_mid_price(state.order_depths["COCONUTS"])
                actual_correlation = mid_price / mid_price_coco
                if actual_correlation < target_correlation and len(self.mid_prices["COCONUTS"]) >= 2 and self.mid_prices["COCONUTS"][-1] < self.mid_prices["COCONUTS"][-2]:
                    place_buy_order(product, orders, best_ask, buy_volume)
                if actual_correlation > target_correlation and len(self.mid_prices["COCONUTS"]) >= 2 and self.mid_prices["COCONUTS"][-1] > self.mid_prices["COCONUTS"][-2]:
                    place_sell_order(product, orders, best_bid, sell_volume)

            if product == BERRIES:
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

            if product == DIVING_GEAR:
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
