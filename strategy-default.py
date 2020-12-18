from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
import backtrader.feeds as btfeeds

import pandas as pd
import streamlit as st

# Create a Stratey

# Actual logic is implimneted at def next:

class TestStrategy(bt.Strategy):
    params = (('p1', 8), 
    ('p2', 21),
    ('p3', 55),
    ('rsi', 40),
    )
    

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        #print('%s, %s' % (dt.isoformat(), txt))
        print('%s,%s, %s' % (dt.strftime("%d/%m/%Y"),self.datas[0].datetime.time().strftime("%H:%M:%S") ,txt))
        st.sidebar.write('%s,%s, %s' % (dt.strftime("%d/%m/%Y"),self.datas[0].datetime.time().strftime("%H:%M:%S") ,txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datalow = self.datas[0].low
        self.datahigh = self.datas[0].high
        

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.sl = 1
        self.reward = 0
        

        # Add a MovingAverageSimple indicator
        self.sma1 = bt.indicators.EMA(period=self.p.p1)
        self.sma2 = bt.indicators.EMA(period=self.p.p2)
        self.sma3 = bt.indicators.EMA(period=self.p.p3)
        
        self.rsi = bt.indicators.RSI(self.datas[0],plothlines=[55, 45])
        #self.vwap = bt.indicators.VWAP(self.datas[0])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, candle_pos = %.2f,' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm,
                     len(self)))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f  candle_pos =%.2f,' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm,
                          len(self)))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f \n \n' %
                 (trade.pnl, trade.pnlcomm))
        

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            c1 = self.dataclose[0] < self.dataclose[-1] # current close less than previous close
            c2 = self.dataclose[-1] < self.dataclose[-2] # previous close less than the previous close


            
            if c1 and c2:
                # BUY, BUY, BUY!!! (with default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
