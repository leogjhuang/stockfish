import math
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

class Trader:
    """
    Trading a trending market.
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

            if product == "PEARLS":
                self.ask_price[product] = min(self.ask_price.get(product, get_best_ask(order_depth)[0]), get_best_ask(order_depth)[0])
                self.bid_price[product] = max(self.bid_price.get(product, get_best_bid(order_depth)[0]), get_best_bid(order_depth)[0])
                if self.ask_price[product] < self.bid_price[product]:
                    place_buy_order(product, orders, self.ask_price[product], buy_volume)
                    place_sell_order(product, orders, self.bid_price[product], sell_volume)
            elif product == "BANANAS":
                if product not in self.prices:
                    self.prices[product] = []
                self.prices[product].append(get_mid_price(order_depth))
                self.acceptable_price[product] = get_moving_average(self.prices[product], 3)
                best_ask, best_ask_volume = get_best_ask(order_depth)
                if best_ask < self.acceptable_price[product]:
                    place_buy_order(product, orders, best_ask, best_ask_volume)
                best_bid, best_bid_volume = get_best_bid(order_depth)
                if best_bid > self.acceptable_price[product]:
                    place_sell_order(product, orders, best_bid, best_bid_volume)

            result[product] = orders

        return result


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
