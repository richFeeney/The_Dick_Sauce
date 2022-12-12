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

def test_modifyPrice():
    
    # Initialize Variables
    var = [0,2,6,10,15,52,1000]
    output = np.zeros(7)
    multiplier = np.array([[0,5, 7, 9, 11, 50],
                       [0.01, 0.015, 0.02, 0.03, 0.04, 0.05]])
    
    # Correct outputs
    goodVars_noMult = [150, 150, 150, 150, 150, 150, 150] #correct output with no mult
    goodVars_short = np.array([151.5, 151.8, 152.625, 155.25, 156.15384615384616, 157.5, 157.5]) #correct output with multiplier and short
    goodVars_long = np.array([148.5, 148.2, 147.375, 144.75, 143.84615384615384, 142.5, 142.5]) #correct output with multiplier and long

    # get context input data and price
    context = testutils.context(sim)
    testPrice = testutils.Price(100,200,300)
    
    # loop through i with multiplier none
    for i,x in enumerate(var):
        output[i] = Utils.modifyPrice(context,testPrice,x)
    assert (output == goodVars_noMult).all(), "Price is not modified correctly"
    
    # loop through i with updated multiplier shortbool on 
    for i,x in enumerate(var):
        output[i] = modifyPrice(context,testPrice,x, multiplier)
    assert (output == goodVars_long).all(), "Price is not modified correctly"
    
    # loop through i with updated multiplier shortbool on 
    context.shortBool = True
    for i,x in enumerate(var):
        output[i] = modifyPrice(context,testPrice,x, multiplier)
    assert (output == goodVars_short).all(), "Price is not modified correctly"