import math
from typing import Any, Dict, List
from datamodel import Order, OrderDepth, ProsperityEncoder, Symbol, TradingState


class Trader:
    """
    Round 2 PnL: 28862 (Pearls: 1216, Bananas: 1356, Coconuts: 10272, Pina Coladas: 16019)
    Trading a stable, trending, and correlated market respectively.
    Monitor changes in the bid/ask prices and place limit orders accordingly.
    """
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20, "COCONUTS": 600, "PINA_COLADAS": 300}
        self.spread_coefficient = {"PEARLS": 0.4, "BANANAS": 0.3, "COCONUTS": 0.2, "PINA_COLADAS": 0.1}
        self.moving_average_window = {"PEARLS": 5, "BANANAS": 5, "COCONUTS": 1, "PINA_COLADAS": 1}
        self.trend_length = {"PEARLS": 0, "BANANAS": 0, "COCONUTS": 9, "PINA_COLADAS": 0}
        self.mid_prices = {"PEARLS": [], "BANANAS": [], "COCONUTS": [], "PINA_COLADAS": []}
        self.vwap_bid_prices = {"PEARLS": [], "BANANAS": [], "COCONUTS": [], "PINA_COLADAS": []}
        self.vwap_ask_prices = {"PEARLS": [], "BANANAS": [], "COCONUTS": [], "PINA_COLADAS": []}
        self.correlation = {"PEARLS": 0, "BANANAS": 0, "COCONUTS": 0, "PINA_COLADAS": 1.875}

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """"
        Entry point for the algorithm
        """
        result = {}

        for product, order_depth in state.order_depths.items():
            orders: list[Order] = []

            position = state.position.get(product, 0)
            buy_volume = self.position_limit.get(product, 0) - position
            sell_volume = self.position_limit.get(product, 0) + position
            best_ask, best_ask_volume = get_best_ask(order_depth)
            best_bid, best_bid_volume = get_best_bid(order_depth)
            best_ask_volume = min(-1 * best_ask_volume, buy_volume)
            best_bid_volume = min(best_bid_volume, sell_volume)
            vwap_ask = get_vwap_ask(order_depth)
            vwap_bid = get_vwap_bid(order_depth)
            mid_price = get_mid_price(order_depth)
            self.vwap_bid_prices[product].append(vwap_bid)
            self.vwap_ask_prices[product].append(vwap_ask)
            self.mid_prices[product].append(mid_price)

            if product == "PEARLS":
                if len(self.mid_prices[product]) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], self.moving_average_window[product])
                    spread = get_spread(order_depth) * self.spread_coefficient[product]
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread), sell_volume)

            if product == "BANANAS":
                if len(self.mid_prices[product]) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], self.moving_average_window[product])
                    spread = get_spread(order_depth) * self.spread_coefficient[product]
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread), sell_volume)

            if product == "COCONUTS":
                if len(self.vwap_bid_prices[product]) > self.trend_length[product] and self.sell_signal(self.vwap_bid_prices[product], self.trend_length[product]):
                    place_sell_order(product, orders, best_bid, best_bid_volume)
                if len(self.vwap_ask_prices[product]) > self.trend_length[product] and self.buy_signal(self.vwap_ask_prices[product], self.trend_length[product]):
                    place_buy_order(product, orders, best_ask, best_ask_volume)

            if product == "PINA_COLADAS":
                mid_price_coco = get_mid_price(state.order_depths["COCONUTS"])
                actual_correlation = mid_price / mid_price_coco
                target_correlation = self.correlation[product]
                if actual_correlation < target_correlation and len(self.mid_prices["COCONUTS"]) >= 2 and self.mid_prices["COCONUTS"][-1] < self.mid_prices["COCONUTS"][-2]:
                    place_buy_order(product, orders, best_ask, best_ask_volume)
                if actual_correlation > target_correlation and len(self.mid_prices["COCONUTS"]) >= 2 and self.mid_prices["COCONUTS"][-1] > self.mid_prices["COCONUTS"][-2]:
                    place_sell_order(product, orders, best_bid, best_bid_volume)

            result[product] = orders

        return result

    def sell_signal(self, vwaps, min_num_of_data):
        return vwaps[-1] < vwaps[-2] and is_increasing(vwaps[-1-min_num_of_data:-1])

    def buy_signal(self, vwaps, min_num_of_data):
        return vwaps[-1] > vwaps[-2] and is_decreasing(vwaps[-1-min_num_of_data:-1])


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
    for i in range(1, len(lst)):
        if lst[i] < lst[i - 1]:
            return False
    return True

def is_decreasing(lst):
    for i in range(1, len(lst)):
        if lst[i] > lst[i - 1]:
            return False
    return True
