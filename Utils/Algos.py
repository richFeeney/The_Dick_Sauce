import numpy as np
import pandas as pd

def algoBase(context, ema, price, longBool, shortBool):
    """This function takes in  a price, ema, and security and checks if we enter/exit 
    at the current time step, and outputs an enter and exit flag"""
    
    # TODO check to buy even if we own
    # TODO check for the chop
    # TODO fix flag stuff
    # TODO validate algorithm entry/exit points
    
    enterFlag=False
    exitFlag=False
    # if we dont own stock, check to enter
    if not longBool and not shortBool: 
        enterFlag,longBool,shortBool =checkEnter(context,ema,price,longBool,shortBool) # check if we want to enter
    else: # if we own, check to exit
        exitFlag,longBool,shortBool=checkExit(context,ema,price,longBool,shortBool)# if we have security, check to exit
    if exitFlag:
        generateOrders(context,price)
        
    return enterFlag, exitFlag,longBool,shortBool
