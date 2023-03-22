import math
import json
from typing import Dict, List, Any
from datamodel import OrderDepth, TradingState, Order, ProsperityEncoder, Symbol

class Trader:
    """
    Trading a stable and trending market respectively.
    Monitor changes in the bid/ask prices and place limit orders accordingly.
    """
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20}
        self.ask_price = {}
        self.bid_price = {}
        self.prices = {}
        self.acceptable_price = {}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """"
        Main entry point for the algorithm
        """
        result = {}

        for product, order_depth in state.order_depths.items():
            orders: list[Order] = []
            position = state.position.get(product, 0)
            buy_volume = self.position_limit.get(product, 0) - position
            sell_volume = self.position_limit.get(product, 0) + position
            best_ask, _ = get_best_ask(order_depth)
            best_bid, _ = get_best_bid(order_depth)
            self.ask_price[product] = min(self.ask_price.get(product, best_ask), best_ask)
            self.bid_price[product] = max(self.bid_price.get(product, best_bid), best_bid)

            if product == "PEARLS":
                if self.ask_price[product] < self.bid_price[product]:
                    place_buy_order(product, orders, self.ask_price[product], buy_volume)
                    place_sell_order(product, orders, self.bid_price[product], sell_volume)
            elif product == "BANANAS":
                if product not in self.prices:
                    self.prices[product] = []
                self.prices[product].append(get_mid_price(order_depth))
                self.acceptable_price[product] = get_moving_average(self.prices[product], 15)
                fill_sell_orders(product, orders, order_depth, buy_volume, self.acceptable_price[product])
                fill_buy_orders(product, orders, order_depth, sell_volume, self.acceptable_price[product])

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


def get_vwap(orders):
    """
    orders = order_depth.buy_orders or order_depth.sell_orders
    """
    weighted_sum = 0
    quantity_sum = 0
    for price in orders:
        quantity = orders[price]
        weighted_sum += price * quantity
        quantity_sum += quantity
    return weighted_sum / quantity_sum if quantity_sum != 0 else 0


def place_buy_order(product, orders, price, quantity):
    """
    Places a buy order
    """
    quantity = abs(quantity)
    print("BUY", str(quantity) + "x", price)
    orders.append(Order(product, price, quantity))


def place_sell_order(product, orders, price, quantity):
    """
    Places a sell order
    """
    quantity = abs(quantity)
    print("SELL", str(quantity) + "x", price)
    orders.append(Order(product, price, -quantity))


def fill_sell_orders(product, orders, order_depth, limit, acceptable_bid_price):
    """
    Fills sell orders up to a given limit and price
    """
    limit = abs(limit)
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
    for best_bid in range(max(order_depth.buy_orders), math.ceil(acceptable_ask_price) - 1, -1):
        if best_bid in order_depth.buy_orders:
            best_bid_volume = min(limit, order_depth.buy_orders[best_bid])
            place_sell_order(product, orders, best_bid, best_bid_volume)
            limit -= best_bid_volume
            if limit <= 0:
                return
