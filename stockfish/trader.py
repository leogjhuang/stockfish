from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
from algorithms.algo1 import Algo1

class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        algo = Algo1()
        return algo.run(state)

