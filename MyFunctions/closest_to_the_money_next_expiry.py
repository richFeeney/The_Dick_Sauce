import datetime as dt
from IBridgePy.quantopian import TrailStopOrder
import bisect


def nextExpiryDate():
    def next_weekday(d, weekday):
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return d + dt.timedelta(days_ahead)

    d = dt.date.today()

    next_monday = next_weekday(d, 0)  # 0 = Monday, 1=Tuesday, 2=Wednesday...
    next_wednesday = next_weekday(d, 2)
    next_friday = next_weekday(d, 4)
    if d.weekday() == 0 or d.weekday() == 2 or d.weekday() == 4:
        next_expiry_date = d
    elif next_monday < next_wednesday and next_monday < next_friday:
        next_expiry_date = next_monday
    elif next_wednesday < next_friday and next_wednesday < next_monday:
        next_expiry_date = next_wednesday
    else:
        next_expiry_date = next_friday
    return next_expiry_date.strftime("%Y%m%d")


def closestToMoney(dff, targetStrike, type):
    assert (isinstance(targetStrike, float))
    # A value is trying to be set on a copy of a slice from a DataFrame.
    # Try using .loc[row_indexer,col_indexer] = value instead
    df = dff.copy()  # To avoid the above error, make a copy of incoming dff
    if type == 'C':
        df['strike'] = df['security'].apply(lambda x: x.strike - targetStrike)
    elif type == 'P':
        df['strike'] = df['security'].apply(lambda x: targetStrike - x.strike)
    else:
        df['strike'] = df['security'].apply(lambda x: abs(x.strike - targetStrike))
    sorted_exp = sorted(list(set(df['strike'])))
    lc = bisect.bisect_left(sorted_exp, 0)
    return df.loc[df['strike'] == sorted_exp[lc], :]


def long_entry(context, data, price):
    if price != -1:
        closest_expiry_date = nextExpiryDate()
        ans_C = get_contract_details(secType='OPT',
                                     symbol='SPY',
                                     field='summary',
                                     currency='USD',
                                     exchange='SMART',
                                     primaryExchange='SMART',
                                     expiry=closest_expiry_date,
                                     right='C')

        df_closestToMoney_C = closestToMoney(ans_C, price, 'C')
        theContract_C = df_closestToMoney_C.iat[0, 0]
        theContract_C.primaryExchange = 'SMART'

        # tenStop = round(price * .90, 2)
        # print(tenStop)
        #orderId = order(theContract_C, 1, StopOrder(stop_price=tenStop))
        orderId = order(theContract_C, 1, TrailStopOrder(trailing_percent=10))

        order_status_monitor(orderId, target_status=['Filled', 'Submitted', 'PreSubmitted'])
    return orderId


def short_entry(context, data, price):
    if price != -1:
        closest_expiry_date = nextExpiryDate()
        ans_P = get_contract_details(secType='OPT',
                                     symbol='SPY',
                                     field='summary',
                                     currency='USD',
                                     exchange='SMART',
                                     primaryExchange='SMART',
                                     expiry=closest_expiry_date,
                                     right='C')

        df_closestToMoney_P = closestToMoney(ans_P, price, 'P')
        theContract_P = df_closestToMoney_P.iat[0, 0]
        theContract_P.primaryExchange = 'SMART'

        orderId = order(theContract_P, 1, TrailStopOrder(trailing_percent=10))

        order_status_monitor(orderId, target_status=['Filled', 'Submitted', 'PreSubmitted'])
    return orderId


# def initialize(context):
#     # pass
#     context.security = symbol('SPY')
#     context.flag = False
#
#
# def handle_data(context, data):
#     # print(get_datetime().strftime("%Y-%m-%d %H:%M:%S %Z"))
#     price = data.current(context.security, 'price')
#     print(price)
#     if price != -1:
#         closest_expiry_date = nextExpiryDate()
#         ans_C = get_contract_details(secType='OPT',
#                                      symbol='SPY',
#                                      field='summary',
#                                      currency='USD',
#                                      exchange='SMART',
#                                      primaryExchange='SMART',
#                                      expiry=closest_expiry_date,
#                                      right='C')
#
#         ans_P = get_contract_details(secType='OPT',
#                                      symbol='SPY',
#                                      field='summary',
#                                      currency='USD',
#                                      exchange='SMART',
#                                      # primaryExchange='ARCA',
#                                      expiry=closest_expiry_date,
#                                      right='P')
#
#         # print(len(ans_P))
#         # print(len(ans_C))
#         # print(ans_C.at[1, 'security'])
#
#         df_closestToMoney_P = closestToMoney(ans_P, last_price, 'P')
#         df_closestToMoney_C = closestToMoney(ans_C, last_price, 'C')
#
#         theContract_C = df_closestToMoney_C.iat[0, 0]
#         theContract_P = df_closestToMoney_P.iat[0, 0]
#         theContract_C.primaryExchange = 'SMART'
#         print('strike', theContract_C.strike)
#
#         if not context.flag:
#             # http://www.ibridgepy.com/ibridgepy-documentation/#order8212_similar_as_order_at_Quantopian
#             tenStop = round(last_price * .90, 2)
#             print(tenStop)
#             orderId = order(theContract_C, 1, StopOrder(stop_price=tenStop))  # buy 100 shares of SPY
#
#             # http://www.ibridgepy.com/ibridgepy-documentation/#order_status_monitor
#             order_status_monitor(orderId, target_status=['Filled', 'Submitted', 'PreSubmitted'])
#             context.flag = True
#         else:
#             display_all()
#             # end()
