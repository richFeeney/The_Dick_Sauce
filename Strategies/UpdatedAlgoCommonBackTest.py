"""
The sauce algorithm updated for modularity

@author: Grady Mellin, Rich Feeney
developed by Lane Capital Group

"""

### Imports\
import csv
import collections
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pdb
import pytz
import sys
import time

sys.path.append(r'D:\algo2\IBridgePy_Win_Anaconda38_64 - Copy')
from IBridgePy.Trader import Trader
from trader_factory import build_active_IBridgePy_plus
from IBridgePy.IbridgepyTools import symbol
from IBridgePy.constants import OrderStatus
from IBridgePy.OrderTypes import LimitOrder
from Utils import Algos
from Utils import EnterExits
from Utils import IndicatorCalculations
from Utils import Orders
from Utils import Plotters
from Utils import Utils


def initialize(context):
    """ This function initializes all variables and flags at the beginning of a session"""
    context.run_once = False  # To show if the handle_data has been run in a day
    context.security = symbol('SPY')  # Define a security for the following part
    context.entry_flag = False # flag that we currently own stock
    context.long_flag = False # flag that we currently own long
    context.short_flag = False # flag that we currently own short
    context.hist_1min = request_historical_data(context.security, '1 min', '16000 S')
    context.hist_5min = request_historical_data(context.security, '5 mins', '31300 S')
    context.macd_list = []
    context.entry_price = None
    context.enter_flag = False # flag to buy stock
    context.longBool = False # flag to determine if we are buying long
    context.shortBool = False # flag to determine if we are buying short
    context.stop_price = None
    context.new_stop_price = None
    context.ts_price_1 = None
    context.ts_price_2 = None
    # context.trail = 0.1
    context.trail_1 = 0.1
    context.trail_2 = 0.2
    context.new_ts_flag = False
    context.double_flag = False
    context.exit_flag = False
    context.TG_flag = False
    context.shares = None
    context.order = None
    context.double_order = None
    context.exit_order = None
    context.entry_time = None
    context.exit_time = None
    context.price_1 = show_real_time_price(context.security, 'last_price')
    context.price_n = show_real_time_price(context.security, 'last_price')
    context.value = 100000.00
    context.file_name="N/A"
    context.log_name = "N/A"
    context.sTime = -9999
    context.macdDelta = 0.05
    context.counter = collections.deque()
    current_date = datetime.date.today()
    current_date_string = str(current_date)
    extension = ".csv"
    context.file_name = "Log\\backtest\\BASE_Buy_Sell_Log_" + current_date_string + extension
    context.log_name = "Log\\backtest\\BASE_Daily_Log_" + current_date_string + extension
    context.sTime = get_datetime('US/Eastern') # Algo start time
    
    # open and head the log files
    
    with open(context.file_name, 'w', newline='') as csvfile:
        csvfile.write("""time, fast, fast1, slow, tLine, macd, signalLine, longBool, shorBool, longFlag, shortFlag, enterFlag, entryFlag, exitFlag, askPrice, bidPrice, lastPrice, midPrice, portfolioValue, positionValue, cash \n""")
    
    with open(context.log_name, 'w', newline='') as dailyLog:
        dailyLog.write("""time, fast, fast1, slow, tLine, macd, signalLine, longBool, shorBool, longFlag, shortFlag, enterFlag, entryFlag, exitFlag, askPrice, bidPrice, lastPrice, midPrice, portfolioValue, positionValue, cash \n""")

def handle_data(context, data):

    #################### Initialize Variables ####################
    context.sTime = get_datetime('US/Eastern') # Algo start time
    print(context.sTime)
    #################### Get Current Price ####################
    price = Utils.Price(context,data)
    if context.sTime.weekday() <= 9 and 10<= context.sTime.hour < 15:  # Only trades on weekdays
        if context.sTime.second == 1 or context.sTime.second == 21 or context.sTime.second == 41: # TODO fix this

            #################### Get Historical Data ####################
            context.hist_1min = request_historical_data(context.security, '1 min', '26000 S')
            context.hist_5min = request_historical_data(context.security, '5 mins', '31300 S')
        
        #################### Calculate indicators ####################
        ema = IndicatorCalculations.ExpMovAvg(context.hist_1min, context.hist_5min, price.ask)

        
        #################### Check to Enter ####################
        if not context.enter_flag: # if we dont have an order for stock
            print("checking to enter")
            print("shortFlag: "+str(context.short_flag)+", longFlag: "+str(context.long_flag)+", shortBool: "+str(context.shortBool)+", longBool: "+str(context.longBool)+", enterFlag: "+str(context.enter_flag)+", entryFlag: "+str(context.entry_flag)+", exitFlag: "+str(context.exit_flag))
            EnterExits.checkEnter(context,ema,price) # check if we want to enter
        if context.enter_flag and not context.entry_flag: # Place buy order
            print("Placing Buy Order")
            print("shortFlag: "+str(context.short_flag)+", longFlag: "+str(context.long_flag)+", shortBool: "+str(context.shortBool)+", longBool: "+str(context.longBool)+", enterFlag: "+str(context.enter_flag)+", entryFlag: "+str(context.entry_flag)+", exitFlag: "+str(context.exit_flag))
            Orders.generateBuyOrder(context,data,price,ema)

        #################### Check to Exit ####################
        if context.entry_flag: 
            print("checking to Exit")
            print("shortFlag: "+str(context.short_flag)+", longFlag: "+str(context.long_flag)+", shortBool: "+str(context.shortBool)+", longBool: "+str(context.longBool)+", enterFlag: "+str(context.enter_flag)+", entryFlag: "+str(context.entry_flag)+", exitFlag: "+str(context.exit_flag))
            EnterExits.checkExit(context, ema, price) # check if we want to exit
        if context.exit_flag: 
            print("Placing sell order")
            print("shortFlag: "+str(context.short_flag)+", longFlag: "+str(context.long_flag)+", shortBool: "+str(context.shortBool)+", longBool: "+str(context.longBool)+", enterFlag: "+str(context.enter_flag)+", entryFlag: "+str(context.entry_flag)+", exitFlag: "+str(context.exit_flag))
            Orders.generateSellOrder(context,data,price,ema) # place sell order
        
        #################### Log Outputs ####################
        Utils.dailyLogging(context,data,ema,price)
