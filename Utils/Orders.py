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
    # Place order and record time
    context.exit_order = data.parentTrader.order(context.security, -context.positionSize, LimitOrder(np.round(price.mid,2)), accountCode='default')
    context.exit_time = context.sTime # Save order time for future reference
    
    # wait for order to be filled, if time takes too long, modify price
    # while checkFillstatus(context,data)==False: # Order hasn't been filled
    #     time.sleep(1)
    #     if context.exit_time.timestamp()-context.sTime.timestamp()>10:
    #         print("Modifying Price")
    #         modifyOrder(context, data, price) # modify order to determine whether or not to lower the price
    
    # reset flags
    Utils.doLogging(context,data,ema,price)
    Utils.flag_reset(context)
    context.shares=0
    time.sleep(60)



def generateBuyOrder(context,data,price,ema):
    """ This function places the orders. 
    Conditions for buying order: We decided to place an order (enter_flag ==true), and 
    havent yet placed the order (entry_flag==false)"""

    context.entry_time = context.sTime  # record time of entry    
   
   # calculate number of shares to buy
    if context.shortBool or context.short_flag: 
        shares = -np.round((0.2*context.portfolio.portfolio_value/price.mid))
        if context.portfolio.cash<np.abs(shares)*price.mid:
            print("not enough cash to go fully into position")
            shares = -np.round((0.2*context.portfolio.cash/price.mid))
    else:
        shares = np.round((0.2*context.portfolio.portfolio_value/price.mid))
        if context.portfolio.cash<np.abs(shares)*price.mid:
            print("not enough cash to go fully into position")
            shares = np.round((0.2*context.portfolio.cash/price.mid))
    
    # record number of shares in position
    context.shares = context.shares+shares 

    # place the order
    context.order = data.parentTrader.order(context.security, shares, LimitOrder(np.round(price.mid,2)),
                            accountCode='default')
                            
    
    # if Order is filled, set appropriate flags
    # while data.parentTrader.get_order_status(context.order) not in [OrderStatus.FILLED]:
    #     print(data.parentTrader.get_order_status(context.order))
    #     time.sleep(1)
        
    # Set flag to determine which type of position we hold
    if context.shortBool:
        context.short_flag = True   
    else:
        context.long_flag=True
    
    # Reset flags and update log
    Utils.dailyLogging(context,data,ema,price)
    context.entry_flag =  True           
    context.longBool =    False
    context.shortBool =   False
    context.enter_flag =  False
    context.double_flag =  False 
    time.sleep(60)