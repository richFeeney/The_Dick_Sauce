"""
This algorithm allows for testing of order features

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
from UnitTests import testutils
from UnitTests import test_orders

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
    context.exitTouchTime = np.NaN
    context.saleFlag = False
    context.price_1 = show_real_time_price(context.security, 'last_price')
    context.price_n = show_real_time_price(context.security, 'last_price')
    context.value = 100000.00
    context.file_name="N/A"
    context.log_name = "N/A"
    context.sTime = -9999
    context.positionSize = 0
    context.macdDelta = 0.1
    context.counter = collections.deque()
    current_date = datetime.date.today()
    current_date_string = str(current_date)
    extension = ".csv"
    context.file_name = "Log\\Buy_Sell_Log_" + current_date_string + extension
    context.log_name = "Log\\Daily_Log_" + current_date_string + extension
    context.sTime = get_datetime('US/Eastern') # Algo start time
    context.i=0
    context.outcomes = []
def handle_data(context, data):

    #################### Initialize Variables ####################
    context.sTime = get_datetime('US/Eastern') # Algo start time
    context.positionSize = count_positions(context.security)
    print("Time: "+str(context.sTime))
    print("Position Size:"+str(count_positions(context.security)))
    print("Portfolio Value: "+str(context.portfolio.portfolio_value))
    
    #################### Get Current Price ####################
    
    test_orders.test_getFillStatus(context,data)
    context.i+=1
    if context.i==9:
        sys.exit()