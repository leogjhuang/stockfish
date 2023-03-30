"""
Utility functions
"""
from datamodel import Order


def get_best_ask(order_depth):
    """
    Returns the best ask
    """
    return min(order_depth.sell_orders)


def get_best_bid(order_depth):
    """
    Returns the best bid
    """
    return max(order_depth.buy_orders)


def get_worst_ask(order_depth):
    """
    Returns the worst ask
    """
    return max(order_depth.sell_orders)


def get_worst_bid(order_depth):
    """
    Returns the worst bid
    """
    return min(order_depth.buy_orders)


def get_mid_price(order_depth):
    """
    Returns the mid price
    """
    best_bid = get_best_bid(order_depth)
    best_ask = get_best_ask(order_depth)
    return (best_bid + best_ask) / 2


def get_moving_average(prices, window_size):
    """
    Returns the moving average of the last window_size trades
    """
    window_size = min(len(prices), window_size)
    return sum(price for price in prices[-window_size:]) / window_size


def place_buy_order(product, orders, price, quantity):
    """
    Places a buy order
    """
    orders.append(Order(product, price, abs(quantity)))


def place_sell_order(product, orders, price, quantity):
    """
    Places a sell order
    """
    orders.append(Order(product, price, -abs(quantity)))
