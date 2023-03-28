import json
import math
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
UKULELE = "UKULELE"
PICNIC_BASKET = "PICNIC_BASKET"
