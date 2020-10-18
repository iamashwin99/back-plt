from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import streamlit as st
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
#from getData import *
import backtrader as bt
from strategy import TestStrategy
from btplotting import BacktraderPlotting
from btplotting.schemes import Tradimo
import yfinance as yf
st.beta_set_page_config(page_title='Stock-plt', page_icon=None, layout='centered', initial_sidebar_state='auto')

st.write("""
# Simple backtrader backtesting App
After choosing each parameter press enter
""")

# tickerSymbol =  'RELIANCE.NS'
# start_date = '2020-09-30'
# end_date =  '2020-10-18'
# interval_length = '5m'
# start_cash =  '100000.0'

tickerSymbol = st.text_input("Enter Symbol (like INFY.NS) ", 'RELIANCE.NS') 
start_date = st.text_input("Enter Start Date", '2020-09-30') 
end_date = st.text_input("Enter End Date", '2020-10-18') 
interval_length = st.text_input("Enter Interval length (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo)", '5m') 
start_cash = st.text_input("Enter starting Cash", '100000.0') 


def runStrategy(tickerSymbol,start_date,end_date,interval_length,start_cash):
    fname = 'out/'
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(float(start_cash))
    #cerebro.addobserver(bt.observers.Cash)
    cerebro.addobserver(bt.observers.Value)
    #cerebro.addobserver(bt.observers.Trade)
    #cerebro.addobserver(bt.observers.BuySell)
    cerebro.broker.setcommission(commission=0.0001)
    tickerData = yf.Ticker(tickerSymbol)
    #get the historical prices for this ticker
    tickerDf = tickerData.history(interval=interval_length, start=start_date, end=end_date)
    # Open	High	Low	Close	Volume	Dividends	Stock Splits

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.addstrategy(TestStrategy)
    cerebro.adddata(bt.feeds.PandasData(dataname=tickerDf))
    cerebro.addanalyzer(bt.analyzers.SharpeRatio)
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    #cerebro.plot(style='candlestick', barup='green', bardown='red')
    fname += datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")

    p = BacktraderPlotting(style='bar',filename=fname+'.html', output_mode='show', scheme=Tradimo())
    cerebro.plot(p)

runStrategy(tickerSymbol,start_date,end_date,interval_length,start_cash)