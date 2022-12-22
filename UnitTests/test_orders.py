"""
This file contains utilities used to assist in testing
"""
### Imports\
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
from UnitTests import testutils

def test_getFillStatus(context,data):
    """ 4 test conditions: 
    Get real time price and:
    Long:
        - set ask price >>> real price: Tue
        - set ask price <<< real price: False
    Short:
        - set ask price >>> real price: False
        - set ask price <<< real price: True"""
    
    knownOutcomes = [True, False, False, True]
    
    ############# Try to buy long for more than its worth - True #################
    i=0 
    multiplier = np.array([10.,0.1,10.,0.1])
    priceReal = Utils.Price(context,data)
    askPrice = testutils.Price(priceReal.ask/10,priceReal.ask/10,priceReal.ask/10)
    askPriceHigh = testutils.Price(priceReal.ask*10,priceReal.ask*10,priceReal.ask*10)

    if context.i==0:
        context.exit_order= data.parentTrader.order(context.security, -10, LimitOrder(np.round(askPrice.mid,2)), accountCode='default') 
    if context.i==1:
        x1=Orders.checkFillstatus(context,data)
        print("Fill Status: "+str(x1))
        if x1:
            context.outcomes.append(True)
        else:
            context.outcomes.append(False)
        
    if context.i==2:
                context.exit_order= data.parentTrader.order(context.security, 10, LimitOrder(np.round(askPrice.mid,2)), accountCode='default')
    if context.i==3:           
        x2=Orders.checkFillstatus(context,data)
        print("Fill Status: "+str(x2))
        if x2:
            context.outcomes.append(True)
        else:
            context.outcomes.append(False)

    if context.i==4:
                context.exit_order= data.parentTrader.order(context.security, -10, LimitOrder(np.round(askPriceHigh.mid,2)), accountCode='default')
    if context.i==5:           
        x3=Orders.checkFillstatus(context,data)
        print("Fill Status: "+str(x3))
        if x3:
            context.outcomes.append(True)
        else:
            context.outcomes.append(False)

    if context.i==6:
                context.exit_order= data.parentTrader.order(context.security, 10, LimitOrder(np.round(askPriceHigh.mid,2)), accountCode='default')
    if context.i==7:           
        x4=Orders.checkFillstatus(context,data)
        print("Fill Status: "+str(x4))
        if x4:
            context.outcomes.append(True)
        else:
            context.outcomes.append(False)
    print(context.outcomes)
    assert np.all([context.outcomes[i]==knownOutcomes[i] for i in range(len(context.outcomes))]), "Results do not match"