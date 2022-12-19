### Imports
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

import csv
import collections
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pdb
import pytz
import shutil
import sys
import time
import zipfile
from email.message import EmailMessage
import smtplib
import ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
import os.path


class Price():
    """ This class takes in a context structure and outputs a data frame with colmns 
    of last price, ask price, bid price, and mid price. Note when moving this function to the actual algo,
    update security to context.security and get rid of sim.show..."""
    def __init__(self,context,data):
        self.ask=data.parentTrader.show_real_time_price(context.security,'ask_price')
        self.bid=data.parentTrader.show_real_time_price(context.security,'bid_price')
        self.last=data.parentTrader.show_real_time_price(context.security,'last_price')
        self.mid=round((self.ask + self.bid) / 2, 2) # calculate midpoint price   


#TODO put all price functions into class Price
def modifyPrice(context,price, i, multiplier:np.array = np.array([[0,5, 7, 9, 11, 50],
                                                                  [0,0.0, 0.0, 0.0, 0.0, 0.0]])):
    """This function takes in a price, an order, and number of time steps the 
    order has been tried to be filled and outputs a new price. A multipler is used as
    a function of a lookup table to calculate the new price."""
    
    # TODO find optimal lookup table

    if context.shortBool: # if we are modifying a short sale, increase the price, decrease for long
        mult = 0.5 + np.interp(i,multiplier[0],multiplier[1])/2 # interpolate i over multiplier
    else:
        mult = 0.5 - np.interp(i,multiplier[0],multiplier[1])/2
    
    newPrice = np.round((price.ask + price.bid)*mult,2) # calculate new price based on lookup table of i
    
    return newPrice

def calcTrailingStop(context, price, mag: float = 5, percentBool: bool=True, shortBool: bool=False):
    """ This function takes inputs of:
    - Context structure
    - Price (USD)
    - Magnitude (USD or %), If percentage is used, use the magnitude of the percentage (i.e. 5, not 0.05 for 5%)
    - boolean flag which determines whether to use percentage or absolute value
    - Boolean flag for long or short sale
     and calculates a trailing stop price. """

    if shortBool: # We are holding short
        if percentBool: # Calculate trailing stop using percentage
            tsPriceNew=price.mid*(1+mag/100)
        else: # Calculate trailing stop using absolute value in USD
            tsPriceNew=price.mid+mag
    else: # We are holding long
        if percentBool: # Calculate trailing stop using percentage
            tsPriceNew=price.mid*(1-mag/100)
        else: # Calculate trailing stop using absolute value in USD
            tsPriceNew=price.mid-mag
            # TODO put context.tsPrice
    return tsPriceNew

def updateTrailingStop(context, price, mag: float = 5, tsPrice: float= np.NAN, percentBool: bool=True, shortBool: bool=False, newTsBool: bool=False):
    """ This function takes inputs of:
    - Context structure
    - Price (USD)
    - Magnitude (USD or %), If percentage is used, use the magnitude of the percentage (i.e. 5, not 0.05 for 5%)
    - Previous trailing stop price (if it exists), else leave empty
    - boolean flag which determines whether to use percentage or absolute value
    - Boolean flag for long or short sale
    - Boolean for whether or not this is the first time we are calculating the trailing stop price
     and determines whether or not to update the trailing price. 
     
     Conditions for updating trailing stop price:
     
     - We hold a short position and the price falls below  the previous trailing stop price
     - we hold a long position and the price rise above the previous trailing stop price
     
     # TODO confirm this is correct, we may have to adjust when the price goes above a previous peak, though
     this can be an easier way to calculate so we dont have to store previous maximum data

     """    
    
    if newTsBool:
        tsPriceNew=calcTrailingStop(context, price, mag=mag, percentBool=percentBool, shortBool=shortBool)
    elif shortBool and percentBool:
        if tsPrice < price.mid*(1+mag/100):
            tsPriceNew=calcTrailingStop(context, price, mag=mag, percentBool=percentBool, shortBool=shortBool)
    elif shortBool and not percentBool:
        if tsPrice < price.mid+mag:
            tsPriceNew=calcTrailingStop(context, price, mag=mag, percentBool=percentBool, shortBool=shortBool)
    elif not shortBool and percentBool:
        if tsPrice > price.mid*(1+mag/100):
            tsPriceNew=calcTrailingStop(context, price, mag=mag, percentBool=percentBool, shortBool=shortBool)
    elif not shortBool and not percentBool:
        if tsPrice > price.mid+mag:
            tsPriceNew=calcTrailingStop(context, price, mag=mag, percentBool=percentBool, shortBool=shortBool)
    else:
        tsPriceNew=tsPrice
        
    return tsPriceNew

def processHistoricalData(min1Data, min5Data, sim,  nVec: list = [13, 48, 8]):
    """This function will take in your 1 minute data, 5 minute data (must both be dataFrames),and n vector 
    (vector containing periods for fast, slow, and Tline), loops through the close times, and calculates/stores
    EMA at relevant Time TODO clean this up to only calculate one time step"""
    
    min1Data=sim.request_historical_data(symbol('SPY'), '1 secs', '2000 S')
    min5Data=sim.request_historical_data(symbol('SPY'), '5 secs', '2000 S')

    nVec = [13, 48, 8]

    maxPeriod=5*26*9 # max start periods for 5 minute data at 26 period filter (not quite sure about the 9 yet)
    price=[]
    Time=[]

    # Initialize structure (use dataframe for now) # TODO make a class eventually
    ema=pd.DataFrame(columns=["fast", "fast_n", "fast_1", "fast_2", 
                    "slow", "slow_n", "slow_1", "fast_slope", "slow_slope",
                    "t_line", "t_line_n", "t_line_1", "t_slope", 
                    "fast_length1", "slow_length_1", "fast_length", "slow_length",
                    "macd", "macd_1", "macd_slope", "macd_9" ])


    # get time in minutes from data start
    min1Data.EpochTime=(min1Data.index-min1Data.index[0]).total_seconds()
    min5Data.EpochTime=(min5Data.index-min5Data.index[0]).total_seconds()

    #Start loop from maximum period to ensure each EMA function has time to spool up
    goodTime=min1Data.EpochTime[min1Data.EpochTime>maxPeriod] 
    goodTime=goodTime[:2335-590] # doing this because we are failing due to slightly less 5min data
    for iter,t in enumerate(goodTime):
        if iter>len(goodTime)-6:
            break
        i=np.argmax(t==min1Data.EpochTime) # get index of time vector
        # get data to put in EMA
        tempPrice=min1Data.close.iloc[i] # price at time t
        temp1Data=min1Data.iloc[:i] # historical values at time t

        # get 5 min data
        ind5=(np.argmax(min5Data.EpochTime>t)) # find index in 5 min data which is > than t
        # temp5Price=min5Data.close.iloc[(ind5-1)] # get last 5 minute data price
        temp5Data=min5Data[:(ind5)] # get historical 5 minute values at time t

        # loop through each time step for 1 and 5 minute 
        temp = IndicatorCalculations.calcEMA(temp1Data, temp5Data, tempPrice, nVec=nVec) # calculate EMA
        # append dataframe with new row of data
        ema=ema.append(temp)
        price.append(tempPrice)
        Time.append(i)
    ema.index=np.arange(len(ema.index))
    ema.insert(0,"time",Time)
    ema.insert(1,"price",price)
    return ema

def initializeJupyter(sim):
    """ This function is used to generate a dummy "context" dataframe for testing purposes. Note that you need to input an instance 
    of ibpy for this function to work"""

    class Context:
        
        def __init__(self, sim):
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
            self.trail_1 = 0.1
            self.trail_2 = 0.2
            self.new_ts_flag = False
            self.double_flag = False
            self.exit_flag = False
            self.exitTimerFlag = False
            self.shares = None
            self.order = None
            self.double_order = None
            self.exit_order = None
            self.entry_time = None
            self.exit_time = None
            self.counter = collections.deque()
            self.macdDelta = 0.0
            self.price_1 = sim.show_real_time_price(self.security, 'last_price')
            self.price_n = sim.show_real_time_price(self.security, 'last_price')
            self.value = 100000.00
            self.file_name="log.txt"
            self.sTime = -9999
    
    context = Context(sim)
    
    return context



def doLogging(context,data,ema,price):
    """ This function logs data given a price, ema, and file name. Note this function will be
    phased out eventually, just putting it in to get the 1st cut algo running."""
   
    with open(context.file_name, 'a', newline='') as csvfile:
        log=[str(context.sTime.timestamp()), str(ema.fast), str(ema.fast_1), str(ema.slow), str(ema.t_line), str(ema.macd), str(ema.macd_9), 
        str(context.longBool), str(context.shortBool), str(context.long_flag), str(context.short_flag),str(context.enter_flag), 
        str(context.entry_flag), str(context.exit_flag), str(price.ask), str(price.bid), str(price.last), str(price.mid),
        str(context.portfolio.portfolio_value),str(context.portfolio.positions_value),str(context.portfolio.cash)]
        csvfile.write(', '.join(log))
        csvfile.write("\n")
        
def dailyLogging(context,data,ema,price):
    """ This function logs data given a price, ema, and file name. Note this function will be
    phased out eventually, just putting it in to get the 1st cut algo running."""
   
    with open(context.log_name, 'a', newline='') as logFile:
        log=[str(context.sTime.timestamp()), str(ema.fast), str(ema.fast_1), str(ema.slow), str(ema.t_line), str(ema.macd), str(ema.macd_9), 
        # flags
        str(context.longBool), str(context.shortBool), str(context.long_flag), str(context.short_flag),str(context.enter_flag),
        str(context.entry_flag), str(context.exit_flag),str(context.exitTimerFlag), str(context.saleFlag), str(context.exitTouchTime.timestamp()),
        # price
        str(price.ask), str(price.bid), str(price.last), str(price.mid),
        # candles
        str(context.hist_1min.open[-1]),str(context.hist_1min.high[-1]),str(context.hist_1min.low[-1]),str(context.hist_1min.close[-1]),str(context.hist_1min.volume[-1]),
        # portfolio
        str(context.positionSize),str(context.portfolio.portfolio_value),str(context.portfolio.positions_value),str(context.portfolio.cash)]
        logFile.write(', '.join(log))
        logFile.write("\n")

def flag_reset(context):
    """This function will reset all flags once some condition is met, come
    back with more info later"""
    context.entry_flag =     False
    context.enter_flag =     False
    context.long_flag =      False
    context.short_flag =     False
    context.longBool =       False
    context.shortBool =      False
    context.entry_price =    None
    context.stop_price =     None
    context.new_stop_price = None
    context.ts_price_1 =     None
    context.ts_price_2 =     None
    context.trail_1 =        0.1
    context.trail_2 =        0.2
    context.new_ts_flag =    False
    context.double_flag =    False
    context.exit_flag =      False
    context.exitTimerFlag =  False
    context.exitTouchTime =  context.sTime
    context.saleFlag =       False
    context.order =          None
    context.double_order =   None
    context.shares =         0
    context.entry_time =     None
    context.exit_time =      None

def initialize(context,data):
    """ This function initializes all variables and flags at the beginning of a session"""
    context.run_once = False  # To show if the handle_data has been run in a day
    context.security = symbol('SPY')  # Define a security for the following part
    context.entry_flag = False # flag that we currently own stock
    context.long_flag = False # flag that we currently own long
    context.short_flag = False # flag that we currently own short
    context.hist_1min = data.parentTrader.request_historical_data(context.security, '1 min', '16000 S')
    context.hist_5min = data.parentTrader.request_historical_data(context.security, '5 mins', '31300 S')
    context.macd_list = []
    context.entry_price = None
    context.enter_flag = False # flag to buy stock
    context.longBool = False # flag to determine if we are buying long
    context.shortBool = False # flag to determine if we are buying short
    context.stop_price = None
    context.new_stop_price = None
    context.ts_price_1 = None
    context.ts_price_2 = None
    # context.trail = 0.1
    context.trail_1 = 0.1
    context.trail_2 = 0.2
    context.new_ts_flag = False
    context.double_flag = False
    context.exit_flag = False
    context.exitTimerFlag =  False
    context.exitTouchTime = np.NaN
    context.saleFlag = False
    context.shares = None
    context.order = None
    context.double_order = None
    context.exit_order = None
    context.entry_time = None
    context.exit_time = None
    context.price_1 = data.parentTrader.show_real_time_price(context.security, 'last_price')
    context.price_n = data.parentTrader.show_real_time_price(context.security, 'last_price')
    context.value = 100000.00
    context.file_name="N/A"
    context.sTime = -9999
    print('entry_flag: ', context.entry_flag,
          '\nlong_flag: ', context.long_flag,
          '\nshort_flag: ', context.short_flag,
          '\nentry_price: ', context.entry_price,
          '\nnew_ts_flag; ', context.new_ts_flag,
          '\ndouble_flag: ', context.double_flag,
          '\norder: ', context.order)
    
def getEndOfDayCandles(context,data):
    # collect daily price data and save to log
    dailyPriceData = data.parentTrader.request_historical_data(symbol('SPY'), '1 min', '23400 S')
    dailyPriceData.to_csv(r"Log\Daily_Price_Data_"+str(datetime.date.today())+".csv")
    
def closeOutTasks(context, data):
    # generate daily price data for later review and plotting
    getEndOfDayCandles(context,data)
    
    # Generate daily plots
    generateDailyPlots()
    
    # move/zip all files before sending email
    ZipFilesForDelivery()
    
    # send out email for end of day summary
    sendEmailEndOfDay()
    
def fixBoolData(logData):
    """ This function takes in the daily log data and converts the long/shortbool
    data and converts it to boolean from string format."""
    
    for parm in ([logData.shortBool,logData.longBool, logData.shortFlag,logData.longFlag, logData.enterFlag, logData.entryFlag, logData.exitFlag, logData.exitTimerFlag, logData.saleFlag]):
        for i in range(len(parm.values)):
            if type(parm.iloc[i])==str:
                if parm.iloc[i].split()[0].lower()=="false":
                    parm.iloc[i]=False
                elif parm.iloc[i].split()[0].lower()=="true":
                    parm.iloc[i]=True
                else:
                    print("error: string must be true or false")
            
    return logData

def calcEntryStatus(logData):
    """ This function takes in a dataframe loaded from the daily log data
    and checks for true/false and ouputs and array with the following indices:
        1 for holding long position
        0 for holding no position
        -1 for holding short position"""
    # intialize array
    testArray = np.zeros_like(logData.longBool.values)-9999

    for i in range(len(logData.longBool.values)):
        if logData.longBool.iloc[i]==True and logData.shortBool.iloc[i]==False:
            testArray[i] = 1
        elif logData.longBool.iloc[i]==False and logData.shortBool.iloc[i]==True:
            testArray[i] = -1
        elif logData.longBool.iloc[i]==False and logData.shortBool.iloc[i]==False:
            testArray[i] = 0
            
    return testArray


def sendEmailEndOfDay(email_sender:str = "lanecapitalgroup.feeney@gmail.com",
                      email_receiver:list = ["richfeeney6@gmail.com","lanecapitalgroup1@gmail.com", "mellingrady@gmail.com","lane.kyle0209@gmail.com","foley802@gmail.com"],
                      attachments: list = [r"Output\OutputData_"+str(datetime.date.today())+".zip"]):

    pnl, count = getPl() # get profit/loss and number of trades to put in email

    email_password = "bhpoxfksvoubpaxl"
    subject = "Daily Plots "+str(datetime.date.today())
    body = """See attached for plots and data for """+str(datetime.date.today())+"\nDaily Profit: "+str(pnl)+"$\nNumber of Trades: "+str(count)

    for email in email_receiver:
        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Setup the attachment
        filename = os.path.basename(attachments[0])
        attachment = open(attachments[0], "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        # Attach the attachment to the MIMEMultipart object
        for a in attachments:
            with open(a,'rb')as f:
                msg.attach(MIMEApplication(f.read(), Name=a.split("\\")[-1]))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_sender, email_password)
        text = msg.as_string()
        server.sendmail(email_sender, email, text)
        server.quit()
        
def generateDailyPlots():
    # create new directory for output plots
    newDir = r"Output\candlestick_"+str(datetime.date.today())
    if not os.path.isdir(newDir):
        os.mkdir(newDir)

    logData, priceData = loadAndCleanData() # load and clean up log data

    # define x limits to plot hourly data
    xlim = Utils.getPlottingHourLimits(logData)

    # plot the full days plot
    outputFileName = newDir+"\\DailyPlot"+str(datetime.date.today())+"_full"+".png"
    Plotters.plotDailyCandleStickMacd(priceData, logData, emaList = ['fast', 'slow'], outPutFileName=outputFileName,saveFig=True)

    # generate hourly plots
    for x in xlim:
        outputFileName = newDir+"\\DailyPlot"+str(datetime.date.today())+"_"+str(x[0].hour)+".png"
        Plotters.plotDailyCandleStickMacd(priceData, logData, emaList = ['fast', 'slow'], x=x,outPutFileName=outputFileName,saveFig=True)
        
def zipFolder(zipPath, zipName):
    """This function takes in a path which contains the files to be zipped and a zip file name. Note that the zip file cannot be placed in 
    the zipPath or else it goes in an infinte loop."""
    with zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for folder_name, subfolders, filenames in os.walk(zipPath):
            print(folder_name)
            for filename in filenames:
                print(filename)
                file_path = os.path.join(folder_name, filename)
                zip_ref.write(file_path, arcname=os.path.relpath(file_path, zipPath))

    zip_ref.close()
    
def ZipFilesForDelivery():
    """ This function runs at the end of the day and copies output logs to a predetermined directory and zips the files """
    
    #make directory to pass folders
    zipPath = r"Output\candlestick_"+str(datetime.date.today())
    if not os.path.isdir(zipPath):
        os.mkdir(zipPath)

    # pass daily log, price data, and trader log
    logPath = r"Log\Daily_Log_"+str(datetime.date.today())+".csv"
    pricePath = r"Log\Daily_Price_Data_"+str(datetime.date.today())+".csv"
    traderPath = r"Log\TraderLog_"+str(datetime.date.today())+".txt"

    # copy files to new directory
    shutil.copy(logPath,zipPath+"\\"+logPath.split("\\")[-1])
    shutil.copy(pricePath,zipPath+"\\"+pricePath.split("\\")[-1])
    shutil.copy(traderPath,zipPath+"\\"+traderPath.split("\\")[-1])

    # Create a zip folder
    zipName = zipPath+"\\..\\OutputData_"+str(datetime.date.today())+".zip"
    Utils.zipFolder(zipPath, zipName)
    
def cleanLogData(logData):
    """ This function takes in the log data and cleans it up so it can be used for plotting and other tasks"""
    logData = logData[logData["time"]!="time"] # remove columns which result from rerunning algo in the day

    for i in range(len(logData.time)): # convert loop parameters from string to floating point
        logData.time.iloc[i]=np.double(logData.time.iloc[i])
        logData.fast.iloc[i]=float(logData.fast.iloc[i])
        logData.slow.iloc[i]=float(logData.slow.iloc[i])
        logData.macd.iloc[i]=float(logData.macd.iloc[i])
        logData.fast1.iloc[i]=float(logData.fast1.iloc[i])
        logData.tLine.iloc[i]=float(logData.tLine.iloc[i])
        logData.exitTouchTime.iloc[i]=np.double(logData.exitTouchTime.iloc[i])
        logData.askPrice.iloc[i]=float(logData.askPrice.iloc[i])
        logData.bidPrice.iloc[i]=float(logData.bidPrice.iloc[i])
        logData.lastPrice.iloc[i]=float(logData.lastPrice.iloc[i])
        logData.midPrice.iloc[i]=float(logData.midPrice.iloc[i])
        logData.open.iloc[i]=float(logData.open.iloc[i])
        logData.high.iloc[i]=float(logData.high.iloc[i])
        logData.low.iloc[i]=float(logData.low.iloc[i])
        logData.close.iloc[i]=float(logData.close.iloc[i])
        logData.volume.iloc[i]=float(logData.volume.iloc[i])
        logData.positionSize.iloc[i]=int(logData.positionSize.iloc[i])
        logData.portfolioValue.iloc[i]=float(logData.portfolioValue.iloc[i])
        logData.positionValue.iloc[i]=float(logData.positionValue.iloc[i])
        logData.cash.iloc[i]=float(logData.cash.iloc[i])
    logData = fixBoolData(logData)
    return logData

def getPlottingHourLimits(logData):
    """This function takes in logData and outputs a list of tuples of datetimes to be used as the x axis in plots"""
    
    # get the unique hours in the log data
    # dates = npL.unique(np.array([datetime.datetime.fromtimestamp(logData.time.values[i]).hour for i in range(len(logData.time))]))
    dates = np.arange(7,14)
    # get todays date time
    today=datetime.datetime.today()
    
    # get list of tuples with monotonically increasing unique hours
    xlim = [(datetime.datetime(today.year,today.month,today.day,dates[i],31,0), datetime.datetime(today.year,today.month,today.day,dates[i+1],31,0)) for i in range(len(dates)-1)]
    
    return xlim

def loadAndCleanData(priceDataPath: str = r"log\Daily_Price_Data_"+str(datetime.date.today())+".csv",
                    logDataPath: str = r"Log\Daily_Log_"+str(datetime.date.today())+".csv"):
    """ This function loads in the price and log data, cleans it up and returns it. """
    
    # load price data
    priceColumns = ["date", "time", "open", "high", "low", "close", "volume"]
    priceData = pd.read_csv(priceDataPath, header=1, names=priceColumns)
    # convert the time into datetime
    priceData['date'] =  np.array([datetime.datetime.fromtimestamp(f) for f in priceData.time.values])

    # load ema data
    logColumns = ["time", "fast", "fast1", "slow", "tLine", "macd", "signalLine", "longBool", "shortBool", "longFlag", "shortFlag", 
                "enterFlag", "entryFlag", "exitFlag", "exitTimerFlag", "saleFlag", "exitTouchTime", "askPrice", "bidPrice", 
                "lastPrice", "midPrice", "open", "high", "low", "close", "volume", "positionSize", "portfolioValue", "positionValue", "cash"]
    logData = pd.read_csv(logDataPath, header=0, names=logColumns)
    logData = cleanLogData(logData)
    logData['date'] = np.array([datetime.datetime.fromtimestamp(float(f)) for f in logData.time.values])
    
    return logData, priceData

def getPl():
    """ This function is used to get # of trades and P&L for the trading day """
    count=0
    logData, priceData = loadAndCleanData()

    # get profit/loss for day
    pnl = np.round(logData.portfolioValue.iloc[-1]-logData.portfolioValue.iloc[0],2)
    
    # get number of trades by looping through and seeing when position size changes (but not to zero since that would indicate a sale)
    for i in range(1,len(logData.positionSize.values)):
        if logData.positionSize.values[i]!=logData.positionSize.values[i-1] and logData.positionSize.values[i]!=0:
            count+=1

    return pnl, count