"""
Algorithm 15
"""
import math
import numpy as np
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
        self.spread_coefficient = {self.PEARLS: 0.4, self.BANANAS: 0.35, self.COCONUTS: 0, self.PINA_COLADAS: 0, self.DIVING_GEAR: 0, self.BERRIES: 0.3}
        self.trend_coefficient = {self.PEARLS: 0.0, self.BANANAS: 0.0, self.COCONUTS: 0, self.PINA_COLADAS: 0, self.DIVING_GEAR: 0, self.BERRIES: 0.5}
        self.moving_average_window = {self.PEARLS: 5, self.BANANAS: 5, self.COCONUTS: 0, self.PINA_COLADAS: 0, self.DIVING_GEAR: 0, self.BERRIES: 5}
        self.trend_length = {self.PEARLS: 0, self.BANANAS: 0, self.COCONUTS: 8, self.PINA_COLADAS: 8, self.DIVING_GEAR: 0, self.BERRIES: 0}
        self.mid_prices = {self.PEARLS: [], self.BANANAS: [], self.COCONUTS: [], self.PINA_COLADAS: [], self.DIVING_GEAR: [], self.BERRIES: []}
        self.bid_prices = {self.PEARLS: [], self.BANANAS: [], self.COCONUTS: [], self.PINA_COLADAS: [], self.DIVING_GEAR: [], self.BERRIES: []}
        self.ask_prices = {self.PEARLS: [], self.BANANAS: [], self.COCONUTS: [], self.PINA_COLADAS: [], self.DIVING_GEAR: [], self.BERRIES: []}
        self.vwap_bid_prices = {self.PEARLS: [], self.BANANAS: [], self.COCONUTS: [], self.PINA_COLADAS: [], self.DIVING_GEAR: [], self.BERRIES: []}
        self.vwap_ask_prices = {self.PEARLS: [], self.BANANAS: [], self.COCONUTS: [], self.PINA_COLADAS: [], self.DIVING_GEAR: [], self.BERRIES: []}
        self.correlation = {self.PEARLS: 0, self.BANANAS: 0, self.COCONUTS: 0, self.PINA_COLADAS: 1.9, self.DIVING_GEAR: 0, self.BERRIES: 0}
        self.dolphin_sightings = []
        self.dolphin_sightings_diff = []
        self.dolphin_sightings_window = 9
        self.pair_trading_diff = []

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """"
        Entry point for the algorithm
        """
        result = {}

        if self.DOLPHIN_SIGHTINGS in state.observations:
            self.dolphin_sightings.append(state.observations[self.DOLPHIN_SIGHTINGS])

        if len(self.dolphin_sightings) > 1:
            self.dolphin_sightings_diff.append(self.dolphin_sightings[-1] - self.dolphin_sightings[-2])

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

            # if product == self.COCONUTS:
            #     if len(self.vwap_bid_prices[product]) > self.trend_length[product] and self.sell_signal(self.vwap_bid_prices[product], self.trend_length[product]):
            #         place_sell_order(product, orders, best_bid, sell_volume)
            #     if len(self.vwap_ask_prices[product]) > self.trend_length[product] and self.buy_signal(self.vwap_ask_prices[product], self.trend_length[product]):
            #         place_buy_order(product, orders, best_ask, buy_volume)

            if product == self.COCONUTS or product == self.PINA_COLADAS:
                if len(self.vwap_bid_prices[product]) > self.trend_length[product] and self.sell_signal(self.vwap_bid_prices[product], self.trend_length[product]):
                    place_sell_order(product, orders, best_bid, sell_volume)
                if len(self.vwap_ask_prices[product]) > self.trend_length[product] and self.buy_signal(self.vwap_ask_prices[product], self.trend_length[product]):
                    place_buy_order(product, orders, best_ask, buy_volume)

            # if product == self.PINA_COLADAS:
            #     mid_price_coco = get_mid_price(state.order_depths[self.COCONUTS])
            #     actual_correlation = mid_price / mid_price_coco
            #     target_correlation = self.correlation[product]
            #     if actual_correlation < target_correlation and len(self.mid_prices[self.COCONUTS]) >= 2 and self.mid_prices[self.COCONUTS][-1] < self.mid_prices[self.COCONUTS][-2]:
            #         place_buy_order(product, orders, best_ask, buy_volume)
            #     if actual_correlation > target_correlation and len(self.mid_prices[self.COCONUTS]) >= 2 and self.mid_prices[self.COCONUTS][-1] > self.mid_prices[self.COCONUTS][-2]:
            #         place_sell_order(product, orders, best_bid, sell_volume)

            # if product == self.PINA_COLADAS:
            #     x = np.array(self.mid_prices[self.COCONUTS])
            #     y = np.array(self.mid_prices[self.PINA_COLADAS])
            #     A = np.vstack([x, np.ones(len(x))]).T
            #     m, c = np.linalg.lstsq(A, y, rcond=None)[0]
            #     difference = self.mid_prices[self.COCONUTS][-1] - m * self.mid_prices[self.PINA_COLADAS][-1]
            #     self.pair_trading_diff.append(difference)
            #     mean = np.mean(self.pair_trading_diff)
            #     std = np.std(self.pair_trading_diff)
            #     z = (difference - mean) / std
            #     if z > 1:
            #         place_buy_order(self.PINA_COLADAS, orders, best_ask, buy_volume)
            #     elif z < -1:
            #         place_sell_order(self.PINA_COLADAS, orders, best_bid, sell_volume)
            #     elif abs(z) < 0.2:
            #         if position > 0:
            #             place_sell_order(self.PINA_COLADAS, orders, best_bid, position)
            #         elif position < 0:
            #             place_buy_order(self.PINA_COLADAS, orders, best_ask, -position)

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
                # if len(self.dolphin_sightings) > 50:
                #     avg_sightings = np.mean(self.dolphin_sightings[-50:])
                # else:
                #     avg_sightings = np.mean(self.dolphin_sightings)
                # if self.dolphin_sightings[-1] < avg_sightings - 3:
                #     place_buy_order(product, orders, best_ask, best_ask_volume)
                # if self.dolphin_sightings[-1] > avg_sightings + 3:
                #     place_sell_order(product, orders, best_bid, best_bid_volume)
                if len(self.dolphin_sightings_diff) >= self.dolphin_sightings_window:
                    volatility = np.std(self.dolphin_sightings_diff[-self.dolphin_sightings_window:])
                    upper_bound = np.mean(self.dolphin_sightings_diff[-self.dolphin_sightings_window:]) + volatility * 2.5
                    lower_bound = np.mean(self.dolphin_sightings_diff[-self.dolphin_sightings_window:]) - volatility * 2.5
                    if self.dolphin_sightings_diff[-1] > upper_bound:
                        place_sell_order(product, orders, best_bid, sell_volume)
                    elif self.dolphin_sightings_diff[-1] < lower_bound:
                        place_buy_order(product, orders, best_ask, buy_volume)

            result[product] = orders

        # coconut_orders = []
        # pina_colada_orders = []
        # coconut_position = state.position.get(self.COCONUTS, 0)
        # pina_colada_position = state.position.get(self.PINA_COLADAS, 0)
        # coconuts_order_depth = state.order_depths.get(self.COCONUTS, {})
        # pina_colada_order_depth = state.order_depths.get(self.PINA_COLADAS, {})
        # best_coconut_ask, best_coconut_ask_volume = get_best_ask(coconuts_order_depth)
        # best_coconut_bid, best_coconut_bid_volume = get_best_bid(coconuts_order_depth)
        # best_pina_colada_ask, best_pina_colada_ask_volume = get_best_ask(pina_colada_order_depth)
        # best_pina_colada_bid, best_pina_colada_bid_volume = get_best_bid(pina_colada_order_depth)

        # x = np.array(self.mid_prices[self.COCONUTS])
        # y = np.array(self.mid_prices[self.PINA_COLADAS])
        # A = np.vstack([x, np.ones(len(x))]).T
        # m, c = np.linalg.lstsq(A, y, rcond=None)[0]
        # difference = self.mid_prices[self.COCONUTS][-1] - m * self.mid_prices[self.PINA_COLADAS][-1] - c
        # self.pair_trading_diff.append(difference)
        # mean = np.mean(self.pair_trading_diff)
        # std = np.std(self.pair_trading_diff)
        # z = (difference - mean) / std
        # if z > 1:
        #     place_buy_order(self.PINA_COLADAS, pina_colada_orders, best_pina_colada_ask, best_pina_colada_ask_volume)
        #     place_sell_order(self.COCONUTS, coconut_orders, best_coconut_bid, best_coconut_bid_volume)
        # elif z < -1:
        #     place_buy_order(self.COCONUTS, coconut_orders, best_coconut_ask, best_coconut_ask_volume)
        #     place_sell_order(self.PINA_COLADAS, pina_colada_orders, best_pina_colada_bid, best_pina_colada_bid_volume)
        # elif abs(z) < 0.2:
        #     if coconut_position > 0:
        #         place_sell_order(self.COCONUTS, coconut_orders, best_coconut_bid, min(best_coconut_bid_volume, abs(coconut_position)))
        #     elif coconut_position < 0:
        #         place_buy_order(self.COCONUTS, coconut_orders, best_coconut_ask, min(best_coconut_ask_volume, abs(coconut_position)))
        #     if pina_colada_position > 0:
        #         place_sell_order(self.PINA_COLADAS, pina_colada_orders, best_pina_colada_bid, min(best_pina_colada_bid_volume, abs(pina_colada_position)))
        #     elif pina_colada_position < 0:
        #         place_buy_order(self.PINA_COLADAS, pina_colada_orders, best_pina_colada_ask, min(best_pina_colada_ask_volume, abs(pina_colada_position)))

        # result[self.COCONUTS] = coconut_orders
        # result[self.PINA_COLADAS] = pina_colada_orders

        return result

    def sell_signal(self, vwaps, min_num_of_data):
        return vwaps[-1] < vwaps[-2] and is_increasing(vwaps[-1-min_num_of_data:-1])

    def buy_signal(self, vwaps, min_num_of_data):
        return vwaps[-1] > vwaps[-2] and is_decreasing(vwaps[-1-min_num_of_data:-1])
