"""
This file contains utilities used to assist in testing
"""
### Imports\
import collections
import csv
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

class context():
    """ This class outputs a generic context structure for testing lower
        level functions"""
    def __init__(self,sim):
        self.run_once = False  # To show if the handle_data has been run in a day
        self.security = symbol('SPY')  # Define a security for the following part
        self.entry_flag = False # flag that we currently own stock
        self.long_flag = False # flag that we currently own long
        self.short_flag = False # flag that we currently own short
        self.hist_1min = sim.request_historical_data(self.security, '1 min', '16000 S')
        self.hist_5min = sim.request_historical_data(self.security, '5 mins', '31300 S')
        self.macd_list = []
        self.entry_price = None
        self.enter_flag = False # flag to buy stock
        self.longBool = False # flag to determine if we are buying long
        self.shortBool = False # flag to determine if we are buying short
        self.stop_price = None
        self.new_stop_price = None
        self.ts_price_1 = None
        self.ts_price_2 = None
        # self.trail = 0.1
        self.trail_1 = 0.1
        self.trail_2 = 0.2
        self.new_ts_flag = False
        self.double_flag = False
        self.exit_flag = False
        self.exitTimerFlag = False
        self.shares = 0
        self.order = None
        self.double_order = None
        self.exit_order = None
        self.entry_time = None
        self.exit_time = None
        self.exitTouchTime = np.NaN
        self.saleFlag = False
        self.price_1 = sim.show_real_time_price(self.security, 'last_price')
        self.price_n = sim.show_real_time_price(self.security, 'last_price')
        self.value = 100000.00
        self.file_name="N/A"
        self.log_name = "N/A"
        self.sTime = -9999
        self.positionSize = 0
        self.macdDelta = 0.1
        self.counter = collections.deque()
        current_date = datetime.date.today()
        current_date_string = str(current_date)
        extension = ".csv"
        self.file_name = "Log\\Buy_Sell_Log_" + current_date_string + extension
        self.log_name = "Log\\Daily_Log_" + current_date_string + extension
        self.sTime = datetime.date.today() # Algo start time
        
class Price():
    """ This class takes in a 3 prices and outputs a dummy price class for testing"""
    def __init__(self,ask, bid, last):
        self.ask=ask
        self.bid=bid
        self.last=last
        self.mid=round((self.ask + self.bid) / 2, 2) # calculate midpoint price  
        
class emaTestData(): 
    """ This class takes in an input array with 9 floats and outputs equivalent to the EMA class. This allows for 
    testing of all enter/exit conditions. Input array order is below:
    
    [fast, fast1, slow, slow1, tline, tline1, macd, macd1, signalLine]
    """
    def __init__(self, inputData):
        assert len(inputData)==9, "Must pass a 9 element array of floats as input"
        
        self.fast = inputData[0]
        self.fast_1 = inputData[1]

        self.slow = inputData[2]
        self.slow_1 = inputData[3]

        self.t_line = inputData[4]
        self.t_line_1 = inputData[5]

        self.macd_1 = inputData[6]
        self.macd = inputData[7]
        self.macd_9 = inputData[8]
        
class contextNoSim():
    """ This class outputs a generic context structure for testing lower
        level functions with no simulation input"""
    def __init__(self):
        self.run_once = False  # To show if the handle_data has been run in a day
        self.security = symbol('SPY')  # Define a security for the following part
        self.entry_flag = False # flag that we currently own stock
        self.long_flag = False # flag that we currently own long
        self.short_flag = False # flag that we currently own short
        self.hist_1min = None
        self.hist_5min = None
        self.macd_list = []
        self.entry_price = None
        self.enter_flag = False # flag to buy stock
        self.longBool = False # flag to determine if we are buying long
        self.shortBool = False # flag to determine if we are buying short
        self.stop_price = None
        self.new_stop_price = None
        self.ts_price_1 = None
        self.ts_price_2 = None
        # self.trail = 0.1
        self.trail_1 = 0.1
        self.trail_2 = 0.2
        self.new_ts_flag = False
        self.double_flag = False
        self.exit_flag = False
        self.exitTimerFlag = False
        self.shares = 0
        self.order = None
        self.double_order = None
        self.exit_order = None
        self.entry_time = None
        self.exit_time = None
        self.exitTouchTime = np.NaN
        self.saleFlag = False
        self.price_1 = None
        self.price_n = None
        self.value = 100000.00
        self.file_name="N/A"
        self.log_name = "N/A"
        self.sTime = -9999
        self.positionSize = 0
        self.macdDelta = 0.1
        self.counter = collections.deque()
        current_date = datetime.date.today()
        current_date_string = str(current_date)
        extension = ".csv"
        self.file_name = "Log\\Buy_Sell_Log_" + current_date_string + extension
        self.log_name = "Log\\Daily_Log_" + current_date_string + extension
        self.sTime = datetime.date.today() # Algo start time