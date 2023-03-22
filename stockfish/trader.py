import math
import json
from typing import Dict, List, Any
from datamodel import OrderDepth, TradingState, Order, ProsperityEncoder, Symbol

class Trader:
    """
    Trading a stable market.
    Submit 40 buy orders at the lowest known ask price and 40 sell orders at the highest known bid price.
    """
    def __init__(self):
        self.product = "PEARLS"
        self.best_ask = 9998
        self.mid_price = 10000
        self.best_bid = 10002
        self.position_limit = 20

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}
        position_threshold = 15
        orders: list[Order] = []
        position = state.position.get(self.product, 0)
        order_depth = state.order_depths[self.product]
        if position < -position_threshold:
            place_buy_orders_up_to(self.product, orders, -position - position_threshold, order_depth)
        else:
            place_buy_order(self.product, orders, self.best_ask, self.position_limit - position)
        # if position > position_threshold:
        #     place_sell_orders_up_to(self.product, orders, position - position_threshold, order_depth)
        # else:
        place_sell_order(self.product, orders, self.best_bid, self.position_limit + position)
        result[self.product] = orders
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


def place_buy_orders_up_to(product, orders, quantity, order_depth):
    """
    Places buy orders up to a given quantity
    """
    quantity = abs(quantity)
    start = min(order_depth.sell_orders.keys())
    finish = max(order_depth.sell_orders.keys())
    for price in range(start, finish + 1):
        if price in order_depth.sell_orders:
            best_ask_volume = abs(order_depth.sell_orders[price])
            quantity = min(quantity, best_ask_volume)
            place_buy_order(product, orders, price, quantity)
            quantity -= best_ask_volume
            if quantity <= 0:
                return
    
    # for best_ask, best_ask_volume in dict(sorted(order_depth.sell_orders.items())):
    #     best_ask_volume = abs(best_ask_volume)
    #     quantity = min(quantity, best_ask_volume)
    #     print("BUY", str(quantity) + "x", best_ask)
    #     orders.append(Order(product, best_ask, quantity))
    #     quantity -= best_ask_volume
    #     if quantity <= 0:
    #         return


def place_sell_order(product, orders, price, quantity):
    """
    Places a sell order
    """
    quantity = abs(quantity)
    print("SELL", str(quantity) + "x", price)
    orders.append(Order(product, price, -quantity))


def place_sell_orders_up_to(product, orders, quantity, order_depth):
    """
    Places sell orders up to a given quantity
    """
    quantity = abs(quantity)
    start = max(order_depth.buy_orders.keys())
    finish = min(order_depth.buy_orders.keys())
    for price in range(start, finish - 1, -1):
        if price in order_depth.buy_orders:
            best_bid_volume = abs(order_depth.buy_orders[price])
            quantity = min(quantity, best_bid_volume)
            place_sell_order(product, orders, price, quantity)
            quantity -= best_bid_volume
            if quantity <= 0:
                return

    # quantity = abs(quantity)
    # for best_bid, best_bid_volume in dict(sorted(order_depth.buy_orders.items(), reverse=True)):
    #     best_bid_volume = abs(best_bid_volume)
    #     quantity = min(quantity, best_bid_volume)
    #     print("SELL", str(quantity) + "x", best_bid)
    #     orders.append(Order(product, best_bid, -quantity))
    #     quantity -= best_bid_volume
    #     if quantity <= 0:
    #         return
