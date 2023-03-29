import json
import math
from typing import Any, Dict, List
from datamodel import Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState


class Trader:
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
            },
            325,
            100
        )

        self.logger.flush(state, result)
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

    def trade_etf(self, state, result, etf, weights, difference, threshold):
        if etf not in state.order_depths or any(product not in state.order_depths for product in weights):
            return
        if etf not in result:
            result[etf] = []
        position = state.position.get(etf, 0)
        buy_volume = self.position_limit.get(etf, 0) - position
        sell_volume = self.position_limit.get(etf, 0) + position
        mid_price = get_mid_price(state.order_depths[etf])
        etf_value = difference
        for product, weight in weights.items():
            etf_value += weight * get_mid_price(state.order_depths[product])
        if mid_price < etf_value - threshold:
            place_buy_order(etf, result[etf], mid_price, buy_volume)
        if mid_price > etf_value + threshold:
            place_sell_order(etf, result[etf], mid_price, sell_volume)


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
    if quantity == 0:
        return
    quantity = abs(quantity)
    orders.append(Order(product, price, quantity))


def place_sell_order(product, orders, price, quantity):
    """
    Places a sell order
    """
    if quantity == 0:
        return
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


"""
Constants for product names
"""

PEARLS = "PEARLS"
BANANAS = "BANANAS"
COCONUTS = "COCONUTS"
PINA_COLADAS = "PINA_COLADAS"
DIVING_GEAR = "DIVING_GEAR"
BERRIES = "BERRIES"
DOLPHIN_SIGHTINGS = "DOLPHIN_SIGHTINGS"
BAGUETTE = "BAGUETTE"
DIP = "DIP"
UKULELE = "UKULELE"
PICNIC_BASKET = "PICNIC_BASKET"


