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

class TestStrategy(bt.Strategy):
    params = (('p1', 8), 
    ('p2', 20),
    ('p3', 144),
    ('rsi', 40),
    ('rr', 4),
    ('rrp', 1),
    ('candleper', 0.005),
    ('delay', -1),
    ('pricelimitper', 0.001),
    ('bodyper', 0.7),
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
        self.ema1 = bt.indicators.EMA(period=self.p.p1)
        self.ema2 = bt.indicators.EMA(period=self.p.p2)
        self.sma3 = bt.indicators.SMA(period=self.p.p3)
 
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
        #self.log('Close, %.2f' % self.dataclose[0])
        # Check if time is greater 9 30 or not
        
        if (self.data.datetime.time() < datetime.time(9,30) ) or (self.data.datetime.time() > datetime.time(15,10)) :
                return 

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        

            # Check if we are in the market
        if self.position.size == 0:
            
            # Not yet ... we MIGHT BUY if ... self.datas[0].close
            c0 = (self.dataclose[self.p.delay -2] > self.dataopen[self.p.delay-2]) #prev prev cadle green 
            c1 = (self.dataclose[self.p.delay] > self.dataopen[self.p.delay]) # current candle green  
            c2 = (self.dataclose[self.p.delay -1] > self.dataopen[self.p.delay-1]) #prev cadle red 
            
            c3 = self.ema2[self.p.delay] > self.sma3[self.p.delay]  ##20EMA > 144SMA
           
            c4 = abs(self.dataclose[self.p.delay] - self.ema2[self.p.delay] ) / self.ema2[self.p.delay] < 0.5/100 # (close - 20em )<0.5%
            c5 = ((self.datahigh[self.p.delay]-self.datalow[self.p.delay]) < self.p.candleper * self.dataclose[self.p.delay]) #  hi-low < 0.5% of close
            
            c6 = self.dataclose[self.p.delay] > self.datahigh[self.p.delay -1]  #crurrent close > prev high 
            c7 =  ( self.datahigh[self.p.delay-1] - self.datalow[self.p.delay-1] ) <  ( self.datahigh[self.p.delay-2] - self.datalow[self.p.delay-2] ) # prev candle len shorter than prev prev candle len 
            c8 = self.ema2[self.p.delay]  > self.ema2[self.p.delay -1]  and  self.ema2[self.p.delay-1]  > self.ema2[self.p.delay -2]  #
            if (c0 & c1 & c2 & c3 & c4 & c5 & c6 & c7 & c8 ):
                ##diff = self.dataclose[0] - self.dataclose[lastred]
                rr = self.p.rr
                

                cash = self.stats.broker.cash[self.p.delay]
                maxRisk = cash * 0.01

                self.sl = 0.999* self.datalow[self.p.delay - 1]  # SL: prev candle low - 0.1%
                diff = self.datalow[self.p.delay ] - self.sl
                self.reward = rr*diff+self.dataclose[self.p.delay]
                self.bsize = int(min(maxRisk/diff , cash/self.dataclose[self.p.delay]))
                # BUY, BUY, BUY!!! (with all possible default parameters)
                bprice = self.data.close[self.p.delay] * (1+self.p.pricelimitper)
                self.log(" Buy Signal at candle_pos = "+str(len(self))+ " Buy limit at "+ str(bprice))

                

                # Keep track of the created order to avoid a 2nd order
                #self.order = self.buy(size=self.bsize)
                
                self.order = self.buy(exectype=bt.Order.Stop,
                size=self.bsize,price=bprice,
                valid=datetime.datetime.now() + datetime.timedelta(minutes=30)
                )

                self.log('BUY CREATE, %.2f' % self.dataclose[self.p.delay])

        else:
            # Already in a position? check exit criteria

            # Long Eixt criteria
            e1 = (self.dataclose[0] < self.sl) # SL reached
            e2 = (self.dataclose[0] > self.reward) # Reward reached
            e3 = (self.dataopen[0] > self.reward)  # Reward reached 

            if (e1 | e2 | e3):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE... closed position, %.2f ' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell(size=self.bsize)
        #printf(f) Close all positions EOD
        if self.position.size != 0:
            if self.data.datetime.time() > datetime.time(15,10):
                    self.close(exectype=bt.Order.Market,size=self.position.size)
