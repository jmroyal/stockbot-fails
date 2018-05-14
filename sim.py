import csv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# CALCULATING MINUTE VOLATILITY
prices = []

# take closing prices from a single day, calculate deltas
file = open("data//intraday//TSLA.csv", "r")
reader = csv.reader(file)

date = "2018-03-16"

# Get a single day's prices:
for row in reader:
    if row[0] == date:
        prices.append(float(row[5]))

# calculate deltas
deltas = []
for i in range(1, len(prices)):
    deltas.append((prices[i] - prices[i - 1])/prices[i - 1]*100)

sigma = np.std(deltas)/26.27

print(sigma)
mu = 0
n = 690
dt = 0.0001
x=pd.DataFrame()
x0 = prices[len(prices) - 1]

step = np.exp((mu-sigma**2/2)*dt)*np.exp(sigma*np.random.normal(0, sigma, n))
print(step)
temp = pd.DataFrame(x0*step.cumprod())

x=pd.concat([x, temp], axis=1)
x.columns=np.arange(1)
plt.xlabel("t")
plt.ylabel("X")
plt.plot(x)
plt.show()
