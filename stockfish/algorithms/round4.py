"""
Round 4
"""
from typing import Dict, List
from stockfish.datamodel import (
    Order, TradingState
)
from stockfish.utils import (
    get_moving_average,
    get_mid_price,
    place_buy_order,
    place_sell_order,
    get_best_ask,
    get_best_bid,
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
    PICNIC_BASKET,
)


class Round4:
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
            UKULELE: 70,
            PICNIC_BASKET: 70
        }
        self.mid_prices = {}
        self.observations = {}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """"
        Entry point for the algorithm
        """
        result = {}

        for product in state.observations:
            if product not in self.observations:
                self.observations[product] = []
            self.observations[product].append(state.observations[product])

        for product, order_depth in sorted(state.order_depths.items()):
            orders: list[Order] = []

            position = state.position.get(product, 0)
            buy_volume = self.position_limit.get(product, 0) - position
            sell_volume = self.position_limit.get(product, 0) + position
            best_ask, _ = get_best_ask(order_depth)
            best_bid, _ = get_best_bid(order_depth)
            mid_price = get_mid_price(order_depth)

            if product not in self.mid_prices:
                self.mid_prices[product] = []
            self.mid_prices[product].append(mid_price)

            if product == PEARLS:
                place_buy_order(product, orders, 9999, buy_volume)
                place_sell_order(product, orders, 10001, sell_volume)

            if product == BANANAS:
                acceptable_price = get_moving_average(self.mid_prices[product], 3)
                place_buy_order(product, orders, acceptable_price - 1, buy_volume)
                place_sell_order(product, orders, acceptable_price + 1, sell_volume)

            if product == PINA_COLADAS:
                expected_correlation = 1.878
                if len(self.mid_prices[COCONUTS]) > 1:
                    actual_correlation = mid_price / self.mid_prices[COCONUTS][-1]
                    if actual_correlation < expected_correlation and self.mid_prices[COCONUTS][-1] < self.mid_prices[COCONUTS][-2]:
                        place_buy_order(product, orders, mid_price, buy_volume)
                    if actual_correlation > expected_correlation and self.mid_prices[COCONUTS][-1] > self.mid_prices[COCONUTS][-2]:
                        place_sell_order(product, orders, mid_price, sell_volume)

            if product == BERRIES:
                if position != self.position_limit[product] and state.timestamp >= 123000 and state.timestamp <= 200000:
                    place_buy_order(product, orders, best_ask, buy_volume)
                if position != -self.position_limit[product] and state.timestamp >= 498000:
                    place_sell_order(product, orders, best_bid, sell_volume)

            if product == DIVING_GEAR:
                change_threshold = 8
                if len(self.observations[DOLPHIN_SIGHTINGS]) > 1:
                    change = self.observations[DOLPHIN_SIGHTINGS][-1] - self.observations[DOLPHIN_SIGHTINGS][-2]
                    if change >= change_threshold:
                        place_buy_order(product, orders, best_ask, buy_volume)
                    if change <= -change_threshold:
                        place_sell_order(product, orders, best_bid, sell_volume)

            result[product] = orders

        return result
