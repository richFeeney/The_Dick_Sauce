### Imports


import csv
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pytz
import sys
import time

class ExpMovAvg():
    """This function will take in your 1 minute data, 5 minute data (must both be dataFrames),and n vector 
    (vector containing periods for fast, slow, and Tline) and output a structure containing all relevant EMAs"""
    
    def __init__(self,min1Data, price: float, nVec: list = [13, 48, 8]):
        
        assert len(nVec)==3, "N vector must have 3 periods for fast, slow, and T line"
       
        # calculate all the EMAs

        self.fast = EMA(min1Data.close, price, nVec[0])
        self.fast_n = EMA(min1Data.close, price, nVec[0])
        self.fast_1 = EMA_1(min1Data.close, nVec[0])
        self.fast_2 = EMA_1(min1Data.close, nVec[0])

        self.slow = EMA(min1Data.close, price, nVec[1])
        self.slow_n = EMA(min1Data.close, price, nVec[1])
        self.slow_1 = EMA_1(min1Data.close, nVec[1])
        self.fast_slope = round((self.fast_n - self.fast_2)/2, 4)
        self.slow_slope = round((self.slow_n - self.slow_1) / 2, 4)

        self.t_line = EMA(min1Data.close, price, nVec[2])
        self.t_line_n = EMA(min1Data.close, price, nVec[2])
        self.t_line_1 = EMA_1(min1Data.close, nVec[2])
        self.t_slope = round((self.t_line_n-self.t_line_1) / 2, 4)
        
        # change to 1 min data from 5 min data going forward
        self.fast_length_1 = EMA_1(min1Data.close, 12)
        self.slow_length_1 = EMA_1(min1Data.close, 26)
        self.fast_length = EMA_1(min1Data.close, 12)
        self.slow_length = EMA_1(min1Data.close, 26)

        self.macd_1 = self.fast_length_1 - self.slow_length_1
        self.macd = round(self.fast_length - self.slow_length, 2) # MACD at time T
        self.macd_slope = round((self.macd-self.macd_1)/2, 4)
        self.macd_9 = MACD(min1Data, self.macd, 9) # signal line



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
    macd_n = round(macd_n, 2)
    return macd_n

def calcEMA(min1Data, min5Data, price: float, nVec: list = [13, 48, 8]): #TODO see if we can delete this
    """This function will take in your 1 minute data, 5 minute data (must both be dataFrames),and n vector 
    (vector containing periods for fast, slow, and Tline) and output a structure containing all relevant EMAs"""
    
    assert len(nVec)==3, "N vector must have 3 periods for fast, slow, and T line"
       
    # calculate all the EMAs
    
    fast = EMA(min1Data.close, price, nVec[0])
    fast_n = EMA(min1Data.close, price, nVec[0])
    fast_1 = EMA_1(min1Data.close, nVec[0])
    fast_2 = EMA_1(min1Data.close, nVec[0])

    slow = EMA(min1Data.close, price, nVec[1])
    slow_n = EMA(min1Data.close, price, nVec[1])
    slow_1 = EMA_1(min1Data.close, nVec[1])
    fast_slope = round((fast_n - fast_2)/2, 4)
    slow_slope = round((slow_n - slow_1) / 2, 4)

    t_line = EMA(min1Data.close, price, nVec[0])
    t_line_n = EMA(min1Data.close, price, nVec[2])
    t_line_1 = EMA_1(min1Data.close, nVec[2])
    t_slope = round((t_line_n-t_line_1) / 2, 4)
    
    # change to 1 min data from 5 min data going forward
    fast_length_1 = EMA_1(min1Data.close, 12)
    slow_length_1 = EMA_1(min1Data.close, 26)
    fast_length = EMA_1(min1Data.close, 12)
    slow_length = EMA_1(min1Data.close, 26)

    macd_1 = fast_length_1 - slow_length_1
    macd = round(fast_length - slow_length, 2) # MACD at time T
    macd_slope = round((macd-macd_1)/2, 4)
    macd_9 = MACD(min5Data, macd, 9) # signal line
    
    # concatenate all outputs into an array before passing into a dataframe
    outputList = np.array([fast, fast_n, fast_1, fast_2, 
                    slow, slow_n, slow_1, fast_slope, slow_slope,
                    t_line, t_line_n, t_line_1, t_slope, 
                    fast_length_1, slow_length_1, fast_length, slow_length,
                    macd, macd_1, macd_slope, macd_9 ])
    
    # load all data into dataframe
    ema=pd.DataFrame(outputList.reshape(1,21), columns=["fast", "fast_n", "fast_1", "fast_2", 
                      "slow", "slow_n", "slow_1", "fast_slope", "slow_slope",
                      "t_line", "t_line_n", "t_line_1", "t_slope", 
                      "fast_length1", "slow_length_1", "fast_length", "slow_length",
                      "macd", "macd_1", "macd_slope", "macd_9" ])

    return ema

def appendCounter(context, N: int = 15):
    """ This function takes in a counter vector and throws out the left side and appends the right side if the vector is 
    greater than size N"""
    context.counter.append(context.entry_flag)
    if len(context.counter)>N:
        context.counter.popleft()
    
def countFlips(context):
    """ This function takes in an input vector and counts the number of times the vector has flipped from true to false"""
    return np.count_nonzero(np.array([context.counter[i]!=context.counter[i+1] for i in range(len(context.counter)-1)]))

def getWeightedAverage(context, n: int = 3, weights: list = [0.1, 0.3, 0.6]):
    """This function takes an N element vector and a weight vector and applies a weighted average of the vector"""
    
    assert len(weights)==n, "N must be length of weights vector"
    assert np.sum(weights)==1, "Weights must sum to 1"

    context.weightAvg =  np.sum(np.array([(context.tSlope[i]*weights[i]) for i in range(n)]))
    
def getTLineSlope(context, ema):
    """ This function manages the deque for the tLine and tLineSlope"""
    
    context.tLine.append(ema.t_line) # append tLine
    if len(context.tLine)>2: # if tLine is larger than two elements, take the slope and drop the oldest element
        context.tSlope.append(context.tLine[1]-context.tLine[0])
        context.tLine.popleft()
    if len(context.tSlope)>3: # if the tslope is larger than 3 elements, drop the oldest element
        context.tSlope.popleft()
    if len(context.tSlope)==3:
        getWeightedAverage(context)