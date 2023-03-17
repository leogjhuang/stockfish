from trader import Trader
from sample.sample0 import state
import datamodel


def main():
    traderBot = Trader()
    traderBot.run(state)

if __name__ == "__main__":
    main()
