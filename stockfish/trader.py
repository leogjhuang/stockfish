import json
import math
import numpy as np
from typing import Any, Dict, List
from datamodel import Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState


class Trader:
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
            PICNIC_BASKET: 70
        }
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
            self.dolphin_sightings_list.append(state.observations[DOLPHIN_SIGHTINGS])

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
                window = self.moving_average_window[DOLPHIN_SIGHTINGS]
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
    local: bool
    local_logs: dict[int, str] = {}

    def __init__(self, local=False) -> None:
        self.logs = ""
        self.local = local

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]]) -> None:
        output = json.dumps({
            "state": state,
            "orders": orders,
            "logs": self.logs,
        }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True)
        if self.local:
            self.local_logs[state.timestamp] = output
        print(output)

        self.logs = ""

    def compress_state(self, state: TradingState) -> dict[str, Any]:
        listings = []
        for listing in state.listings.values():
            listings.append([listing["symbol"], listing["product"], listing["denomination"]])

        order_depths = {}
        for symbol, order_depth in state.order_depths.items():
            order_depths[symbol] = [order_depth.buy_orders, order_depth.sell_orders]

        return {
            "t": state.timestamp,
            "l": listings,
            "od": order_depths,
            "ot": self.compress_trades(state.own_trades),
            "mt": self.compress_trades(state.market_trades),
            "p": state.position,
            "o": state.observations,
        }

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append([
                    trade.symbol,
                    trade.buyer,
                    trade.seller,
                    trade.price,
                    trade.quantity,
                    trade.timestamp,
                ])

        return compressed

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])

        return compressed

logger = Logger(local=True)


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


def buy_signal(prices, window_size):
    """
    Returns True if the price has been decreasing for the last window_size trades but is starting to increase
    """
    return is_decreasing(prices[-1 - window_size:-1]) and prices[-1] > prices[-2]


def sell_signal(prices, window_size):
    """
    Returns True if the price has been increasing for the last window_size trades but is starting to decrease
    """
    return is_increasing(prices[-1 - window_size:-1]) and prices[-1] < prices[-2]


PEARLS = "PEARLS"
BANANAS = "BANANAS"
COCONUTS = "COCONUTS"
PINA_COLADAS = "PINA_COLADAS"
DIVING_GEAR = "DIVING_GEAR"
BERRIES = "BERRIES"
DOLPHIN_SIGHTINGS = "DOLPHIN_SIGHTINGS"
BAGUETTE = "BAGUETTE"
DIP = "DIP"
UKELELE = "UKELELE"
PICNIC_BASKET = "PICNIC_BASKET"
