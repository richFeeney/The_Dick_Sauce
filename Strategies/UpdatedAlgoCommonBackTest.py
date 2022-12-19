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

sys.path.append(r'C:\algo2')
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
from UnitTests import testutils

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
    context.exitTimerFlag = False
    context.shares = 0
    context.order = None
    context.double_order = None
    context.exit_order = None
    context.entry_time = None
    context.exit_time = None
    context.exitTouchTime = datetime.datetime.now()
    context.saleFlag = False
    context.price_1 = show_real_time_price(context.security, 'last_price')
    context.price_n = show_real_time_price(context.security, 'last_price')
    context.value = 100000.00
    context.file_name="N/A"
    context.log_name = "N/A"
    context.sTime = -9999
    context.positionSize = 0
    context.macdDelta = 0.5
    context.counter = collections.deque()
    current_date = datetime.date.today()
    current_date_string = str(current_date)
    extension = ".csv"
    context.file_name = "Log\\BackTest_Buy_Sell_Log_" + extension
    context.log_name = "Log\\BackTest_Daily_Log_" + extension
    context.sTime = get_datetime('US/Eastern') # Algo start time
    
    # open and head the log files
    
    with open(context.file_name, 'w', newline='') as csvfile:
        csvfile.write("""time, fast, fast1, slow, tLine, macd, signalLine, longBool, shorBool, longFlag, shortFlag, enterFlag, entryFlag, exitFlag, askPrice, bidPrice, lastPrice, midPrice, portfolioValue, positionValue, cash \n""")
    
    with open(context.log_name, 'w', newline='') as dailyLog:
        dailyLog.write("""time, fast, fast1, slow, tLine, macd, signalLine, longBool, shorBool, longFlag, shortFlag, enterFlag, entryFlag, exitFlag, exitTimerFlag, saleFlag, exitTouchTime, askPrice, bidPrice, lastPrice, midPrice, open, high, low, close, volume, positionSize, portfolioValue, positionValue, cash \n""")

def handle_data(context, data):

    #################### Initialize Variables ####################
    context.sTime = get_datetime('US/Eastern') # Algo start time
    context.positionSize = count_positions(context.security)
    print("Time: "+str(context.sTime))
    print("Position Size:"+str(count_positions(context.security)))
    print("Portfolio Value: "+str(context.portfolio.portfolio_value))
    
    #################### Get Current Price ####################
    price = Utils.Price(context,data)

    #################### Get Historical Data ####################
    context.hist_1min = request_historical_data(context.security, '1 min', '26000 S')
    # context.hist_5min = request_historical_data(context.security, '5 mins', '31300 S')

    #################### Calculate indicators ####################
    ema = IndicatorCalculations.ExpMovAvg(context.hist_1min,price.ask)
        
    if context.sTime.weekday() <= 4 and 10 <= context.sTime.hour <16:  # Only trades on weekdays
        if context.sTime.hour<15 or context.sTime.hour==15 and context.sTime.minute<=30:

            #################### Check to Enter ####################
            if context.positionSize == 0: # if we dont have an order for stock
                print("checking the cross")
                EnterExits.checkCross(context,ema) # check if fast/slow are crossing

                print("checking to enter")
                EnterExits.checkEnter(context, ema,price) # check if we want to enter

            if context.enter_flag: # Place buy order
                print("Placing Buy Order")
                Orders.generateBuyOrder(context,data,price,ema)

            #################### Check to Exit ####################
            if context.positionSize != 0: 
                print("checking to Exit")
                EnterExits.checkExit(context, data, ema, price) # check if we want to exit

            if context.saleFlag: 
                print("Placing sell order")
                Orders.generateSellOrder(context,data,price,ema) # place sell order
            
            #################### Log Outputs ####################
            Utils.dailyLogging(context,data,ema,price)

    #################### Closeout Stuff ####################
    if context.sTime.weekday() <= 4 and context.sTime.hour == 15 and context.sTime.minute == 30 and context.sTime.second >= 0: 
        if context.positionSize != 0: # exit all positions end of day
            Orders.generateSellOrder(context,data,price,ema)
        
        # Utils.closeOutTasks(context,data)               
        # display_all()
        # sys.exit()
    
       
        