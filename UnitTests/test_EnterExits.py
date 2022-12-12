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
from UnitTests import testutils

def test_checklong():
    """ four testing conditions:
        1. Price>fast>slow and fast<fast1: False
        2. Price>fast>slow and fast>fast1: True
        3. Price>fast<slow and fast<fast1: False
        4. Price>fast<slow and fast>fast1: False """

    knownOutcomes = [False, True, False, False] # vector containing outcomes
    outcomes = [] # empty list for appending outcomes

    # intialize all inputs
    price = np.ones(4)*100
    fast = np.ones(4)*99
    slow = np.array([98, 98, 101, 101])
    fast1 = np.array([100, 97, 100, 97])
    macd = np.ones(4)*100
    signalLine = np.array([100,99,100,100])
    
    # intialize context class
    context = testutils.contextNoSim()
    
    # loop through and calcualte checkLong
    for i in range(4):
        emaVec = np.array([fast[i], fast1[i], slow[i], slow[i], 0, 0, macd[i], macd[i], signalLine[i] ])
        priceVec = testutils.Price(price[i],price[i],price[i])
        ema = testutils.emaTestData(emaVec)
        outcomes.append(EnterExits.checkLong(context, ema, priceVec))

    assert np.all([outcomes[i]==knownOutcomes[i] for i in range(len(outcomes))]), "Results do not match"

def test_checkShort():
    """ four testing conditions:
        Price<fast<slow and fast<fast1: True
        Price<fast>slow and fast>fast1: False
        Price>fast<slow and fast<fast1: False
        Price>fast<slow and fast>fast1: False """

    knownOutcomes = [True, False, False, False] # vector containing outcomes
    outcomes = [] # empty list for appending outcomes

    # intialize all inputs
    price = np.ones(4)*97
    fast = np.array([98, 98, 96, 96])
    slow = np.array([99, 97, 100, 101])
    fast1 = np.array([100, 97, 92, 95])
    macd = np.ones(4)*100
    signalLine = np.array([101,99,100,100])

    # intialize context class
    context = testutils.contextNoSim()

    # loop through and calcualte checkShort
    for i in range(4):
        emaVec = np.array([fast[i], fast1[i], slow[i], slow[i], 0, 0, macd[i], macd[i], signalLine[i] ])
        priceVec = testutils.Price(price[i],price[i],price[i])
        ema = testutils.emaTestData(emaVec)
        outcomes.append(EnterExits.checkShort(context, ema, priceVec))

    assert np.all([outcomes[i]==knownOutcomes[i] for i in range(len(outcomes))]), "Results do not match"

def test_checkSellLong():
    """ Two testing conditions
    price<fast: True
    price>fast: False
    """
    
    knownOutcomes = [True, False] # vector containing outcomes
    outcomes = [] # empty list for appending outcomes

    # intialize all inputs
    price = np.ones(2)*97
    fast = np.array([98, 96])
    slow = np.array([99, 97])
    fast1 = np.array([100, 97])
    macd = np.ones(2)*100
    signalLine = np.array([101,99])

    # intialize context class
    context = testutils.contextNoSim()

    # loop through and calcualte checkSellLong
    for i in range(2):
        emaVec = np.array([fast[i], fast1[i], slow[i], slow[i], 0, 0, macd[i], macd[i], signalLine[i] ])
        priceVec = testutils.Price(price[i],price[i],price[i])
        ema = testutils.emaTestData(emaVec)
        outcomes.append(EnterExits.checkSellLong(context, ema, priceVec))

        assert np.all([outcomes[i]==knownOutcomes[i] for i in range(len(outcomes))]), "Results do not match"

def test_checkSellShort():
    """ Two testing conditions
    price>fast: True
    price<fast: False
    """
    
    knownOutcomes = [True, False] # vector containing outcomes
    outcomes = [] # empty list for appending outcomes

    # intialize all inputs
    price = np.ones(2)*97
    fast = np.array([96, 98])
    slow = np.array([99, 97])
    fast1 = np.array([100, 97])
    macd = np.ones(2)*100
    signalLine = np.array([101,99])

    # intialize context class
    context = testutils.contextNoSim()

    # loop through and calcualte checkSellShort
    for i in range(2):
        emaVec = np.array([fast[i], fast1[i], slow[i], slow[i], 0, 0, macd[i], macd[i], signalLine[i] ])
        priceVec = testutils.Price(price[i],price[i],price[i])
        ema = testutils.emaTestData(emaVec)
        outcomes.append(EnterExits.checkSellShort(context, ema, priceVec))

        assert np.all([outcomes[i]==knownOutcomes[i] for i in range(len(outcomes))]), "Results do not match"

def test_checkCross():
    """ 4 testing conditions:
    fast>slow and fast1<slow1: True - long
    fast>slow and fast1>slow1: False
    fast<slow and fast1>slow1: True - short
    fast<slow and fast1<slow1: False
    """
    
    # vectors containing outcomes
    knownOutcomes     = [True, False, True, False] 
    longBoolOutcomes  = [True, False, False, False]
    shortBoolOutcomes = [False, False, True, False]

    # empty lists for appending outcomes
    outcomes =   [] 
    longBools =  []
    shortBools = []

    # intialize all inputs
    fast = np.array([99, 99, 96, 96])
    slow = np.array([96, 97, 100, 101])
    fast1 = np.array([96, 98, 97, 95])
    slow1 = np.array([97, 97, 96, 101])
    macd = np.ones(4)*100
    signalLine = np.array([101,99,100,100])

    # loop through and calcualte checkCross
    for i in range(4):
        context = testutils.contextNoSim() # intialize/reset context class
        emaVec = np.array([fast[i], fast1[i], slow[i], slow1[i], 0, 0, macd[i], macd[i], signalLine[i]])
        ema = testutils.emaTestData(emaVec)
        outcomes.append(EnterExits.checkCross(context, ema))
        longBools.append(context.longBool)
        shortBools.append(context.shortBool)

    assert np.all([outcomes[i]==knownOutcomes[i] for i in range(len(outcomes))]), "Results do not match"
    assert np.all([shortBools[i]==shortBoolOutcomes[i] for i in range(len(outcomes))]), "Shorts do not match"
    assert np.all([longBools[i]==longBoolOutcomes[i] for i in range(len(outcomes))]), "Longs do not match"

def test_checkEnter():
    """ This test has the following conditions:
    Price<fast<slow and fast<fast1: checkShort is True
    Price>fast>slow and fast>fast1: checkLong is True
    Price>fast<slow and fast<fast1: False
    Price>fast>slow and fast<fast1: False
    """
    
    # vectors containing outcomes
    knownOutcomes     = [True, True, False, False] 
    longBoolOutcomes  = [False, True, False, False]
    shortBoolOutcomes = [True, False, False, False]

    # empty lists for appending outcomes
    outcomes =   [] 
    longBools =  []
    shortBools = []

    # intialize all inputs
    price = np.ones(4)*98
    fast = np.array([99, 97, 96, 96])
    slow = np.array([100, 96, 100, 95])
    fast1 = np.array([100, 96, 97, 99])
    slow1 = np.array([97, 97, 96, 101])
    macd = np.ones(4)*100
    signalLine = np.array([101,98,100,100])

    # loop through and calcualte checkCross
    for i in range(4):
        # Get ema class
        emaVec = np.array([fast[i], fast1[i], slow[i], slow1[i], 0, 0, macd[i], macd[i], signalLine[i]])
        ema = testutils.emaTestData(emaVec)

        context = testutils.contextNoSim() # intialize/reset context class
        priceVec = testutils.Price(price[i],price[i],price[i]) # get price class

        # check to enter
        EnterExits.checkEnter(context, ema, priceVec)

        # record flags
        outcomes.append(context.enter_flag)
        longBools.append(context.longBool)
        shortBools.append(context.shortBool)

    assert np.all([outcomes[i]==knownOutcomes[i] for i in range(len(outcomes))]), "Results do not match"
    assert np.all([shortBools[i]==shortBoolOutcomes[i] for i in range(len(outcomes))]), "Shorts do not match"
    assert np.all([longBools[i]==longBoolOutcomes[i] for i in range(len(outcomes))]), "Longs do not match"
