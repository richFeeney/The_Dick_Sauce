"""
The sauce algorithm for the commons

@author: Grady Mellin
developed by Lane Capital Group

"""

### Imports
import datetime

import pytz

# from MyFunctions.EMA import *
from IBridgePy.constants import OrderStatus
# from IBridgePy.quantopian import LimitOrder,TrailStopOrder
import csv


def flag_reset(context):
    """This function will reset all flags once some condition is met, come
    back with more info later -rmf"""
    context.entry_flag = False
    context.enter_flag = False
    context.long_flag = False
    context.short_flag = False
    context.entry_price = None
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
    context.TG_flag = False
    context.order = None
    context.double_order = None
    context.shares = None
    context.entry_time = None
    context.exit_time = None


def initialize(context):
    context.run_once = False  # To show if the handle_data has been run in a day
    context.security = symbol('SPY')  # Define a security for the following part
    context.entry_flag = False # flag that we currently own stock
    context.long_flag = False
    context.short_flag = False
    context.hist_1min = request_historical_data(context.security, '1 min', '16000 S')
    # context.hist_2min = retry_request_hist(context.security, '2 mins', '6000 S')
    context.hist_5min = request_historical_data(context.security, '5 mins', '31300 S')
    context.macd_list = []
    context.entry_price = None
    context.enter_flag = False # flag to buy stock
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
    context.TG_flag = False
    context.shares = None
    context.order = None
    context.double_order = None
    context.exit_order = None
    context.entry_time = None
    context.exit_time = None
    context.price_1 = show_real_time_price(context.security, 'last_price')
    context.price_n = show_real_time_price(context.security, 'last_price')
    context.value = 100000.00
    print('entry_flag: ', context.entry_flag,
          '\nlong_flag: ', context.long_flag,
          '\nshort_flag: ', context.short_flag,
          '\nentry_price: ', context.entry_price,
          '\nnew_ts_flag; ', context.new_ts_flag,
          '\ndouble_flag: ', context.double_flag,
          '\norder: ', context.order)


def handle_data(context, data):
    current_date = datetime.date.today()
    current_date_string = str(current_date)
    extension = ".csv"
    file_name = "log_" + current_date_string + extension
    # with open(file_name, 'a', newline='') as csvfile:
    #     fieldnames = [
    #         "Time", "Entry Type", "Price", "Fast(EMA(13))", "Slow(EMA(48))",
    #         "Fast_Length(12)", "Slow_Length(26)", "MACD", "MACD(9)"
    #     ]
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writerow({'Time': sTime, "Entry Type": "none" , "Price": price, "Fast(EMA(13))": fast, " Slow(EMA(48))": slow,
    #      "Fast_Length(12)": fast_length, "Slow_Length(26)": slow_length, "MACD": macd, "MACD(9):" macd_9})
    sTime = get_datetime('US/Eastern')

    price = show_real_time_price(context.security, 'last_price')
    price_ask = show_real_time_price(context.security, 'ask_price')
    price_bid = show_real_time_price(context.security, 'bid_price')
    price_mid = round((price_ask + price_bid) / 2, 2)


    if sTime.weekday() <= 4 and 10 <= sTime.hour < 16:  # Only trades on weekdays
        # if sTime.second == 1 or sTime.second == 31:
            # try:
            # context.hist_2min = request_historical_data(context.security, '2 mins', '6000 S')
            # context.hist_1min = request_historical_data(context.security, '1 min', '26000 S')
            # context.hist_5min = request_historical_data(context.security, '5 mins', '31300 S')
            # except RuntimeError:
        if sTime.second == 1 or sTime.second == 21 or sTime.second == 41:
            # try:
            # context.hist_2min = request_historical_data(context.security, '2 mins', '6000 S')
            context.hist_1min = request_historical_data(context.security, '1 min', '26000 S')
            context.hist_5min = request_historical_data(context.security, '5 mins', '31300 S')
            # context.price_n = show_real_time_price(context.security, 'last_price')
            #     pass
        ### Historical data and EMAS
        # hist_2min_1 = context.hist_2min[:-1]
        # print(context.hist_5min, context.hist_2min)
        
        
        ##### Calculate EMAs and Inputs ##### 
        # TODO - turn this into one function to fetch all data
        # TODO - functionalize each loading too to avoid typos
        
        
        # fast filtered data
        fast = EMA(context.hist_1min.close[:-1], price, 13)
        # fast = EMA(context.hist_1min.close[:-1], context.price_n, 13)
        fast_n = EMA(context.hist_1min.close[:-1], price, 13)
        fast_1 = EMA_1(context.hist_1min.close[:-1], 13)
        fast_2 = EMA_1(context.hist_1min.close[:-2], 13)
        
        # slow filtered data
        # slow = EMA(context.hist_1min.close[:-1], context.price_n, 48)
        slow = EMA(context.hist_1min.close[:-1], price, 13)
        slow_n = EMA(context.hist_1min.close[:-1], price, 48)
        slow_1 = EMA_1(context.hist_1min.close[:-2], 48)
        fast_slope = round((fast_n - fast_2)/2, 4)
        slow_slope = round((slow_n - slow_1) / 2, 4)
        
        # calculate t line
        # t_line = EMA(context.hist_1min.close[:-1], context.price_n, 8)
        t_line = EMA(context.hist_1min.close[:-1], price, 13)
        t_line_n = EMA(context.hist_1min.close[:-1], price, 8)
        t_line_1 = EMA_1(context.hist_1min.close[:-2], 8)
        t_slope = round((t_line_n-t_line_1) / 2, 4)
        
        # dont know what this is
        fast_length_1 = EMA_1(context.hist_5min.close[:-2], 12)
        slow_length_1 = EMA_1(context.hist_5min.close[:-2], 26)
        # fast_length_n = EMA(context.hist_5min.close[:-1], price, 12)
        fast_length = EMA_1(context.hist_5min.close, 12)
        # slow_length_n = EMA(context.hist_5min.close[:-1], price, 26)
        slow_length = EMA_1(context.hist_5min.close, 26)
        
        # calculate MACD
        macd_1 = fast_length_1 - slow_length_1
        macd = round(fast_length - slow_length, 2)
        macd_slope = round((macd-macd_1)/2, 4)
        macd_9 = MACD(context.hist_5min[:-1], macd, 9)

        print(sTime, "Price:", price, "Mid-Price:", price_mid, "EMA(13)[-1]:", fast_1, "Fast(EMA(13)):", fast,
              "Slow(EMA(48)):", slow, "T LineEMA(8):", t_line, "T LineEMA(8)_2:", t_line_n ,"Fast_Length(12):", fast_length, "Slow_Length(26):",
              slow_length, "fast slope:", fast_slope, "Slow slope:", slow_slope, "t slope:", t_slope)

        ##Check if in position
        if context.order is None: # does this mean that we dont have stock currently?
            ###Long entry conditions
            if (fast > fast_1) and (slow_slope >= 0 or macd > macd_9):
                if (fast_slope >= (slow_slope + 0.02) and t_slope >= (fast_slope + 0.015)) or (t_slope >= 0.03): # TODO fix these hard coded contants
                    if context.price_1 > t_line >= price: # if price is over T line, buy
                        context.enter_flag = True # buy
                else: # we already have stock?
                    if (fast > slow) and context.price_1 > fast >= price:
                        context.enter_flag = True
                if context.enter_flag:
                    if context.entry_flag:
                        print("already in position")
                    elif not context.entry_flag:
                        print("enter long")
                        context.entry_price = price_mid
                        context.shares = int(context.value / price_mid)
                        context.ts_price_1 = price_mid - context.trail_1
                        context.ts_price_2 = price_mid - context.trail_2
                        context.order = order(context.security, context.shares, LimitOrder(price_mid),
                                              accountCode='default')
                        if get_order_status(context.order) in [OrderStatus.FILLED, OrderStatus.PRESUBMITTED,
                                                               OrderStatus.SUBMITTED]:
                            context.entry_time = sTime
                            context.entry_flag = True
                            context.long_flag = True
                            with open(file_name, 'a', newline='') as csvfile:
                                fieldnames = [
                                    "Time", "Entry Type", "Price", "Fast(EMA(13))", "Slow(EMA(48))",
                                    "Fast_Length(12)", "Slow_Length(26)", "MACD", "MACD(9)"
                                ]
                                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                writer.writerow({'Time': sTime, 'Entry Type': "Long",
                                                 'Price': price, 'Fast(EMA(13))': fast, 'Slow(EMA(48))': slow,
                                                 'Fast_Length(12)': fast_length, 'Slow_Length(26)': slow_length,
                                                 "MACD": macd, 'MACD(9)': macd_9})
                            print('entry_flag: ', context.entry_flag, "\n", 'long_flag: ', context.long_flag)
            ###Short entry conditions
            elif (fast < fast_1) and (slow_slope >= 0 or macd < macd_slope):
                # (slow_slope <= 0)
                if (fast_slope <= (slow_slope - 0.02) and t_slope <= (fast_slope - 0.015)) or (t_slope <= -0.3):
                    if context.price_1 < t_line <= price:
                        context.enter_flag = True
                else:
                    if (fast < slow) and context.price_1 < fast <= price:
                        context.enter_flag = True
                if context.enter_flag:
                    if context.entry_flag:
                        print("already in position")
                    elif not context.entry_flag:
                        print("enter short")
                        context.entry_price = price_mid
                        value = - context.value
                        context.shares = int(value / price_mid)
                        context.ts_price_1 = price_mid + context.trail_1
                        context.ts_price_2 = price_mid + context.trail_2
                        context.order = order(context.security, context.shares, LimitOrder(price_mid),
                                              accountCode='default')
                        if get_order_status(context.order) in [OrderStatus.FILLED, OrderStatus.PRESUBMITTED,
                                                               OrderStatus.SUBMITTED]:
                            context.entry_time = sTime
                            context.entry_flag = True
                            context.short_flag = True
                            with open(file_name, 'a', newline='') as csvfile:
                                fieldnames = [
                                    "Time", "Entry Type", "Price", "Fast(EMA(13))", "Slow(EMA(48))",
                                    "Fast_Length(12)", "Slow_Length(26)", "MACD", "MACD(9)"
                                ]
                                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                writer.writerow({'Time': sTime, 'Entry Type': "Short",
                                                 'Price': price, 'Fast(EMA(13))': fast, 'Slow(EMA(48))': slow,
                                                 'Fast_Length(12)': fast_length, 'Slow_Length(26)': slow_length,
                                                 "MACD": macd, 'MACD(9)': macd_9})
                            print('entry_flag: ', context.entry_flag, "\n", 'short_flag: ', context.short_flag)

        ##################### EXITS CONDITIONS
        elif get_order_status(context.order) in [OrderStatus.FILLED]:
            # print(context.ts_price_1,"    ", context.ts_price_2)
            ###In Long Position
            if context.entry_flag and context.long_flag:
                ###New Trailing Stop
                if price_mid >= (context.entry_price + 0.1) and not context.new_ts_flag:
                    print("new trailing stop")
                    context.trail_1 = 0.05
                    context.ts_price_1 = price_mid - context.trail_1
                    context.new_ts_flag = True
                    print("new trailing stop:", context.new_ts_flag)
                ###Adjust Trail
                if context.ts_price_1 < price_mid - context.trail_1:
                    context.ts_price_1 = price_mid - context.trail_1
                if context.ts_price_2 < price_mid - context.trail_2:
                    context.ts_price_2 = price_mid - context.trail_2
                elif price_mid <= context.ts_price_1:
                    print("Exit Position via Trailing Stop 1")
                    context.exit_flag = True
                    with open(file_name, 'a', newline='') as csvfile:
                        fieldnames = [
                            "Time", "Entry Type", "Price", "Fast(EMA(13))", "Slow(EMA(48))",
                            "Fast_Length(12)", "Slow_Length(26)", "MACD", "MACD(9)"
                        ]
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow({'Time': sTime, 'Entry Type': "EXIT: Trail 1",
                                         'Price': price, 'Fast(EMA(13))': fast, 'Slow(EMA(48))': slow,
                                         'Fast_Length(12)': fast_length, 'Slow_Length(26)': slow_length,
                                         "MACD": macd, 'MACD(9)': macd_9})
                elif slow_slope < 0:
                    print("Exit Position")
                    context.exit_flag = True
                    with open(file_name, 'a', newline='') as csvfile:
                        fieldnames = [
                            "Time", "Entry Type", "Price", "Fast(EMA(13))", "Slow(EMA(48))",
                            "Fast_Length(12)", "Slow_Length(26)", "MACD", "MACD(9)"
                        ]
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow({'Time': sTime, 'Entry Type': "EXIT: CrossOver",
                                         'Price': price, 'Fast(EMA(13))': fast, 'Slow(EMA(48))': slow,
                                         'Fast_Length(12)': fast_length, 'Slow_Length(26)': slow_length,
                                         "MACD": macd, 'MACD(9)': macd_9})
                ###Double Position
                if not context.double_flag and not context.exit_flag and context.price_1 > slow >= price and (fast < slow):
                    print("Double Position")
                    # amount = get_position(context.security).amount
                    context.double_order = order(context.security, context.shares, LimitOrder(price_mid),
                                                 accountCode='default')
                    context.shares *= 2
                    print(context.shares)
                    context.double_flag = True
                    print("Double Position:", context.double_flag)
                    # display_all()
            ###In Short Position
            if context.entry_flag and context.short_flag:
                ###New Trailing Stop
                if price_mid <= (context.entry_price - 0.1) and not context.new_ts_flag:
                    print("new trailing stop")
                    context.trail_1 = 0.05
                    context.ts_price_1 = price_mid + context.trail_1
                    context.new_ts_flag = True
                    print("new trailing stop:", context.new_ts_flag)
                ###Adjust Trail
                if context.ts_price_1 > price_mid + context.trail_1:
                    context.ts_price_1 = price_mid + context.trail_1
                if context.ts_price_2 > price_mid + context.trail_2:
                    context.ts_price_2 = price_mid + context.trail_2
                ################## Short Exits
                # if price_mid >= context.ts_price_2 and (fast_slope <= (slow_slope - 0.02) and t_slope <= (fast_slope - 0.015)):
                #     print("Exit Position via Trailing Stop 2")
                #     with open(file_name, 'a', newline='') as csvfile:
                #         fieldnames = [
                #             "Time", "Entry Type", "Price", "Fast(EMA(13))", "Slow(EMA(48))",
                #             "Fast_Length(12)", "Slow_Length(26)", "MACD", "MACD(9)"
                #         ]
                #         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                #         writer.writerow({'Time': sTime, 'Entry Type': "EXIT: Trail 2",
                #                          'Price': price, 'Fast(EMA(13))': fast, 'Slow(EMA(48))': slow,
                #                          'Fast_Length(12)': fast_length, 'Slow_Length(26)': slow_length,
                #                          "MACD": macd, 'MACD(9)': macd_9})
                #     context.exit_flag = True

                elif price_mid >= context.ts_price_1:
                    print("Exit Position via Trailing Stop 1")
                    with open(file_name, 'a', newline='') as csvfile:
                        fieldnames = [
                            "Time", "Entry Type", "Price", "Fast(EMA(13))", "Slow(EMA(48))",
                            "Fast_Length(12)", "Slow_Length(26)", "MACD", "MACD(9)"
                        ]
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow({'Time': sTime, 'Entry Type': "EXIT: Trail 1",
                                         'Price': price, 'Fast(EMA(13))': fast, 'Slow(EMA(48))': slow,
                                         'Fast_Length(12)': fast_length, 'Slow_Length(26)': slow_length,
                                         "MACD": macd, 'MACD(9)': macd_9})
                    context.exit_flag = True
                elif slow_slope > 0:
                    print("Exit Position")
                    with open(file_name, 'a', newline='') as csvfile:
                        fieldnames = [
                            "Time", "Entry Type", "Price", "Fast(EMA(13))", "Slow(EMA(48))",
                            "Fast_Length(12)", "Slow_Length(26)", "MACD", "MACD(9)"
                        ]
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow({'Time': sTime, 'Entry Type': "EXIT: CrossOver",
                                         'Price': price, 'Fast(EMA(13))': fast, 'Slow(EMA(48))': slow,
                                         'Fast_Length(12)': fast_length, 'Slow_Length(26)': slow_length,
                                         "MACD": macd, 'MACD(9)': macd_9})
                    context.exit_flag = True
                ###Double Position
                if not context.double_flag and not context.exit_flag and context.price_1 < slow <= price and (fast < slow):
                    print("Double Position")
                    # amount = get_position(context.security).amount
                    context.double_order = order(context.security, context.shares, LimitOrder(price_mid),
                                                 accountCode='default')
                    context.shares *= 2
                    print(context.shares)
                    context.double_flag = True
                    print("Double Position:", context.double_flag)
                    # display_all()
        elif get_order_status(context.order) not in [OrderStatus.FILLED]:
            i = int((sTime - context.entry_time).total_seconds())
            if i == 5:
                modify_order(context.order, newLimitPrice=price_mid)
                context.entry_time = sTime

            ##### Exit
        if context.exit_flag:
            if not context.double_flag:
                if context.exit_order is None:
                    exit_shares = -context.shares
                    context.exit_order = order(context.security, exit_shares, LimitOrder(price_mid),
                                               accountCode='default')
                    context.exit_time = sTime
                else:
                    if get_order_status(context.exit_order) in [OrderStatus.FILLED]:
                        context.exit_order = None
                        flag_reset(context)
                    elif get_order_status(context.exit_order) not in [OrderStatus.FILLED]:
                        i = int((sTime - context.exit_time).total_seconds())
                        if i == 5:
                            print(get_order_status(context.exit_order))
                            modify_order(context.exit_order, newLimitPrice=price_mid)
                            context.exit_time = sTime
            elif context.double_order is not None:
                if get_order_status(context.double_order) in [OrderStatus.FILLED]:
                    if context.exit_order is None:
                        exit_shares = -context.shares
                        context.exit_order = order(context.security, exit_shares, LimitOrder(price_mid),
                                                   accountCode='default')
                        context.exit_time = sTime
                    else:
                        if get_order_status(context.exit_order) in [OrderStatus.FILLED]:
                            context.exit_order = None
                            flag_reset(context)
                        elif get_order_status(context.exit_order) not in [OrderStatus.FILLED]:
                            i = int((sTime - context.exit_time).total_seconds())
                            if i == 5:
                                modify_order(context.exit_order, newLimitPrice=price_mid)
                                context.exit_time = sTime

                else:
                    pass
    if sTime.weekday() <= 4 and sTime.hour == 15 and sTime.minute == 59 and sTime.second == 59:
        close_all_positions()
        display_all()
    # flag_reset(context)
    context.price_1 = price
