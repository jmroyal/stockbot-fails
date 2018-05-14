import virtual_market
from keras.models import load_model
import h5py
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import TensorBoard
import numpy
import random
import finance

# Method to take price data and format it so the network can use it
# Note that the output will be one smaller than the input (it's
# effectively a list of deltas sorted into four categories)
# Endpoints should be in ascending order (e1 < e2 < e3)
def format_data(price_data, e1, e2, e3):

    # Output list - will be double-dimensional with
    # each row containing a list with 0s and 1s
    output = []

    # for loop to populate output
    for i in range(len(price_data)-1):

        # Calculate % change in price
        delta = (price_data[i+1]-price_data[i])/price_data[i]

        # Take the price change and determine which category it's in
        cats = [0,0,0,0]
        if delta < e1:
            cats[0] = 1
        elif delta < e2:
            cats[1] = 1
        elif delta < e3:
            cats[2] = 1
        else:
            cats[3] = 1

        # Update output
        output.append(cats)

    return output


# Method to convert a year, month, and day to a string
def date_str(y, m, d):
    date = "" + str(y)
    if m < 10:
        date += "-0" + str(m)
    else:
        date += "-" + str(m)

    if d < 10:
        date += "-0" + str(d)
    else:
        date += "-" + str(d)

    return date

# Method to advance the date by one day
def adv_date(y, m, d, dates):

    # Instantiate variables
    date = ""
    i = 0 # Counter so loop runs at least once

    # Loop to advance until we hit a trading day
    while i < 1 or not date in dates:

        # Change the day and month
        d += 1
        if m == 9 or m == 4 or m == 6 or m == 11:
            if d > 30:
                d = 1
                m += 1
        elif m == 2:
            if y % 400 == 0 or (y % 4 == 0 and y % 100 != 0):
                if d > 29:
                    d = 1
                    m += 1
            elif d > 28:
                d = 1
                m += 1
        elif d > 31:
            d = 1
            m += 1

        # Change the year
        if m > 12:
            y += 1
            m = 1

        # Create a date string
        date = date_str(y, m, d)

        # Increment the counter
        i += 1

    return y,m,d,date

# VM with starting cash
vm = virtual_market.v_market(50000)

# Create a date string
y = 2017
m = 1
d = 3
date = date_str(y,m,d)

# Load the model
#model = load_model("models/Test_model.h5")

# Endpoint variables
endpt1 = -0.05
endpt2 = 0.0
endpt3 = 0.05

# We're trading Google stock to test
stock = "MSFT"

# Get a list of all the trading days from Alpha Vantage
dates = vm.check_stock(stock).keys()

# Instantiate a random number generator
generator = random.Random()

# Trading loop
while date[:7] != "2017-03":

    print("-" * 20)
    print(date)

    closings = vm.check_stock_range(stock, date, 15)
    print(format_data(closings,endpt1,endpt2,endpt3))

    # Predict price change here (save as a dp variable)
    dp = generator.random() - 0.5
    print("Expected price change: " + str(dp*100) + "%")

    # Buy/sell action
    if dp > 0:
        n = vm.buy_risk(stock, date)
        print("Bought " + str(n) + " shares")
    if dp < 0:
        n = vm.sell_risk(stock, date, dp)
        print("Sold " + str(n) + " shares")

    y,m,d,date = adv_date(y,m,d,dates)

print("\n"*2 + "RESULTS" + "\n" + "-"*30)
print("WORTH: " + str(vm.calc_worth(date)))
print(stock + " VALUE AT END OF SIM: " + str(vm.get_value_at(date)))
print("CURRENT " + stock + " VALUE: " + str(vm.get_value_at("2018-02-28")))
print("INVENTORY:")
print(vm.get_inventory())