"""
a set of functions that calculate the EMAs in the 2 and 5 minute bars

@author: Grady Mellin

"""

### Imports
import time
from IBridgePy.IbridgepyTools import symbol
from numpy import sum
from datetime import timedelta
import pandas as pd


def EMA(values, current_price, n):
    start = len(values) - n+1
    sma_start = len(values) - (2*n) + 1
    ema = (sum(values[sma_start:start]))/n
    # print(ema)
    j = 1
    for i in range(start+1, len(values)):
        ema = (values[i] - ema) * (2 / (n + 1)) + ema
        # print(values[i])
        j += 1
    # print("\n")
    ema = (current_price - ema) * (2 / (n + 1)) + ema
    ema = round(ema, 2)
    return ema

def EMA_1(values, n):
    start = len(values) - n
    sma_start = (len(values) - (2*n))
    ema = (sum(values[sma_start:start]))/n
    v = values[sma_start:start]
    j = 1
    r = range(start+1, len(values))

    for i in range(start+1, len(values)):
        v2 = values[i]
        ema = (values[i] - ema) * (2 / (n + 1)) + ema
        j += 1
    ema = round(ema, 2)
    return ema

def MACD(values, current_macd, n):
    # values_list = [values[:-9].close, values[:-8].close, values[:-7].close, values[:-6].close,
    #                values[:-5].close, values[:-4].close, values[:-3].close, values[:-2].close, values[:-1].close]
    values_list = []
    for i in range(-18, 0):
        values_list.append(values[:i].close)
    macd_list = []
    for x in values_list:
        ###fast_length
        ema_12 = EMA_1(x, 12)
        ###slow_length
        start_26 = len(x) - 26
        ema_26 = EMA_1(x, 26)
        macd_x = ema_12 - ema_26
        macd_list.append(macd_x)

    macd_n = EMA(macd_list, current_macd, n)
    # start = len(macd_list) - n
    # macd_n = sum(macd_list[start:len(macd_list)]) / n
    # j = 1
    # for i in range(start, len(macd_list)):
    #     macd_n = (macd_list[i] - macd_n) * (9 / (j + 1)) + macd_n
    #     j+=1
    # macd_n = (current_macd - macd_n) * (9 / (n + 1)) + macd_n
    macd_n = round(macd_n, 2)
    return macd_n

def seconds_between(values, current_macd):
    values.iloc[-1].name