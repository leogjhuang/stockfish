import trader
import datamodel


def main():
    traderBot = trader.Trader()
    traderBot.run(datamodel.TradingState(0, {}, {}, {}, {}, {}, {}))

if __name__ == "__main__":
    main()
