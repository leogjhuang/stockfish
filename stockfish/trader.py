import json
import math
from typing import Any, Dict, List
from datamodel import Order, OrderDepth, ProsperityEncoder, Symbol, TradingState


class Trader:
    """
    Trading a stable and trending market respectively.
    Monitor changes in the bid/ask prices and place limit orders accordingly.
    """
    def __init__(self):
        self.position_limit = {"PEARLS": 20, "BANANAS": 20, "COCONUTS": 600, "PINA_COLADAS": 300}
        self.global_best_ask: Dict[Symbol, int] = {}
        self.global_best_bid: Dict[Symbol, int] = {}
        self.mid_prices: Dict[Symbol, List[int]] = {}

        #min num of data [buy, sell]
        self.coco_min_num_of_data = [9, 9]
        self.pina_min_num_of_data = [7, 7]

        #vwap data
        self.vwap_bid_prices = {}
        self.vwap_ask_prices = {}

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

            if product == "PEARLS":
                if product not in self.mid_prices:
                    self.mid_prices[product] = []
                if get_mid_price(order_depth) is not None:
                    self.mid_prices[product].append(get_mid_price(order_depth))
                if len(self.mid_prices[product]) > 0 and len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], 5)
                    spread = get_spread(order_depth)
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread / 2.5), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread / 2.5), sell_volume)

            elif product == "BANANAS":
                if product not in self.mid_prices:
                    self.mid_prices[product] = []
                if get_mid_price(order_depth) is not None:
                    self.mid_prices[product].append(get_mid_price(order_depth))
                if len(self.mid_prices[product]) > 0 and len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                    acceptable_price = get_moving_average(self.mid_prices[product], 5)
                    spread = get_spread(order_depth)
                    place_buy_order(product, orders, math.ceil(acceptable_price - spread / 3), buy_volume)
                    place_sell_order(product, orders, math.floor(acceptable_price + spread / 3), sell_volume)

            elif product == "COCONUTS" or product == "PINA_COLADAS":
                best_ask, best_ask_volume = get_best_ask(order_depth)
                best_bid, best_bid_volume = get_best_bid(order_depth)
                best_ask_volume = min(-best_ask_volume, buy_volume)
                best_bid_volume = min(best_bid_volume, sell_volume)

                if product == "COCONUTS":
                    min_num_of_data = self.coco_min_num_of_data
                else:
                    min_num_of_data = self.pina_min_num_of_data

                self.order_by_vwap(
                    product=product,
                    prices=self.vwap_bid_prices,
                    book=order_depth.buy_orders,
                    min_num_of_data=min_num_of_data[1],
                    order_condition=lambda : self.sell_signal(product, min_num_of_data[1]),
                    place_order_function=lambda : place_sell_order(product, orders, best_bid, best_bid_volume)
                )

                self.order_by_vwap(
                    product=product,
                    prices=self.vwap_ask_prices,
                    book=order_depth.sell_orders,
                    min_num_of_data=min_num_of_data[0],
                    order_condition=lambda : self.buy_signal(product, min_num_of_data[0]),
                    place_order_function=lambda : place_buy_order(product, orders, best_ask, best_ask_volume)
                )

            result[product] = orders

        logger.flush(state, orders)
        return result

    def sell_signal(self, product, min_num_of_data):
        vwaps = self.vwap_bid_prices[product]
        return vwaps[-1] < vwaps[-2] and is_increasing(vwaps[-1-min_num_of_data:-1])

    def buy_signal(self, product, min_num_of_data):
        vwaps = self.vwap_ask_prices[product]
        return vwaps[-1] > vwaps[-2] and is_decreasing(vwaps[-1-min_num_of_data:-1])

    def order_by_vwap(self, product, prices, 
                      book,
                      min_num_of_data,
                      order_condition, 
                      place_order_function):
        self.init_list(product, prices)
        prices[product].append(get_vwap(book))
        if self.not_enough_data(product, prices, min_num_of_data):
            return
        if order_condition():
            place_order_function()

    def init_list(self, product, lst):
        if product not in lst:
            lst[product] = []
    
    def not_enough_data(self, product, prices, min_num_of_data):
        return len(prices[product]) <= min_num_of_data

    


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