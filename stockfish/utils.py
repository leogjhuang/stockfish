"""
Utility functions for algorithms
"""
import math
from datamodel import Order


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
