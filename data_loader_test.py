# NOTE: THIS IS A DUPLICATE OF THE DATA_LOADER CLASS THAT HAS BEEN MODIFIED
# TO WORK WITH THE FINANCE GET_INDICATOR METHOD. THIS IS NOT THE VERSION OF
# DATA_LOADER WE ARE USING. It is merely here in case we decide to utilize
# get_indicator() in the future, so that we don't lose the implementation
# that was being tested prior.

# This is a data loader class that helps with maintaining an active database
# of stock data. The "manager" instance allows the user to create an initial
# database via init_write() and to then continuously update it with fetch().

# To update the dataset, simply do this in the terminal:
# >>>from data_loader import manager
# >>>m = manager()
# >>>m.fetch()

# This is a time-expensive process due to AV's throttling of requests. If you
# call fetch(), be sure that you have enough time for the process to complete.
# It should also be noted that since safe writing was removed (i.e. being able
# to view the changes that will be written before "pushing" them onto the files
# via push() [kind of like GitHub]), one must be absolutely sure that calling
# fetch() is necessary, since once the method is called, the files will be
# edited immediately.

# Future features: automatic fetching of macroeconomic data.

from alpha_vantage.timeseries import TimeSeries
import time
import csv
import datetime
import finance


# Reformats pandas-format data into a list.
def fetch_data(index, row):
    timedata = index.split()

    # Format: yyyy-mm-dd
    date = timedata[0]
    timeofday = timedata[1]

    # Monetary data
    o = row["1. open"]
    h = row["2. high"]
    l = row["3. low"]
    c = row["4. close"]
    v = row["5. volume"]

    return [date, timeofday, o, h, l, c, v]


# Simply returns all stock symbols in symbols.txt as a list.
def get_symbols():
    symbol_file = open("data//symbols.txt", "r")
    symbols = symbol_file.readlines()

    corrected = []

    # Correcting for newline delimiters.
    for symbol in symbols:
        corrected.append(symbol.rstrip())

    return corrected


# Class to help maintain a database of intraday stock data for multiple companies.
class manager:
    ts = TimeSeries("J4XLT1RK0S2QK5X0", output_format="pandas")

    def __init__(self):
        # self.deltas = {}
        pass

    # WARNING: This method should only be used once when setting up the database.
    # This is a method to create csv files for all stocks in symbols.txt, and to
    # populate said csv files with a single batch of data. This should only be
    # used ONCE, or else all files will be overwritten.
    def init_write(self):
        for stock_symbol in get_symbols():
            intraday_data, meta_data = self.ts.get_intraday(symbol=stock_symbol, outputsize="full", interval="1min")

            # with open("data//intraday//" + stock_symbol + ".csv", "w") as intraday_file:
            with open("data//intraday_test//" + stock_symbol + ".csv", "w") as intraday_file:
                writer = csv.writer(intraday_file, lineterminator="\n")

                # Writing column titles:
                # writer.writerow(["date", "ToD", "open", "high", "low", "close", "volume"])
                writer.writerow(
                    ["date", "ToD", "open", "high", "low", "close", "volume", "ad", "obv", "mfi", "trange", "mom",
                     "sar"])

                # Instantiate an indicators object to store the indicators in ind_list
                tech_ind = finance.indicators()
                ind_list = ["ad", "obv", "trange", "sar"]

                # To run the retrieval loop below, we need some values for date and time.
                # The specific values don't matter, but get_indicators() needs them to run
                # properly. We get the first date and time in intraday_data for this purpose.
                index, row = next(intraday_data.iterrows())
                array = index.split()
                date = array[0]
                timeofday = array[1]

                # We retrieve the data for each indicator we're checking before
                # running the loop to update our actual dataset. This way, we can
                # throttle our iterations in the retrieval loop without throttling
                # iterations in the update loop that don't involve additional api calls.
                for ind in ind_list:
                    # Call get_indicator for each indicator. We aren't concerned about
                    # storing the output in a variable, just changing the instance
                    # variable data in the indicators object tech_ind.
                    tech_ind.get_indicator(stock_symbol, ind, "1min", date + " " + timeofday[:5])
                    time.sleep(2)  # aforementioned throttling

                # Loop to write the dataset to a csv
                for index, row in intraday_data.iterrows():

                    # Get date and time of day
                    array = index.split()
                    date = array[0]
                    timeofday = array[1]

                    # Get price data based on date and tod
                    info = fetch_data(index, row)

                    # Iterate through ind_list and append current value of each indicator to info
                    for ind in ind_list:
                        data = tech_ind.get_indicator(stock_symbol, ind, "1min", date + " " + timeofday[:5])
                        info.append(data)
                        # No throttling is necessary because we've already retrieved data

                    # Write info to the csv
                    writer.writerow(info)
                    print(info)
                    # writer.writerow(fetch_data(index, row))

            print(stock_symbol + " finished.")

            # To prevent AV from throttling our requests completely, we need to
            # minimize our call frequency. Around half a call per second is good
            # enough to prevent AV from throwing an error. Although we have already
            # inserted delays above, we need to add one here because we are about
            # to iterate again with a new stock and therefore access new data from AV.
            time.sleep(2)

    # Like GitHub's fetch function, this checks for differences between current versions
    # of each stock csv stored locally and the data that is returned through AV. If there
    # are mismatches, they are stored in deltas, to be "committed" via push().
    def fetch(self):
        print("Checking for deltas...")
        symbols = get_symbols()

        # Counter for the stock we are currently at.
        n = 1
        print("#\tTime\t\t\tSymbol\tLast update\t\tDeltas")

        for stock_symbol in symbols:
            intraday_data, metadata = self.ts.get_intraday(symbol=stock_symbol, outputsize="full", interval="1min")

            # Ugly formatting. Oh well.
            print(str(n) + ".\t" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\t" + stock_symbol, end="")

            # String denoting the file that the open() method should access.
            filepath = "data//intraday_test//" + stock_symbol + ".csv"
            # filepath = "data//intraday//" + stock_symbol + ".csv"

            # Empty string fields that denote the date and time of day of the last index. This helps
            # the program understand after what point it should begin appending new values to the csv
            # file.
            lastdate = ""
            lasttime = ""

            # This is not a pretty solution at all. To fetch the last row of the csv file, it is
            # apparently necessary to read over the entire thing, which slows down the updating
            # process significantly. I'll try to find some workaround for that, because there
            # has to be one.
            with open(filepath, "r") as file:
                reader = csv.reader(file)

                for row in reader:
                    lastdate = row[0]
                    lasttime = row[1]

            print("\t" + lastdate + " " + lasttime, end="")

            # Sentry variable of sorts. While the flag is off, the program ignores any input it
            # reads from the new data. It is set to "on" (True) when the row's date and time match
            # the last recorded date and time. Following that iteration, all other iterations
            # will append rows to the csv file.
            flag = False

            # This is to see how many changes are actually made to the file.
            deltas = 0

            with open(filepath, "a") as file:
                writer = csv.writer(file, lineterminator="\n")

                # Iterate through stock data:
                for index, row in intraday_data.iterrows():
                    array = index.split()
                    date = array[0]
                    timeofday = array[1]
                    if flag == True:
                        # Potential implementation of indicators
                        ind_list = ["sma", "ema", "macd", "rsi", "adx", "cci", "ad", "obv"]
                        info = fetch_data(index, row)
                        tech_ind = finance.indicators()
                        for ind in ind_list:
                            data = tech_ind.get_indicator(stock_symbol, ind, "1min", date + " " + timeofday[:5])
                            info.append(data)
                            time.sleep(2)
                        writer.writerow(info)
                        writer.writerow(fetch_data(index, row))
                        deltas += 1

                    if flag == False:
                        if date == lastdate and timeofday == lasttime:
                            flag = True

            print("\t" + str(deltas))
            n += 1

            # Again, a hardcoded wait time.
            # time.sleep(2)


m = manager()
m.init_write()