import math
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        algo = Algo3()
        return algo.run(state)


class Algo3:

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

                buy_orders = order_depth.buy_orders
                best_bid = max(buy_orders.keys())
                best_bid_volume = -1
                orders.append(Order(product, best_bid + 1, -best_bid_volume))
                print("SELL", str(best_bid_volume) + "x", best_bid)
            
                result[product] = orders
                

        return result

