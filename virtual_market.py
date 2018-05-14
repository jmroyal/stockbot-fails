from alpha_vantage.timeseries import TimeSeries
import datetime
import finance

class v_market:

    # Two constants that are used to choose how much to buy/sell.
    # STOP_LEVEL represents the expected decrease in price at which an
    # investor should dump all of their shares in a stock. We set this
    # at 20% based on outside research.
    # RISK_TOLERANCE represents the amount of our total worth that we
    # are willing to lose on a bet on a single stock. Most recommendations
    # state that this should be 2% or less. We set this at 4% because it
    # is unlikely that we will ever actually risk 2% if we set RISK_TOLERANCE
    # at that value based on the way the buy_risk method works.
    STOP_LEVEL = 0.2
    RISK_TOLERANCE = 0.04

    # Constructor that creates an inventory with starting cash
    def __init__(self, starting_cash=0):

        # Inventory is a dictionary with stocks as keys and # of shares as values
        self.inventory = {}
        self.inventory["CASH"] = starting_cash

        # A dictionary that stores closing prices and dates for the most
        # recent stock the user has examined
        # Because this info is needed regularly, we call check_stock()
        # once, store the value here, and then update it if necessary
        self.date_close = {}
        self.stock = ""

        # Instance of the indicators class used across virtual market to minimize
        # calls to alpha vantage API to collect indicator data
        self.data = finance.indicators()

    # Method to check if we have enough money to make a purchase
    def check_money(self, price):
        return self.inventory["CASH"] > price

    # Method to get the value of a stock on a specifc date
    # Note - this method uses whatever stock was last loaded
    # using the check_stock() method
    def get_value_at(self, date):
        return self.date_close[date]

    # Method to calculate the value of our inventory
    def calc_worth(self,date):
        worth = self.inventory["CASH"]
        stocks = self.convert_to_list(self.inventory)
        for i in range(1, len(stocks)):
            if self.stock != stocks[i]:
                self.check_stock(stocks[i])
            current = self.get_value_at(date)
            worth += current * self.inventory[stocks[i]]
        return worth

    # Method to get the inventory
    def get_inventory(self):
        return self.inventory

    # Method to purchase a specified amount of a stock
    def buy_date(self, name, date, amount):
        current = self.get_value_at(date)
        if self.check_money(current * amount):
            if name in self.inventory:
                self.inventory[name] += amount
                self.inventory["CASH"] -= current * amount
            else:
                self.inventory[name] = amount
                self.inventory["CASH"] -= current * amount
        else:
            return -1

        return 0

    # Method to sell a specified number of shares on a specific date
    def sell_date(self, name, date, amount):
        if name in self.inventory:
            if self.inventory[name] >= amount:
                current = self.get_value_at(date)
                self.inventory[name] -= amount
                self.inventory["CASH"] += current * amount
                return 0
        return -1

    # Method to return the closing prices of a stock
    def check_stock(self, name):

        self.stock = name

        ts = TimeSeries(key='J4XLT1RK0S2QK5X0')
        data, meta_data = ts.get_daily(symbol=name,outputsize="full")

        keys = self.convert_to_list(data)

        self.date_close = {}

        for i in range(len(keys)-1, -1, -1):
            self.date_close[keys[i]] = float(data[keys[i]]["4. close"])

        return self.date_close

    # Method to return a list of stock prices over a date range
    def check_stock_range(self, name, end_date, num_days):
        keylist = self.convert_to_list(self.date_close)
        i = keylist.index(end_date)
        closings = []
        for num in range(i - num_days, i, 1):
            closings.append(self.date_close[keylist[num]])

        return closings

    # Alternate version of buy_risk() that doesn't take conf_array
    def buy_risk(self, name, date):

        t = self.calc_trend(name, date, 1)
        r = self.RISK_TOLERANCE * t
        w = self.calc_worth(date)
        p = self.get_value_at(date)
        n = (int)(w * r / (p * self.STOP_LEVEL))  # change to an int because we can't buy fractions

        # If we can't buy as many shares as we want with our current cash,
        # buy as many as possible
        if n * p > self.inventory["CASH"]:
            n = (int)(self.inventory["CASH"] / p)

        # Call the buy_date method to actually add shares to our inventory
        self.buy_date(name, date, n)

        return n

    """
    # A method that automatically determines how many shares of a stock
    # we should buy based on a variety of inputs. See the comments below
    # for the formula. This method calls the buy_date() method to actually
    # add shares to our inventory
    def buy_risk(self, name, date, conf_array):

        high = 0
        for i in conf_array:
            if i > high:
                high = i

        p = []
        for i in conf_array:
            if i != high:
                p.append(i)

        # Calculation of how much to buy:
        # We determine how much to buy using the following formula:
        # n = w * r / (p * STOP_LEVEL)
        # Where n is the number to buy, w is our current worth,
        # r is the maximum percentage of our worth we are willing
        # to lose, p is the price, and STOP_LEVEL is a 20% decrease
        # in price (the maximum we will allow before selling off
        # all shares of a stock)
        t = self.calc_trend(name, date, 1)
        c = self.calc_confidence(high, p[0],p[1],p[2])
        r = self.RISK_TOLERANCE * t * c # the maximum amount of risk we want to take on
                                        # if trend strength was 100% and the network was
                                        # 100% confident, we'd risk 4% of our worth
        w = self.calc_worth(date)
        p = self.get_value_at(date)
        n = (int) (w * r / (p * self.STOP_LEVEL)) # change to an int because we can't buy fractions

        # If we can't buy as many shares as we want with our current cash,
        # buy as many as possible
        if n*p > self.inventory["CASH"]:
            n = (int) (self.inventory["CASH"] / p)

        # Call the buy_date method to actually add shares to our inventory
        self.buy_date(name,date,n)

        return n
    """

    # Alternate version of sell_risk() that doesn't take conf_array
    def sell_risk(self, name, date, dp):

        if not name in self.get_inventory().keys():
            return 0

        t = self.calc_trend(name, date, 0)
        cur = self.get_inventory()[name]
        n = (int) (-cur * (dp / self.STOP_LEVEL) * t) # Multiply by -1 because dp is negative
                                                      # NOTE: THIS ROUNDING MIGHT CAUSE PROBLEMS

        # Call the sell_date method to actually remove shares from our inventory
        self.sell_date(name, date, n)

        return n

    """
    # A method that automatically determines how many shares of a stock
    # we should sell based on a variety of inputs. See the comments below
    # for the formula. This method calls the sell_date() method to actually
    # remove shares from our inventory
    def sell_risk(self, name, date, conf_array, dp):
        
        if not name in self.get_inventory().keys():
            return 0
        
        high = 0
        for i in conf_array:
            if i > high:
                high = i

        p = []
        for i in conf_array:
            if i != high:
                p.append(i)

        # Calculation of how much to sell:
        # We determine how much to sell using the following formula:
        # n = -cur * (dp / STOP_LEVEL) * t * c
        # Where n is how many shares to sell off, c is the # of shares we currently
        # own, dp is the expected price change determined by the network, STOP_LEVEL
        # is a 20% decrease in share price, t is the trend strength based on technical
        # indicators, and c is the network's confidence in its prediction.
        t = self.calc_trend(name, date, 0)
        c = self.calc_confidence(high, p[0], p[1], p[2])
        cur = self.get_inventory()[name]
        n = (int) (-cur * (dp / self.STOP_LEVEL) * t * c) # Multiply by -1 because dp is negative
                                                          # NOTE: THIS ROUNDING MIGHT CAUSE PROBLEMS

        # Call the sell_date method to actually remove shares from our inventory
        self.sell_date(name, date, n)

        return n
    """

    # Calculation of trend strength:
    # Trend strength (t in buy_risk and sell_risk) is simply the average
    # of two technical indicators that show trend strength: ADX and Aroon.
    # This is convenient because ADX and Aroon are both measured on a 0
    # to 100 scale, with 100 being the strongest trend possible.
    def calc_trend(self, name, date, type):
        adx = float(self.data.get_adx(name, date))
        aroon = float(self.data.get_aroon(name, date, type))
        return (adx+aroon)/200.0 # divide by 200 to get a value between 0 and 1

    # Calculation to determine the confidence in the network's prediction:
    # The highest value (guess) is weighted positive one, and each of the
    # three other options are weighted negative one third (so that we cannot
    # obtain an output less than 0). The sum of these is our confidence level.
    def calc_confidence(self, guess, p1, p2, p3):
        return guess - p1/3.0 - p2/3.0 - p3/3.0

    # Method to take a dictionary and return its keys as a list
    def convert_to_list(self, dict):
        keys = []
        for i in dict.keys():
            keys.append(i)
        return keys

    # Method to reformat the closing prices of a stock
    def __format_dates(self, start, data, size):
        if (not (start in data)):
            return -1

        keys = self.convert_to_list(data)
        if (not (keys.index(start)+size < len(keys)-1)):
            return -2

        new_dict = {}
        for i in range(size):
            new_dict[i] = data[keys[i]]

        return new_dict


"""
# Testing check_stock() and __format_dates()
test = check_stock("MSFT")
test_2 = __format_dates("2017-09-29", test, 40)
print(test)
print(test_2)
print("\n")

# Testing buy(), sell(), and calc_worth()
print(inventory)
print(calc_worth())
print(buy("MSFT", 3))
print(inventory)
print(calc_worth())
print(sell("MSFT",1))
print(inventory)
print(calc_worth())
print(buy("GOOG", 1))
print(inventory)
print(calc_worth())
print(get_current_value("MSFT"))
print(get_current_value("GOOG"))
"""