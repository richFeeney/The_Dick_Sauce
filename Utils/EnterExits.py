### Imports


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


def checkLong(context, ema, price):
    """This function takes in the input context, which is an IBPY standard structure and determines 
    whether or not to enter long, conditions for entering long are:
        - Price > Fast EMA > Slow EMA
    This function also has safeguards in place to reduce enters while in "the chop", these conditions are:
        - Fast is increasing
        -  macd > signal line
        This function returns a flag which determines whether or not to enter"""
    
    enter_flag_temp = False # set enter flag to false Automatically
    print('checking long\n')
    if (price.mid > ema.fast)  and (ema.fast> ema.slow) : # check to see we are in enter long conditions
        print('Checking Long before the chop\n')

        if (ema.fast  > ema.fast_1) and (ema.macd > (ema.macd_9 + context.macdDelta)): # checks to ensure we are not buying in the chop
            print('We passed the chop, buy long')
            enter_flag_temp = True # buy               
    return enter_flag_temp


def checkShort(context, ema, price):
    """This function takes in the input context, which is an IBPY standard structure and determines 
    whether or not to enter short, conditions for entering short are:
        - Price < Fast EMA < Slow EMA
    This function also has safeguards in place to reduce enters while in "the chop", these conditions are:
        - Fast is decreasing
        - macd is less than signal line
        This function returns a flag which determines whether or not to enter"""
    # pdb.set_trace()
    enter_flag_temp = False  # set enter flag to false Automatically
    print('checking short\n')
    if (price.mid < ema.fast) and (ema.fast< ema.slow): # check to see we are in enter short conditions
        print('Checking short before the chop\n')

        if (ema.fast < ema.fast_1)  and (ema.macd < (ema.macd_9 - context.macdDelta)): # checks to ensure we are not buying in the chop
            print('We passed the chop, buy short')
            enter_flag_temp = True # buy         
    return enter_flag_temp

def checkEnter(context, ema, price):
    """This function takes in the input context, which is an IBPY standard structure, and an EMA dataframe and 
        calls the checks if we are deciding to enter short or long"""
    
    if checkShort(context,ema,price):# if we enter on either short or long, set flag to true
        context.enter_flag=True
        context.shortBool=True
    if checkLong(context,ema,price): # if we enter on either short or long, set flag to true
        context.enter_flag=True
        context.longBool=True

def checkDoubleOrNothing(context, data, price, ema):
    """ This function checks if we want to increase our position or sell our position after the 60 second timer is up
    Conditions for increasing long position:
    - T line is greater than slow
    - fast is greater than slow
    - Macd is greater than signal line
    
     Conditions for increasing short position:
    - T line is less than slow
    - fast is less than slow
    - Macd is less than signal line
    
    If the position increase requirements are not met, we exit the position"""

    if context.long_flag:
        if ema.t_line>ema.slow and ema.macd>ema.macd_9: # double position
            print("Double Long")
            Orders.generateBuyOrder(context,data,price,ema) 
        else:
            print("exit not double")
            context.saleFlag=True
    if context.short_flag:
        if ema.t_line<ema.slow and ema.macd<ema.macd_9: # double position
           print("Double Long")
           Orders.generateBuyOrder(context,data,price,ema) 
        else:
            print("exit not double")
            context.saleFlag=True


def checkExit(context, data, ema, price):
    """ This function checks if we want to exit a position. Conditions for exit are as follows:

        - Checks to exit short or long position based on criteria defined in those respective functions
        - If we decide to exit for the first time, start a 60s timer
        - If fast and slow cross at any time, exit trade
        - Once 60s timer is up, look to see if we add to position or exit based on the criteria defined in that function
        - Clean up flags and place order
    
    """

    if checkSellShort(context,ema,price) and context.short_flag: # check to exit short
        context.exit_flag=True

    if checkSellLong(context,ema,price) and context.long_flag: # check to exit long
        context.exit_flag=True

    if context.exit_flag and context.exitTimerFlag==False: # is this the first time we have decided to exit? if so, start the timer
        context.exitTimerFlag=True
        context.exitTouchTime = context.sTime 

    if context.exit_flag and checkCross(context, ema): # if we cross within the timer, exit position
        context.saleFlag=True
        context.exitFlag=False
        context.exitTimerFlag=False
        print("selling on the cross")

    # if 60s is up, check to see if we add to position or exit from position
    elif context.exit_flag and context.exitTimerFlag:
        if np.abs(context.exitTouchTime.timestamp()-context.sTime.timestamp())>=60:
            print("checking double or nothing")
            checkDoubleOrNothing(context,data, price,ema)
            context.exitTimerFlag=False
            context.exitFlag=False

def checkCross(context, ema):
    """ This function checks for the fast to cross the slow and generates a buy order accordingly. """
    tempFlag=False # flag to return true if cross occurs

    if ema.fast>ema.slow and ema.fast_1<=ema.slow_1: # check if we cross over
        context.enter_flag=True
        context.longBool=True
        tempFlag=True

    elif ema.fast<ema.slow and ema.fast_1>=ema.slow_1: # check if we cross under
        context.enter_flag=True
        context.shortBool=True
        tempFlag=True

    return tempFlag

def checkSellLong(context, ema, price):
    """This function sells a long security when the following occurs
        - price closes below the fast EMA"""
    print('checking to sell long \n')
    exit_flag_temp=False # set enter flag to false Automatically
    if (price.ask < ema.fast): # check to if price is less than the fast
        exit_flag_temp = True
    return exit_flag_temp
    
def checkSellShort(context, ema, price):
    """This function sells a short security when the following occurs
        - price closes above the fast EMA"""
    print('checking to sell short \n')
    exit_flag_temp=False # set enter flag to false Automatically
    if (price.ask > ema.fast): # check to if price is greater than the fast
        exit_flag_temp = True
    return exit_flag_temp
