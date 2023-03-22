from typing import Dict, List
from stockfish.datamodel import Order, TradingState
from stockfish.utils import place_buy_order, place_sell_order, get_best_ask, get_best_bid, get_mid_price, get_moving_average, fill_buy_orders, fill_sell_orders


class Algo7:
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

        return result
