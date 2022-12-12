### Imports


import csv
import datetime
from dateutil import tz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
import numpy as np
import os
import pandas as pd
import pytz
import sys
import time

sys.path.append(r'D:\algo2\IBridgePy_Win_Anaconda38_64 - Copy')
from Utils import Utils



def plotDailyCandleStick(priceData, 
                 logData, 
                 emaList: list = ['fast', 'slow', "macd"],
                 saveFig: bool = False,
                 outPutFileName: str=r"C:\Users\Lane Capital\OneDrive\Desktop\repos\plots\TestCandle.png",
                 x = None):
    
    """This function takes in a historical input data dataframe, EMA dataframe from calcEMAVector 
    and plots the differnet EMAS against the price. Price is assumed to be the close price"""
    # TODO add volume held for plotting
    #create figure
    fig, ax = plt.subplots(figsize=(36,28))

    #define width of candlestick elements
    width = 0.0005
    width2 = 0.0001

    #define up and down priceData
    up = priceData[priceData.close>=priceData.open]
    down = priceData[priceData.close<priceData.open]
    log = logData.copy()
    if x!=None:
    # remove elements not in the x limit
        up = up[up.time>datetime.datetime.timestamp(x[0])]
        up = up[up.time<datetime.datetime.timestamp(x[1])]

        down = down[down.time>datetime.datetime.timestamp(x[0])]
        down = down[down.time<datetime.datetime.timestamp(x[1])]

        log = log[log.time>datetime.datetime.timestamp(x[0])]
        log = log[log.time<datetime.datetime.timestamp(x[1])]

    #define colors to use
    col1 = 'green'
    col2 = 'red'

    for i,j in enumerate(emaList):
        exec('temp{}=log.{}'.format(i,j))    
        exec('ax.plot(log.date, temp{})'.format(i))

#     outArray=plotEntryStatus(log)
#     ax2 = ax.twinx()
#     ax2.plot(log.date,outArray,color='r')
#     fig.legend(['fast','slow','holding flag'],fontsize=30) # sticking this code here as a lazy fix for the legend

    #plot up priceData
    ax.bar(up.date,up.close-up.open,width,bottom=up.open,color=col1)
    ax.bar(up.date,up.high-up.close,width2,bottom=up.close,color=col1)
    ax.bar(up.date,up.low-up.open,width2,bottom=up.open,color=col1)

    # #plot down priceData
    ax.bar(down.date,down.close-down.open,width,bottom=down.open,color=col2)
    ax.bar(down.date,down.high-down.open,width2,bottom=down.open,color=col2)
    ax.bar(down.date,down.low-down.close,width2,bottom=down.close,color=col2)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M',tz=tz.gettz('America/New York')))


    # Turn grid on for both major and minor ticks and style minor slightly differently.
    ax.grid(which='major')
    ax.grid(which='minor', linewidth=0.25)
    ax.minorticks_on()
    plt.ylim(np.min([np.min(up.low),np.min(down.low)])-.05,np.max([np.max(up.high),np.max(down.high)])+.05)
    if x==None:
        plt.xlabel("Time",fontsize=30)
        plt.ylabel("Stock Price (USD)",fontsize=30)
        plt.title("SPY Stock Price: "+str(datetime.date.today()),fontdict={'fontsize': 40})
    else:
        ax.set(xlim = x)
        plt.xlabel("Time",fontsize=30)
        plt.ylabel("Stock Price (USD)",fontsize=30)
        plt.title("SPY Stock Price: "+str(datetime.date.today()),fontdict={'fontsize': 40})
           
    outArray=plotEntryStatus(log)
    ax2 = ax.twinx()
    ax2.plot(log.date,outArray,color='r')
    ax2.set(ylim = (-1,1))
    if saveFig:
        fig.savefig(outPutFileName)
        

        
def plotDailyCandleStickMacd(priceData, 
                 logData, 
                 emaList: list = ['fast', 'slow', "macd"],
                 saveFig: bool = False,
                 outPutFileName: str=r"C:\Users\Lane Capital\OneDrive\Desktop\repos\plots\TestCandle.png",
                 x = None):

    """This function takes in a historical input data dataframe, EMA dataframe from calcEMAVector 
    and plots the differnet EMAS against the price. Price is assumed to be the close price"""

    #create figure
    fig, (ax,ax1) = plt.subplots(2,figsize=(36,28),gridspec_kw={'height_ratios': [2, 1]})

    #define width of candlestick elements
    width = 0.0005
    width2 = 0.0001

    #define up and down priceData
    up = priceData[priceData.close>=priceData.open]
    down = priceData[priceData.close<priceData.open]
    log = logData.copy()
    if x!=None:
        # remove elements not in the x limit
        up = up[up.time>datetime.datetime.timestamp(x[0])]
        up = up[up.time<datetime.datetime.timestamp(x[1])]

        down = down[down.time>datetime.datetime.timestamp(x[0])]
        down = down[down.time<datetime.datetime.timestamp(x[1])]

        log = log[log.time>datetime.datetime.timestamp(x[0])]
        log = log[log.time<datetime.datetime.timestamp(x[1])]

    #define colors to use
    col1 = 'green'
    col2 = 'red'

    ax.plot(log.date,log.fast)
    ax.plot(log.date,log.slow)

    outArray=plotEntryStatus(log)
    ax1.plot(log.date,outArray)

    ax1.plot(log.date,log.macd)
    ax1.plot(log.date,log.signalLine)


    #plot up priceData
    ax.bar(up.date,up.close-up.open,width,bottom=up.open,color=col1)
    ax.bar(up.date,up.high-up.close,width2,bottom=up.close,color=col1)
    ax.bar(up.date,up.low-up.open,width2,bottom=up.open,color=col1)

    # #plot down priceData
    ax.bar(down.date,down.close-down.open,width,bottom=down.open,color=col2)
    ax.bar(down.date,down.high-down.open,width2,bottom=down.open,color=col2)
    ax.bar(down.date,down.low-down.close,width2,bottom=down.close,color=col2)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M',tz=tz.gettz('America/New York')))


    # Turn grid on for both major and minor ticks and style minor slightly differently.
    ax.grid(which='major')
    ax.grid(which='minor', linewidth=0.25)
    ax.minorticks_on()
    ax.set_ylim(np.min([np.min(up.low),np.min(down.low)])-.05,np.max([np.max(up.high),np.max(down.high)])+.05)

    ax1.grid(which='major')
    ax1.grid(which='minor', linewidth=0.25)
    ax1.minorticks_on()
    ax1.set_ylim((-1.1,1.1))


    ax.set_xlabel("Time",fontsize=30)
    ax1.set_xlabel("Time",fontsize=30)
    ax.set_ylabel("Stock Price (USD)",fontsize=30)
    ax1.set_ylabel("Value (nd)",fontsize=30)
    ax.set_title("SPY Stock Price: "+str(datetime.date.today()),fontdict={'fontsize': 40})
    ax1.set_title("MacD/Signal Line Value",fontdict={'fontsize': 40})
    ax1.legend(["holding flag","macd","signal line"],fontsize=20)
    if x!=None:
        ax.set_xlim(x)
        ax1.set_xlim(x)

    if saveFig:
        fig.savefig(outPutFileName)
        
def plotEntryStatus(logData):
    """ This function takes in data from the daily log, cleans the short/long bool data, and 
    outputs an array displaying if were holding long, short, or nothing."""
    
    # copy data
    log=logData.copy()
    
    # clean up data
    log = Utils.fixBoolData(log)
    
    holdStatus = Utils.calcEntryStatus(log)
    
    return holdStatus
