"""
Round 5
"""
from typing import Dict, List
from stockfish.constants import (
    PEARLS,
    BANANAS,
    COCONUTS,
    PINA_COLADAS,
    DIVING_GEAR,
    BERRIES,
    DOLPHIN_SIGHTINGS,
    BAGUETTE,
    DIP,
    UKULELE,
    PICNIC_BASKET
)
from stockfish.datamodel import Order, TradingState
from stockfish.logger import Logger
from stockfish.utils import (
    get_moving_average,
    get_mid_price,
    place_buy_order,
    place_sell_order
)


class Round5:
    """
    Using stable, trending, pairs, seasonal, and correlated strategies to trade.
    """
    def __init__(self):
        self.logger = Logger(local=True)
        self.position_limit = {
            PEARLS: 20,
            BANANAS: 20,
            COCONUTS: 600,
            PINA_COLADAS: 300,
            DIVING_GEAR: 50,
            BERRIES: 250,
            BAGUETTE: 150,
            DIP: 300,
            UKULELE: 70,
            PICNIC_BASKET: 70
        }
        self.mid_prices = {}
        self.last_observation = {}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        self.trade_stable(
            state,
            result,
            PEARLS,
            9999,
            10001
        )
        self.trade_trending(
            state,
            result,
            BANANAS,
            3
        )
        self.trade_pairs(
            state,
            result,
            PINA_COLADAS,
            COCONUTS,
            1.875,
            0.001
        )
        # TODO: Consider better time windows
        self.trade_seasonal(
            state,
            result,
            BERRIES,
            125000,
            200000,
            500000,
            575000
        )
        self.trade_correlated(
            state,
            result,
            DIVING_GEAR,
            DOLPHIN_SIGHTINGS,
            8
        )
        self.trade_etf(
            state,
            result,
            PICNIC_BASKET,
            {
                BAGUETTE: 2,
                DIP: 4,
                UKULELE: 1
            }
        )

        return result

    def trade_stable(self, state, result, product, ask_price, bid_price):
        if product not in state.order_depths:
            return
        if product not in result:
            result[product] = []
        position = state.position.get(product, 0)
        buy_volume = self.position_limit.get(product, 0) - position
        sell_volume = self.position_limit.get(product, 0) + position
        place_buy_order(product, result[product], ask_price, buy_volume)
        place_sell_order(product, result[product], bid_price, sell_volume)

    def trade_trending(self, state, result, product, window):
        if product not in state.order_depths:
            return
        if product not in result:
            result[product] = []
        if product not in self.mid_prices:
            self.mid_prices[product] = []
        self.mid_prices[product].append(get_mid_price(state.order_depths[product]))
        position = state.position.get(product, 0)
        buy_volume = self.position_limit.get(product, 0) - position
        sell_volume = self.position_limit.get(product, 0) + position
        acceptable_price = get_moving_average(self.mid_prices[product], window)
        place_buy_order(product, result[product], acceptable_price - 1, buy_volume)
        place_sell_order(product, result[product], acceptable_price + 1, sell_volume)

    def trade_pairs(self, state, result, product1, product2, correlation, tolerance):
        if product1 not in state.order_depths or product2 not in state.order_depths:
            return
        if product1 not in result:
            result[product1] = []
        if product2 not in result:
            result[product2] = []
        if product1 not in self.mid_prices:
            self.mid_prices[product1] = []
        if product2 not in self.mid_prices:
            self.mid_prices[product2] = []
        self.mid_prices[product1].append(get_mid_price(state.order_depths[product1]))
        self.mid_prices[product2].append(get_mid_price(state.order_depths[product2]))
        position1 = state.position.get(product1, 0)
        position2 = state.position.get(product2, 0)
        buy_volume1 = self.position_limit.get(product1, 0) - position1
        sell_volume1 = self.position_limit.get(product1, 0) + position1
        buy_volume2 = self.position_limit.get(product2, 0) - position2
        sell_volume2 = self.position_limit.get(product2, 0) + position2
        actual_correlation = self.mid_prices[product1][-1] / self.mid_prices[product2][-1]
        if len(self.mid_prices[product2]) > 1:
            if actual_correlation <= correlation - tolerance and self.mid_prices[product2][-1] < self.mid_prices[product2][-2]:
                place_buy_order(product1, result[product1], self.mid_prices[product1][-1], buy_volume1)
            if actual_correlation >= correlation + tolerance and self.mid_prices[product2][-1] > self.mid_prices[product2][-2]:
                place_sell_order(product1, result[product1], self.mid_prices[product1][-1], sell_volume1)
        # TODO: Add logic for trading second product

    def trade_seasonal(self, state, result, product, peak_start, peak_end, trough_start, trough_end):
        if product not in state.order_depths:
            return
        if product not in result:
            result[product] = []
        position = state.position.get(product, 0)
        buy_volume = self.position_limit.get(product, 0) - position
        sell_volume = self.position_limit.get(product, 0) + position
        mid_price = get_mid_price(state.order_depths[product])
        if buy_volume > 0 and state.timestamp >= peak_start and state.timestamp <= peak_end:
            place_buy_order(product, result[product], mid_price, buy_volume)
        if sell_volume > 0 and state.timestamp >= trough_start and state.timestamp <= trough_end:
            place_sell_order(product, result[product], mid_price, sell_volume)

    def trade_correlated(self, state, result, product, observation, change_threshold):
        if product not in state.order_depths or observation not in state.observations:
            return
        if product not in result:
            result[product] = []
        position = state.position.get(product, 0)
        buy_volume = self.position_limit.get(product, 0) - position
        sell_volume = self.position_limit.get(product, 0) + position
        mid_price = get_mid_price(state.order_depths[product])
        observation_value = state.observations[observation]
        if observation in self.last_observation:
            change = observation_value - self.last_observation[observation]
            # TODO: Check if trading at mid price is able to fill position to limit
            if change >= change_threshold:
                place_buy_order(product, result[product], mid_price, buy_volume)
            if change <= -change_threshold:
                place_sell_order(product, result[product], mid_price, sell_volume)
        self.last_observation[observation] = observation_value

    def trade_etf(self, state, result, etf, weights):
        if etf not in state.order_depths or any(product not in state.order_depths for product in weights):
            return
        if etf not in result:
            result[etf] = []
        position = state.position.get(etf, 0)
        buy_volume = self.position_limit.get(etf, 0) - position
        sell_volume = self.position_limit.get(etf, 0) + position
        mid_price = get_mid_price(state.order_depths[etf])
        etf_value = 0
        for product, weight in weights.items():
            etf_value += weight * get_mid_price(state.order_depths[product])
        if mid_price < etf_value - 400:
            place_buy_order(etf, result[etf], mid_price, buy_volume)
        if mid_price > etf_value + 400:
            place_sell_order(etf, result[etf], mid_price, sell_volume)
