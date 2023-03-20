import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt

day_number_is_one_filename = 'day_one.png'
day_number_is_not_one_filename = 'day_n.png'

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

def plot_graph(data_dict):

    data_by_day = {}

    for product in data_dict:
        data_by_day[product] = {}
        done = False
        day_count = min(list(data_dict[product]['day']))
        day_number = 0
        while not done:
            todays_data = data_dict[product][data_dict[product]['day'] == day_count]
            if len(todays_data.index) == 0:
                done = True
            else:
                data_by_day[product][day_count] = todays_data
                day_count += 1
                day_number += 1


    fig, axs = plt.subplots(len(data_by_day),day_number)
    fig.suptitle('Price/Time')
    product_count = 0
    if day_number == 1:
        for product in data_by_day:
            day_count = 0
            for day_data in data_by_day[product]:
                plot_columns = list(data_by_day[product][day_data].keys())
                for i in range(6):
                    if i < 3:
                        colour = 'red'
                    else:
                        colour = 'blue'
                    transparency = list(data_by_day[product][day_data][plot_columns[2*i+3]])
                    transparency_transform = []
                    for j in range(len(transparency)):
                        transparency_transform.append(sigmoid(transparency[j] / 20 - 5))
                    axs[product_count].scatter(data_by_day[product][day_data]["timestamp"], data_by_day[product][day_data][plot_columns[2*i+2]], color=colour, alpha=np.array(transparency_transform))
                axs[product_count].set_title(f'{product}: Day {day_data}')
                axs[product_count].set(xlabel="Time", ylabel="Price")
                axs[product_count].grid(True)
                day_count += 1
            product_count += 1
        pltSaveFig(day_number_is_one_filename)
    else:
        for product in data_by_day:
            day_count = 0
            for day_data in data_by_day[product]:
                plot_columns = list(data_by_day[product][day_data].keys())
                for i in range(6):
                    if i < 3:
                        colour = 'red'
                    else:
                        colour = 'blue'
                    transparency = list(data_by_day[product][day_data][plot_columns[2*i+3]])
                    transparency_transform = []
                    for j in range(len(transparency)):
                        transparency_transform.append(sigmoid(transparency[j] / 20 - 5))
                    axs[product_count, day_count].scatter(data_by_day[product][day_data]["timestamp"], data_by_day[product][day_data][plot_columns[2*i+2]], color=colour, alpha=np.array(transparency_transform))
                axs[product_count, day_count].set_title(f'{product}: Day {day_data}')
                axs[product_count, day_count].set(xlabel="Time", ylabel="Price")
                axs[product_count, day_count].grid(True)
                day_count += 1
            product_count += 1
        pltSaveFig(day_number_is_not_one_filename)

def pltSaveFig(filename):
    # plt.show()
    plt.savefig(filename)

def main():
    plotData()
    # test()

def plotData():
    day0 = pd.read_csv(r'prices_round_1_day_0.csv', sep=";")
    day1 = pd.read_csv(r'prices_round_1_day_-1.csv', sep=";")
    day2 = pd.read_csv(r'prices_round_1_day_-2.csv', sep=";")

    frames = [day0, day1, day2]

    df = pd.concat(frames)

    pearldata = df[df['product'] == "PEARLS"].drop(axis=1, columns=["product", "mid_price", "profit_and_loss"]).fillna(axis=0, method="ffill").fillna(axis=0, method="bfill")
    bananadata = df[df['product'] == "BANANAS"].drop(axis=1, columns=["product", "mid_price", "profit_and_loss"]).fillna(axis=0, method="ffill").fillna(axis=0, method="bfill")

    plt.style.use('classic')

    data_dict = {"BANANAS": bananadata, "PEARLS": pearldata}

    plot_graph(data_dict)

def test():
    testReadCSV()

def testReadCSV():
    day0 = pd.read_csv(r'prices_round_1_day_0.csv', sep=";")
    day1 = pd.read_csv(r'prices_round_1_day_-1.csv', sep=";")
    day2 = pd.read_csv(r'prices_round_1_day_-2.csv', sep=";")
    print(day0)
    print(day1)
    print(day2)

if __name__ == '__main__':
    main()