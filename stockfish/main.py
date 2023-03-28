from trader import Trader
from sample.sample0 import state
import datamodel


def main():
    trader = Trader()
    simulate_alternative(3, 0, trader, False, 30000)

if __name__ == "__main__":
    main()
