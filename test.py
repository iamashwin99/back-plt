from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
from getData import *
import backtrader as bt
from strategy import TestStrategy
from btplotting import BacktraderPlotting
from btplotting.schemes import Tradimo


fname = 'out'
stock = 'RELIANCE.NS'
noDays = 30
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)
    #cerebro.addobserver(bt.observers.Cash)
    cerebro.addobserver(bt.observers.Value)
    #cerebro.addobserver(bt.observers.Trade)
    #cerebro.addobserver(bt.observers.BuySell)
    cerebro.broker.setcommission(commission=0.0001)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.addstrategy(TestStrategy)
    get5minData(stock,noDays,fname)
    datapath = (fname+'.csv')
    data = bt.feeds.GenericCSVData(
        dataname='out.csv',
        #dtformat=('%Y-%m-%d %H.%M.%S'),
        timeframe=bt.TimeFrame.Minutes,
        compression=5, 
        datetime=0,
        time=-1,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1
    )
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio)
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    #cerebro.plot(style='candlestick', barup='green', bardown='red')
    fname = 'out/'+datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")

    p = BacktraderPlotting(style='bar',filename=fname+'.html', output_mode='show', scheme=Tradimo())
    cerebro.plot(p)

    # figure = cerebro.plot(style='candlestick', barup='green', bardown='red')[0][0]
    # figure.savefig('out/'+datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")+'.png')
