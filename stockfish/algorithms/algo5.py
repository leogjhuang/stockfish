from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from stockfish.utils import get_vwap


class Algo5:
    """
    Bananas trading.
    Experimenting with keeping track of past bid and ask prices.
    """
    all_past_data = []

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'BANANAS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                buy_orders = order_depth.buy_orders
                sell_orders = order_depth.sell_orders

                self.append_orders(buy_orders, sell_orders)

                if state.timestamp == 1500:
                    self.display_past_data(state)

                if state.position.get(product, 0) > 0:
                    self.sell(state, product, order_depth, orders)
                else:
                    self.buy(state, product, order_depth, orders)

                # Add all the above orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        return result

    def append_orders(self, buy_orders, sell_orders):
        self.all_past_data.append(Past(buy_orders, sell_orders))

    def buy(self, state : TradingState, product : str, order_depth : OrderDepth, orders : list[Order]):
        acceptable_price = 4940.944
        # If statement checks if there are any SELL orders in the PEARLS market
        if len(order_depth.sell_orders) > 0:

            # Sort all the available sell orders by their price,
            # and select only the sell order with the lowest price
            best_ask = min(order_depth.sell_orders.keys())
            best_ask_volume = max(order_depth.sell_orders[best_ask], state.position.get(product, 0) - 20)

            # Check if the lowest ask (sell order) is lower than the above defined fair value
            if best_ask < acceptable_price:

                # In case the lowest ask is lower than our fair value,
                # This presents an opportunity for us to buy cheaply
                # The code below therefore sends a BUY order at the price level of the ask,
                # with the same quantity
                # We expect this order to trade with the sell order
                print("BUY", str(-best_ask_volume) + "x", best_ask)
                orders.append(Order(product, best_ask, -best_ask_volume))

    def sell(self, state : TradingState, product : str, order_depth : OrderDepth, orders : list[Order]):
        acceptable_price = 4935.635
        if len(order_depth.buy_orders) != 0:
            best_bid = max(order_depth.buy_orders.keys())
            best_bid_volume = min(order_depth.buy_orders[best_bid], state.position.get(product, 0) + 20) # minus -20
            if best_bid > acceptable_price:
                print("SELL", str(best_bid_volume) + "x", best_bid)
                orders.append(Order(product, best_bid, -best_bid_volume))

    def display_past_data(self, state : TradingState):
        for data in self.all_past_data:
            data : Past = data
            print(state.timestamp)
            print(data.buy_orders)
            print(data.sell_orders)
            print(data.vwap_buy)
            print(data.vwap_sell)
            print('End timestamp')

class Past:
    def __init__(self, buy_orders, sell_orders):
        self.buy_orders = buy_orders
        self.sell_orders = sell_orders
        self.vwap_buy = get_vwap(buy_orders)
        self.vwap_sell = get_vwap(sell_orders)
        # self.trades = None
