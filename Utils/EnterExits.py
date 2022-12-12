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
    if (price.ask > ema.fast)  and (ema.fast> ema.slow) : # check to see we are in enter long conditions
        print('Checking Long before the chop\n')
        if (ema.fast  > ema.fast_1) and ema.macd > (ema.macd_9 + context.macdDelta): # checks to ensure we are not buying in the chop
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
    if (price.ask < ema.fast) and (ema.fast< ema.slow): # check to see we are in enter short conditions
        print('Checking short before the chop\n')
        if (ema.fast < ema.fast_1)  and ema.macd < (ema.macd_9 - context.macdDelta): # checks to ensure we are not buying in the chop
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

    if context.longBool:
        if ema.t_line>ema.slow and ema.fast>ema.slow and ema.macd>ema.macd_9: # double position
            Orders.generateBuyOrder(context,data,price,ema) 
        else:
            context.saleFlag=True
    if context.shortBool:
        if ema.t_line<ema.slow and ema.fast<ema.slow and ema.macd<ema.macd_9: # double position
            Orders.generateBuyOrder(context,data,price,ema) 
        else:
            context.saleFlag=True


def checkExit(context, data, ema, price):
    """This function takes in the input context, which is an IBPY standard structure, and an EMA dataframe and 
        calls the checks if we are deciding to enter short or long"""
    # TODO come back and clean up these if statements, I am just putting it like this because I know it works and I'm short on time
    currentTime = datetime.datetime.now() # TODO (come back and fix this later to confirm sTime will work)
    if checkSellShort(context,ema,price) and context.shortBool:
        context.exit_flag=True
        # context.shortBool=False
    if checkSellLong(context,ema,price) and context.longBool: # if we enter on either short or long, set flag to true
        context.exit_flag=True
        # context.longBool=False
    if context.exit_flag and context.exitTimerFlag==False:
        context.exitTimerFlag=True
        context.exitTouchTime = datetime.datetime.now()  # record time which price touches the fast
    if context.exit_flag and checkCross(context, ema): # if we cross within the timer, exit position
        context.saleFlag=True
    elif context.exit_flag and context.exitTimerFlag:
        if np.abs(context.exitTouchTime.timestamp()-currentTime.timestamp())>60 :
            checkDoubleOrNothing(context,data, price,ema)
            context.exitTimerFlag=False

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
        print("Exit long Position")
        exit_flag_temp = True
    return exit_flag_temp
    
def checkSellShort(context, ema, price):
    """This function sells a short security when the following occurs
        - price closes above the fast EMA"""
    print('checking to sell short \n')
    exit_flag_temp=False # set enter flag to false Automatically
    if (price.ask > ema.fast): # check to if price is greater than the fast
        print("Exit short Position")
        exit_flag_temp = True
    return exit_flag_temp
