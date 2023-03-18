import math

class Util:
    def get_best_bid(self, order_depth):
        """
        Returns the best bid and its volume
        """
        if len(order_depth.buy_orders) == 0:
            return None, None
        best_bid = max(order_depth.buy_orders.keys())
        best_bid_volume = order_depth.buy_orders[best_bid]
        return best_bid, best_bid_volume


    def get_best_ask(self, order_depth):
        """
        Returns the best ask and its volume
        """
        if len(order_depth.sell_orders) == 0:
            return None, None
        best_ask = min(order_depth.sell_orders.keys())
        best_ask_volume = -order_depth.sell_orders[best_ask]
        return best_ask, best_ask_volume


    def get_mid_price(self, order_depth):
        """
        Returns the mid price
        """
        best_bid, _ = self.get_best_bid(order_depth)
        best_ask, _ = self.get_best_ask(order_depth)
        if best_bid is None or best_ask is None:
            return None
        return (best_bid + best_ask) / 2


    def get_moving_average(self, trades, window_size):
        """
        Returns the moving average of the last window_size trades
        """
        window_size = min(len(trades), window_size)
        return sum(trade.price for trade in trades[-window_size:]) / window_size


    def get_moving_std(self, trades, window_size):
        """
        Returns the moving standard deviation of the last window_size trades
        """
        window_size = min(len(trades), window_size)
        mean = self.get_moving_average(trades, window_size)
        return math.sqrt(sum((trade.price - mean) ** 2 for trade in trades[-window_size:]) / window_size)

    def get_vwap(self, orders):
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