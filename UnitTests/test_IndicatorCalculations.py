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

def test_counterFunctions():
    sim = build_active_IBridgePy_plus('DU2628075') # Build an active trader to get connected to Interactive Brokers 
    context = Utils.initializeJupyter(sim)
    choice = [True, False, True, True, True, False, False, True, True, False, False, True, True, False, True, True, False, True]
    output = [True, True, False, False, True, True, False, False, True, True, False, True, True, False, True]
    N=15
    
    for i in range(len(choice)):
        context.entry_flag = choice[i]
        IndicatorCalculations.appendCounter(context,N=N)
        
    assert IndicatorCalculations.countFlips(context)==8, "wrong number of flips counted"
    assert len(context.counter)==N, "Counter vector is the wrong length"
    assert np.all([context.counter[i]==output[i] for i in range(len(output))]), "Output Vector does not match"