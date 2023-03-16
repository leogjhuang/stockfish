import math
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        algo = Algo1()
        return algo.run(state)


class Algo1:
    """
    Contains the logic for the trading algorithm.
    """

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
            if product == 'PEARLS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Define a fair value for the PEARLS.
                # Note that this value of 1 is just a dummy value, you should likely change it!
                acceptable_price = 10000

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:
                    # Variable keeping track of how much room we have left to buy
                    # We can only buy up to 20 PEARLS at a time
                    # This variable is initialized to 20, and is decremented by the volume of each order
                    limit = 20 - state.position[product] if product in state.position else 20
                    # Go through every single sell order from lowest to acceptable_price - 1
                    for best_ask in range(min(order_depth.sell_orders.keys()), acceptable_price):
                        # Check if the current price has any orders
                        if best_ask in order_depth.sell_orders:
                            # If there are orders, retrieve the volume
                            best_ask_volume = min(-order_depth.sell_orders[best_ask], limit)
                            # Send a BUY order at the price level of the ask, with the same quantity
                            print("BUY", str(best_ask_volume) + "x", best_ask)
                            orders.append(Order(product, best_ask, best_ask_volume))
                            limit -= best_ask_volume
                            if limit <= 0:
                                break

                    # # Sort all the available sell orders by their price,
                    # # and select only the sell order with the lowest price
                    # best_ask = min(order_depth.sell_orders.keys())
                    # best_ask_volume = order_depth.sell_orders[best_ask]

                    # # Check if the lowest ask (sell order) is lower than the above defined fair value
                    # if best_ask < acceptable_price:

                    #     # In case the lowest ask is lower than our fair value,
                    #     # This presents an opportunity for us to buy cheaply
                    #     # The code below therefore sends a BUY order at the price level of the ask,
                    #     # with the same quantity
                    #     # We expect this order to trade with the sell order
                    #     print("BUY", str(-best_ask_volume) + "x", best_ask)
                    #     orders.append(Order(product, best_ask, -best_ask_volume))

                # The below code block is similar to the one above,
                # the difference is that it finds the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium
                if len(order_depth.buy_orders) != 0:
                    limit = state.position[product] + 20 if product in state.position else 20
                    # Go through every single buy order from highest to acceptable_price + 1
                    for best_bid in range(max(order_depth.buy_orders.keys()), acceptable_price, -1):
                        # Check if the current price has any orders
                        if best_bid in order_depth.buy_orders:
                            # If there are orders, retrieve the volume
                            best_bid_volume = min(order_depth.buy_orders[best_bid], limit)
                            # Send a SELL order at the price level of the bid, with the same quantity
                            print("SELL", str(best_bid_volume) + "x", best_bid)
                            orders.append(Order(product, best_bid, -best_bid_volume))
                            limit -= best_bid_volume
                            if limit <= 0:
                                break
                    # best_bid = max(order_depth.buy_orders.keys())
                    # best_bid_volume = order_depth.buy_orders[best_bid]
                    # if best_bid > acceptable_price:
                    #     print("SELL", str(best_bid_volume) + "x", best_bid)
                    #     orders.append(Order(product, best_bid, -best_bid_volume))

                # Add all the above orders to the result dict
                result[product] = orders

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        return result

