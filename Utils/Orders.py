### Imports
from IBridgePy.Trader import Trader
from IBridgePy.constants import OrderStatus
from IBridgePy.OrderTypes import LimitOrder
from Utils import Utils


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


def checkFillstatus(context,data):
    """This function checks the order status and returns a True if its filled,
    otherwise it returns a False"""
    return data.parentTrader.get_order_status(context.exit_order) in [OrderStatus.FILLED]

def modifyOrder(context, data, price, N: int = 5):
    i = int(context.sTime.timestamp() - context.exit_time.timestamp())
    if i>=N:
        newPrice=Utils.modifyPrice(context,price, i)
        data.parentTrader.modify_order(context.exit_order, newLimitPrice=newPrice)
        context.exit_time = context.sTime

def generateSellOrder(context,data,price,ema):
    """ This function places the orders.
    Conditions for buying order: We decided to place an order (exit_flag ==true), and 
    havent yet placed the order (exit order==None)"""
    # pdb.set_trace()
    if context.exit_flag and context.exit_order is None: # Order has not been placed yet
        context.exit_order = data.parentTrader.order(context.security, -context.positionSize, LimitOrder(np.round(price.mid,2)), accountCode='default')
        context.exit_time = context.sTime # Save order time for future reference
    else: # Order has been placed
        if checkFillstatus(context,data): # Order has been filled
            context.exit_order = None # reset flags
            context.exit_flag = False
            Utils.flag_reset(context)
            Utils.doLogging(context,data,ema,price)
            context.shares=0
        else: # Order has not been filled
            print("Modifying Price")
            modifyOrder(context, data, price) # modify order to determine whether or not to lower the price

def generateBuyOrder(context,data,price,ema):
    """ This function places the orders. 
    Conditions for buying order: We decided to place an order (enter_flag ==true), and 
    havent yet placed the order (entry_flag==false)"""
    # pdb.set_trace()
    # check to see if a flag was set to place an order, and we dont currently have open orders
    if context.enter_flag and not context.entry_flag: 
        context.entry_price = price.mid
        
        # calculate number of shares to buy/short (TODO: write a smarter function)
        if context.shortBool: 
            shares = -np.round((0.2*context.portfolio.portfolio_value/price.mid))
        else:
            shares = np.round((0.2*context.portfolio.portfolio_value/price.mid))
        
        context.shares = context.shares+shares

        # place the order
        context.order = data.parentTrader.order(context.security, shares, LimitOrder(np.round(price.mid,2)),
                                accountCode='default')
                                
        context.double_flag =  False # set flag to false after placing order to avoid multiple erroneous orders

        # if Order is filled, set appropriate flags
        if data.parentTrader.get_order_status(context.order) in [OrderStatus.FILLED, OrderStatus.PRESUBMITTED,
                                                OrderStatus.SUBMITTED]:
            context.entry_time = context.sTime 
            
            if context.shortBool:
                context.short_flag = True   
            else:
                context.long_flag=True
            
            context.entry_flag =  True           
            context.longBool =    False
            context.shortBool =   False
            context.enter_flag =  False

            Utils.doLogging(context,data,ema,price)