"""
new and improved trader functions

@author: Grady Mellin

"""

from IBridgePy.Trader import *
import bisect
from IBridgePy.quantopian import TrailStopOrder, StopOrder
import numpy as np


class Trader(Trader):

    def new_modify_order(self, ibpyOrderId, newQuantity=None, newOrderType=None, newTrailingPercent=None,
                         newTrailingStopPrice=None, newLimitPrice=None, newStopPrice=None, newTif=None,
                         newOrderRef=None, newOcaGroup=None, newOcaType=None):
        self._log.debug(__name__ + '::modify_order: ibpyOrderId = %s' % (ibpyOrderId,))
        currentOrder = self._brokerService.get_order(ibpyOrderId)
        if currentOrder.status in [OrderStatus.PRESUBMITTED, OrderStatus.SUBMITTED]:
            if newQuantity is not None:
                currentOrder.order.totalQuantity = newQuantity
            if newOrderType is not None:
                currentOrder.order.orderType = newOrderType
            if newTrailingPercent is not None:
                currentOrder.order.trailingPercent = newTrailingPercent
            if newTrailingStopPrice is not None:
                currentOrder.order.trailingStopPrice = newTrailingStopPrice
            if newLimitPrice is not None:
                currentOrder.order.lmtPrice = newLimitPrice
            if newStopPrice is not None:
                currentOrder.order.auxPrice = newStopPrice
            if newTif is not None:
                currentOrder.order.tif = newTif
            if newOrderRef is not None:
                currentOrder.order.orderRef = newOrderRef
            if newOcaGroup is not None:
                currentOrder.order.ocaGroup = newOcaGroup
            if newOcaType is not None:
                currentOrder.order.ocaType = newOcaType
            self._brokerService.submit_requests(ModifyOrder(ibpyOrderId, currentOrder.contract, currentOrder.order,
                                                            FollowUpRequest.DO_NOT_FOLLOW_UP))
        else:
            self._log.error(__name__ + '::modify_order: Cannot modify ibpyOrderId=%s orderStatus=%s' % (
                ibpyOrderId, currentOrder.status))
            exit()

    def new_modify_orders(self, ibpyOrderId, ibpyOrderId2, newQuantity=None, newOrderType=None, newTrailingPercent=None,
                          newTrailingStopPrice=None, newLimitPrice=None, newStopPrice=None, newTif=None,
                          newOrderRef=None, newOcaGroup=None, newOcaType=None):

        self._log.debug(__name__ + '::modify_order: ibpyOrderId = %s' % (ibpyOrderId,))
        currentOrder = self._brokerService.get_order(ibpyOrderId)
        if currentOrder.status in [OrderStatus.PRESUBMITTED, OrderStatus.SUBMITTED]:
            if newQuantity is not None:
                currentOrder.order.totalQuantity = newQuantity
            if newOrderType is not None:
                currentOrder.order.orderType = newOrderType
            if newTrailingPercent is not None:
                currentOrder.order.trailingPercent = newTrailingPercent
            if newTrailingStopPrice is not None:
                currentOrder.order.trailingStopPrice = newTrailingStopPrice
            if newLimitPrice is not None:
                currentOrder.order.lmtPrice = newLimitPrice
            if newStopPrice is not None:
                currentOrder.order.auxPrice = newStopPrice
            if newTif is not None:
                currentOrder.order.tif = newTif
            if newOrderRef is not None:
                currentOrder.order.orderRef = newOrderRef
            if newOcaGroup is not None:
                currentOrder.order.ocaGroup = newOcaGroup
            if newOcaType is not None:
                currentOrder.order.ocaType = newOcaType
        self._log.debug(__name__ + '::modify_order: ibpyOrderId = %s' % (ibpyOrderId2,))
        currentOrder2 = self._brokerService.get_order(ibpyOrderId2)
        if currentOrder2.status in [OrderStatus.PRESUBMITTED, OrderStatus.SUBMITTED]:
            if newQuantity is not None:
                currentOrder2.order.totalQuantity = newQuantity
            if newOrderType is not None:
                currentOrder2.order.orderType = newOrderType
            if newTrailingPercent is not None:
                currentOrder2.order.trailingPercent = newTrailingPercent
            if newTrailingStopPrice is not None:
                currentOrder2.order.trailingStopPrice = newTrailingStopPrice
            if newLimitPrice is not None:
                currentOrder2.order.lmtPrice = newLimitPrice
            if newStopPrice is not None:
                currentOrder2.order.auxPrice = newStopPrice
            if newTif is not None:
                currentOrder2.order.tif = newTif
            if newOrderRef is not None:
                currentOrder2.order.orderRef = newOrderRef
            if newOcaGroup is not None:
                currentOrder2.order.ocaGroup = newOcaGroup
            if newOcaType is not None:
                currentOrder2.order.ocaType = newOcaType
            self._brokerService.submit_requests(ModifyOrder(ibpyOrderId, currentOrder.contract, currentOrder.order,
                                                            FollowUpRequest.DO_NOT_FOLLOW_UP),
                                                ModifyOrder(ibpyOrderId2, currentOrder2.contract, currentOrder2.order,
                                                            FollowUpRequest.DO_NOT_FOLLOW_UP))
        else:
            self._log.error(__name__ + '::modify_order: Cannot modify ibpyOrderId=%s orderStatus=%s' % (
                ibpyOrderId, currentOrder.status))
            exit()

    def place_order_with_trailing_stoploss(self, security, value, trail, style, contract_price, tif='DAY',
                                           accountCode='default'):
        # https://developer.tdameritrade.com/content/place-order-samples Not implemented for TD yet
        targetShare = int(value / contract_price)
        stopPrice = round(contract_price * .80, 2)
        # if op_type == "P":
        #     limitPrice -=.01
        # elif op_type == "C":
        #     limitPrice +=.01
        # limitPrice += .01
        # parentOrder_tup = self._helper(security, targetShare,
        #                                style, accountCode)
        # adj_accountCode, parentOrder, int_tsOrderId, ocaGroup, int_parentOrderId = parentOrder_tup
        adj_accountCode = self.adjust_accountCode(accountCode)
        ocaGroup = str(dt.datetime.now())

        int_parentOrderId = self._brokerService.use_next_id()
        parentOrder = create_order(int_parentOrderId, adj_accountCode, security, targetShare, style,
                                   self.get_datetime())

        int_slOrderId = self._brokerService.use_next_id()
        slOrder = create_order(int_slOrderId, adj_accountCode, security, -targetShare,
                               StopOrder(stop_price=stopPrice, tif='DAY'),
                               self.get_datetime(), ocaGroup=ocaGroup)

        int_tsOrderId = self._brokerService.use_next_id()
        tsOrder = create_order(int_tsOrderId, adj_accountCode, security, -targetShare,
                               TrailStopOrder(trailing_percent=trail, tif=tif),
                               self.get_datetime(), ocaGroup=ocaGroup)
        # IB recommends this way to place takeProfitOrder and stopLossOrder
        # with main order.
        parentOrder.requestedOrder.transmit = False
        slOrder.requestedOrder.parentId = int_parentOrderId
        slOrder.requestedOrder.transmit = False
        tsOrder.requestedOrder.parentId = int_parentOrderId
        tsOrder.requestedOrder.transmit = True  # only transmit tsOrder to avoid inadvertent actions

        # Does not follow up on place_order(parentOrder) because it is a partial order
        # As IB recommended, parentOrder and takeProfitOrder are not transmitted, so that IBridgePy should not follow up
        str_parentOrderId = self._brokerService.place_order(parentOrder, followUp=False)
        str_slOrderId = self._brokerService.place_order(slOrder, followUp=False)
        str_tsOrderId = self._brokerService.place_order(tsOrder)
        return str_parentOrderId, str_tsOrderId, str_slOrderId

    def add_to_position_with_trailing_stoploss(self, security, str_tsOrderId, str_slOrderId, amount, trail, style,
                                               contract_price,
                                               tif='DAY', accountCode='default'):
        stopPrice = round(contract_price * .95, 2)
        amount = int(amount)
        amount2 = amount * 2
        self.cancel_order(str_tsOrderId)
        self.cancel_order(str_slOrderId)
        adj_accountCode = self.adjust_accountCode(accountCode)
        ocaGroup = str(dt.datetime.now())
        int_add_toOrderId = self._brokerService.use_next_id()
        add_toOrder = create_order(int_add_toOrderId, adj_accountCode, security, amount, style, self.get_datetime(),
                                   ocaGroup=ocaGroup)
        int_add_to_tsOrderId = self._brokerService.use_next_id()
        add_to_tsOrder = create_order(int_add_to_tsOrderId, adj_accountCode, security, -amount,
                                      TrailStopOrder(trailing_percent=trail, tif=tif), self.get_datetime(),
                                      ocaGroup=ocaGroup)
        int_add_to_slOrderId = self._brokerService.use_next_id()
        add_to_slOrder = create_order(int_add_to_slOrderId, adj_accountCode, security, -amount,
                                      StopOrder(stop_price=stopPrice, tif='DAY'),
                                      self.get_datetime(), ocaGroup=ocaGroup)
        int_add_to_tsOrderId2 = self._brokerService.use_next_id()
        add_to_tsOrder2 = create_order(int_add_to_tsOrderId2, adj_accountCode, security, -amount,
                                       TrailStopOrder(trailing_percent=trail, tif=tif), self.get_datetime(),
                                       ocaGroup=ocaGroup)
        int_add_to_slOrderId2 = self._brokerService.use_next_id()
        add_to_slOrder2 = create_order(int_add_to_slOrderId2, adj_accountCode, security, -amount,
                                       StopOrder(stop_price=stopPrice, tif='DAY'),
                                       self.get_datetime(), ocaGroup=ocaGroup)

        add_toOrder.requestedOrder.transmit = False
        add_to_tsOrder.requestedOrder.parentId = int_add_toOrderId
        add_to_tsOrder.requestedOrder.transmit = False
        add_to_slOrder.requestedOrder.parentId = int_add_toOrderId
        add_to_slOrder.requestedOrder.transmit = False
        add_to_tsOrder2.requestedOrder.parentId = int_add_toOrderId
        add_to_tsOrder2.requestedOrder.transmit = False
        add_to_slOrder2.requestedOrder.parentId = int_add_toOrderId
        add_to_slOrder2.requestedOrder.transmit = True
        retry = 3
        count = 1
        ans = None
        while count <= retry:
            count += 1
            try:
                str_add_toOrderId = self._brokerService.place_order(add_toOrder, followUp=False)
                str_add_to_tsOrder = self._brokerService.place_order(add_to_tsOrder, followUp=False)
                str_add_to_slOrderId = self._brokerService.place_order(add_to_slOrder, followUp=False)
                str_add_to_tsOrder2 = self._brokerService.place_order(add_to_tsOrder2, followUp=False)
                str_add_to_slOrderId2 = self._brokerService.place_order(add_to_slOrder2)
                break
            except RuntimeError:
                time.sleep(1)
        return security, str_add_toOrderId, str_add_to_tsOrder, str_add_to_slOrderId, str_add_to_tsOrder2, str_add_to_slOrderId2

    # def add_to_position_with_trailing_stoploss(self, security, str_tsOrderId, amount, trail, style,
    #                                            contract_price,
    #                                            tif='DAY', accountCode='default'):
    #     amount = int(amount)
    #     self.cancel_order(str_tsOrderId)
    #     adj_accountCode = self.adjust_accountCode(accountCode)
    #     ocaGroup = str(dt.datetime.now())
    #     int_add_toOrderId = self._brokerService.use_next_id()
    #     add_toOrder = create_order(int_add_toOrderId, adj_accountCode, security, amount, style, self.get_datetime(),
    #                                ocaGroup=ocaGroup)
    #     int_add_to_tsOrderId = self._brokerService.use_next_id()
    #     add_to_tsOrder = create_order(int_add_to_tsOrderId, adj_accountCode, security, -2*amount,
    #                                   TrailStopOrder(trailing_percent=trail, tif=tif), self.get_datetime(),
    #                                   ocaGroup=ocaGroup)
    #
    #     add_toOrder.requestedOrder.transmit = True
    #
    #     str_add_toOrderId = self._brokerService.place_order(add_toOrder, followUp=True)
    #     order_status_doubled = self.get_order_status(str_add_toOrderId)
    #     while order_status_doubled not in [OrderStatus.FILLED]:
    #         # print("filling")
    #         # print(order_status_doubled)
    #         order_status_doubled = self.get_order_status(str_add_toOrderId)
    #         print(order_status_doubled)
    #         if order_status_doubled in [OrderStatus.FILLED]:
    #             break
    #     add_to_tsOrder.requestedOrder.transmit = True
    #     str_add_to_tsOrder = self._brokerService.place_order(add_to_tsOrder)
    #
    #     return security, str_add_toOrderId, str_add_to_tsOrder

    def nextExpiryDate(self):
        def next_weekday(d, weekday):
            days_ahead = weekday - d.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            return d + dt.timedelta(days_ahead)

        sTime = self.get_datetime('US/Eastern')
        d = dt.date.today()

        next_monday = next_weekday(d, 0)  # 0 = Monday, 1=Tuesday, 2=Wednesday...
        next_wednesday = next_weekday(d, 2)
        next_friday = next_weekday(d, 4)
        if (d.weekday() == 0 or d.weekday() == 2 or d.weekday() == 4) and sTime.hour < 12:
            next_expiry_date = d
        elif next_monday < next_wednesday and next_monday < next_friday:
            next_expiry_date = next_monday
        elif next_wednesday < next_friday and next_wednesday < next_monday:
            next_expiry_date = next_wednesday
        else:
            next_expiry_date = next_friday
        return next_expiry_date.strftime("%Y%m%d")

    def closestToMoney(self, dff, targetStrike, op_type):
        assert (isinstance(targetStrike, float))
        # A value is trying to be set on a copy of a slice from a DataFrame.
        # Try using .loc[row_indexer,col_indexer] = value instead
        df = dff.copy()  # To avoid the above error, make a copy of incoming dff
        if op_type == 'C':
            df['strike'] = df['security'].apply(lambda x: x.strike - targetStrike)
        elif op_type == 'P':
            df['strike'] = df['security'].apply(lambda x: targetStrike - x.strike)
        else:
            df['strike'] = df['security'].apply(lambda x: abs(x.strike - targetStrike))
        sorted_exp = sorted(list(set(df['strike'])))
        lc = bisect.bisect_left(sorted_exp, 0)
        return df.loc[df['strike'] == sorted_exp[lc], :]

    def long_entry(self, price, value):
        if price != -1:
            closest_expiry_date = self.nextExpiryDate()
            ans_C = self.get_contract_details(secType='OPT',
                                              symbol='SPY',
                                              field='summary',
                                              currency='USD',
                                              exchange='SMART',
                                              primaryExchange='SMART',
                                              expiry=closest_expiry_date,
                                              right='C')

            df_closestToMoney_C = self.closestToMoney(ans_C, price, 'C')
            theContract_C = df_closestToMoney_C.iat[0, 0]
            theContract_C.primaryExchange = 'SMART'
            contract_ask_price = self.show_real_time_price(theContract_C, 'ask_price')
            contract_mid_price = round(((self.show_real_time_price(theContract_C, 'ask_price') +
                                         self.show_real_time_price(theContract_C, 'bid_price')) / 2), 2)

            orderId = self.place_order_with_trailing_stoploss(theContract_C, value, 10, LimitOrder(contract_ask_price),
                                                              contract_ask_price, tif='DAY', accountCode='default')

        return theContract_C, orderId[0], orderId[1], orderId[2]

    def short_entry(self, price, value):
        if price != -1:
            closest_expiry_date = self.nextExpiryDate()
            ans_P = self.get_contract_details(secType='OPT',
                                              symbol='SPY',
                                              field='summary',
                                              currency='USD',
                                              exchange='SMART',
                                              primaryExchange='SMART',
                                              expiry=closest_expiry_date,
                                              right='P')

            df_closestToMoney_P = self.closestToMoney(ans_P, price, 'P')
            theContract_P = df_closestToMoney_P.iat[0, 0]
            theContract_P.primaryExchange = 'SMART'
            contract_ask_price = self.show_real_time_price(theContract_P, 'ask_price')
            contract_mid_price = round(((self.show_real_time_price(theContract_P, 'ask_price') +
                                         self.show_real_time_price(theContract_P, 'bid_price')) / 2), 1)

            orderId = self.place_order_with_trailing_stoploss(theContract_P, value, 10, LimitOrder(contract_ask_price),
                                                              contract_ask_price, tif='DAY', accountCode='default')

        return theContract_P, orderId[0], orderId[1], orderId[2]

    def long_entry_new(self, price, value):
        if price != -1:
            closest_expiry_date = self.nextExpiryDate()
            ans_C = self.get_contract_details(secType='OPT',
                                              symbol='SPY',
                                              field='summary',
                                              currency='USD',
                                              exchange='SMART',
                                              primaryExchange='SMART',
                                              expiry=closest_expiry_date,
                                              right='C')

            df_closestToMoney_C = self.closestToMoney(ans_C, price, 'C')
            theContract_C = df_closestToMoney_C.iat[0, 0]
            theContract_C.primaryExchange = 'SMART'
            contract_ask_price = self.show_real_time_price(theContract_C, 'ask_price')
            shares = int(value / contract_ask_price)
            orderId = self.order(theContract_C, shares, LimitOrder(contract_ask_price), accountCode='default')

        return theContract_C, orderId, shares

    def short_entry_new(self, price, value):
        if price != -1:
            closest_expiry_date = self.nextExpiryDate()
            ans_P = self.get_contract_details(secType='OPT',
                                              symbol='SPY',
                                              field='summary',
                                              currency='USD',
                                              exchange='SMART',
                                              primaryExchange='SMART',
                                              expiry=closest_expiry_date,
                                              right='P')

            df_closestToMoney_P = self.closestToMoney(ans_P, price, 'P')
            theContract_P = df_closestToMoney_P.iat[0, 0]
            theContract_P.primaryExchange = 'SMART'
            contract_ask_price = self.show_real_time_price(theContract_P, 'ask_price')
            shares = int(value/contract_ask_price)
            orderId = self.order(theContract_P, shares, LimitOrder(contract_ask_price), accountCode='default')

        return theContract_P, orderId, shares

    def retry_request_hist(self, security, barSize, goBack):
        retry = 3
        count = 1
        ans = None
        while count <= retry:
            count += 1
            try:
                ans = self.request_historical_data(security, barSize, goBack, useRTH=0)
                break
            except RuntimeError:
                time.sleep(3)
        return ans
