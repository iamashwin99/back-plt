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
    ('p2', 21),
    ('p3', 55),
    ('p4', 144),
    ('rsi', 40),
    ('rr', 2),
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
        self.sma1 = bt.indicators.EMA(period=self.p.p1)
        self.sma2 = bt.indicators.EMA(period=self.p.p2)
        self.sma3 = bt.indicators.EMA(period=self.p.p3)
        self.sma4 = bt.indicators.EMA(period=self.p.p4)
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
            c1 = (self.dataclose[self.p.delay] > self.dataopen[self.p.delay]) # Green Candle 
            c2 = (self.rsi[self.p.delay] >= self.p.rsi)  # RSI>55 
            c3 = (self.dataclose[self.p.delay] > self.sma1[self.p.delay]) & (self.dataclose[self.p.delay] > self.sma2[self.p.delay]) # Close above EMA1  and 2
            c4 = (self.datalow[self.p.delay] < self.sma1[self.p.delay]) & (self.datalow[self.p.delay] < self.sma2[self.p.delay])  #low below 9 and 21 ema
            c5 = ((self.datahigh[self.p.delay]-self.datalow[self.p.delay]) < self.p.candleper * self.dataclose[self.p.delay]) #  hi-low < 0.5% of close
            c6 = self.dataclose[self.p.delay] > self.sma3[self.p.delay]
            c7 = self.dataclose[self.p.delay] > self.sma4[self.p.delay]
            #c8 = self.dataclose[0] > self.vwap[0]
            c9 = (self.dataclose[self.p.delay]-self.dataopen[self.p.delay]) > self.p.bodyper * (self.datahigh[self.p.delay] - self.datalow[self.p.delay])
            testcandle = 3110
            if(len(self) == testcandle):
                self.log("Entering candle no " + str(testcandle))
                                                                                                                         
            if (c1 & c2 & c3 & c4 & c5 & c9):
                ##diff = self.dataclose[0] - self.dataclose[lastred]
                rr = self.p.rr
                if(c6):
                    rr += self.p.rrp
                if( c7 ):
                    rr += self.p.rrp
                # if( c8 ):
                #     rr+=1
                #rr =2 
                cash = self.stats.broker.cash[self.p.delay]
                maxRisk = cash * 0.01
                diff = abs(2*(self.datahigh[self.p.delay]-self.datalow[self.p.delay]))
                self.sl = self.dataclose[self.p.delay] - diff
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
