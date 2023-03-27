import json
import math
import numpy as np
from typing import Any, Dict, List
from datamodel import Order, OrderDepth, ProsperityEncoder, Symbol, TradingState


class Trader:
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

            if product not in self.vwap_ask_prices:
                self.vwap_ask_prices[product] = []
            if product not in self.vwap_bid_prices:
                self.vwap_bid_prices[product] = []
            if product not in self.mid_prices:
                self.mid_prices[product] = []
            self.vwap_ask_prices[product].append(vwap_ask)
            self.vwap_bid_prices[product].append(vwap_bid)
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

        logger.flush(state, orders)
        return result


class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]]) -> None:
        print(json.dumps({
            "state": state,
            "orders": orders,
            "logs": self.logs,
        }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True))

        self.logs = ""

logger = Logger()


def get_best_bid(order_depth):
    """
    Returns the best bid and its volume
    """
    if len(order_depth.buy_orders) == 0:
        return None, None
    best_bid = max(order_depth.buy_orders)
    best_bid_volume = order_depth.buy_orders[best_bid]
    return best_bid, best_bid_volume


def get_best_ask(order_depth):
    """
    Returns the best ask and its volume
    """
    if len(order_depth.sell_orders) == 0:
        return None, None
    best_ask = min(order_depth.sell_orders)
    best_ask_volume = order_depth.sell_orders[best_ask]
    return best_ask, best_ask_volume


def get_spread(order_depth):
    """
    Returns the spread
    """
    best_bid, _ = get_best_bid(order_depth)
    best_ask, _ = get_best_ask(order_depth)
    if best_bid is None or best_ask is None:
        return None
    return best_ask - best_bid


def get_mid_price(order_depth):
    """
    Returns the mid price
    """
    best_bid, _ = get_best_bid(order_depth)
    best_ask, _ = get_best_ask(order_depth)
    if best_bid is None or best_ask is None:
        return None
    return (best_bid + best_ask) / 2


def get_average_price(trades):
    """
    Returns the average price of a list of trades
    """
    return sum(trade for trade in trades) / len(trades) if len(trades) != 0 else 0


def get_average_market_trade_price(trades):
    """
    Returns the average price of a list of market trades
    """
    return sum(trade.price for trade in trades) / len(trades) if len(trades) != 0 else 0


def get_moving_average(prices, window_size):
    """
    Returns the moving average of the last window_size trades
    """
    window_size = min(len(prices), window_size)
    return sum(price for price in prices[-window_size:]) / window_size


def get_moving_std(trades, window_size):
    """
    Returns the moving standard deviation of the last window_size trades
    """
    window_size = min(len(trades), window_size)
    mean = get_moving_average(trades, window_size)
    return math.sqrt(sum((trade.price - mean) ** 2 for trade in trades[-window_size:]) / window_size)


def get_vwap_bid(order_depth):
    """
    Returns the volume weighted average price of the buy orders
    """
    weighted_sum = 0
    quantity_sum = 0
    for price, quantity in order_depth.buy_orders.items():
        weighted_sum += price * quantity
        quantity_sum += quantity
    return weighted_sum / quantity_sum if quantity_sum != 0 else 0


def get_vwap_ask(order_depth):
    """
    Returns the volume weighted average price of the sell orders
    """
    weighted_sum = 0
    quantity_sum = 0
    for price, quantity in order_depth.sell_orders.items():
        weighted_sum += price * quantity
        quantity_sum += quantity
    return weighted_sum / quantity_sum if quantity_sum != 0 else 0


def place_buy_order(product, orders, price, quantity):
    """
    Places a buy order
    """
    quantity = abs(quantity)
    orders.append(Order(product, price, quantity))


def place_sell_order(product, orders, price, quantity):
    """
    Places a sell order
    """
    quantity = abs(quantity)
    orders.append(Order(product, price, -quantity))


def fill_sell_orders(product, orders, order_depth, limit, acceptable_bid_price):
    """
    Fills sell orders up to a given limit and price
    """
    limit = abs(limit)
    if len(order_depth.sell_orders) == 0:
        return
    for best_ask in range(min(order_depth.sell_orders), math.floor(acceptable_bid_price) + 1):
        if best_ask in order_depth.sell_orders:
            best_ask_volume = min(limit, -order_depth.sell_orders[best_ask])
            place_buy_order(product, orders, best_ask, best_ask_volume)
            limit -= best_ask_volume
            if limit <= 0:
                return


def fill_buy_orders(product, orders, order_depth, limit, acceptable_ask_price):
    """
    Fills buy orders up to a given limit and price
    """
    limit = abs(limit)
    if len(order_depth.buy_orders) == 0:
        return
    for best_bid in range(max(order_depth.buy_orders), math.ceil(acceptable_ask_price) - 1, -1):
        if best_bid in order_depth.buy_orders:
            best_bid_volume = min(limit, order_depth.buy_orders[best_bid])
            place_sell_order(product, orders, best_bid, best_bid_volume)
            limit -= best_bid_volume
            if limit <= 0:
                return

def is_increasing(lst):
    """
    Returns True if the list is increasing, False otherwise
    """
    for i in range(1, len(lst)):
        if lst[i] < lst[i - 1]:
            return False
    return True

def is_decreasing(lst):
    """
    Returns True if the list is decreasing, False otherwise
    """
    for i in range(1, len(lst)):
        if lst[i] > lst[i - 1]:
            return False
    return True

def sell_signal(prices, window_size):
    """
    Returns True if the price has been increasing for the last window_size trades but is starting to decrease
    """
    return is_increasing(prices[-1 - window_size:-1]) and prices[-1] < prices[-2]

def buy_signal(prices, window_size):
    """
    Returns True if the price has been decreasing for the last window_size trades but is starting to increase
    """
    return is_decreasing(prices[-1 - window_size:-1]) and prices[-1] > prices[-2]
