from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import streamlit as st
import base64
import datetime  # For datetime objects
import os  # To manage paths
import io
import backtrader as bt
#from strategy import TestStrategy
from btplotting import BacktraderPlotting
from btplotting.schemes import Tradimo
import yfinance as yf
import backtrader.feeds as btfeeds
import pandas as pd
from streamlit_ace import st_ace
import random, string
import importlib
st.beta_set_page_config(page_title='Back-plt', page_icon=None, layout='centered', initial_sidebar_state='auto')

def runStrategy(tickerSymbol,tickerDf,start_cash):
    fname = 'out/' 
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(float(start_cash))
    cerebro.addobserver(bt.observers.Value)
    cerebro.broker.setcommission(commission=0.0001)
    st.sidebar.write(''' ### Strategy output''')
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.addstrategy(TestStrategy)
    cerebro.adddata(bt.feeds.PandasData(dataname=tickerDf))
    cerebro.addanalyzer(bt.analyzers.SharpeRatio)
    cerebro.run()
    
    st.write('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    st.write('Strategy performance: %.3f percent' % ((cerebro.broker.getvalue()- float(start_cash))*100/float(start_cash)) )
    st.write('Stock performance: %.3f percent' % ((((tickerDf['Open'][-1]) - (tickerDf['Open'][0]))/(tickerDf['Open'][0])).astype('float')*100))
    
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    #cerebro.plot(style='candlestick', barup='green', bardown='red')
    file_name = tickerSymbol + '-'+datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
    fname += file_name

    p = BacktraderPlotting(style='bar',filename=fname+'.html', output_mode='save', scheme=Tradimo())
    cerebro.plot(p)
    print("saved at "+fname+'.html')
    return [fname+'.html', file_name]




THEMES = [
    "chaos","ambiance",  "chrome", "clouds", "clouds_midnight", "cobalt", "crimson_editor", "dawn",
    "dracula", "dreamweaver", "eclipse", "github", "gob", "gruvbox", "idle_fingers", "iplastic",
    "katzenmilch", "kr_theme", "kuroir", "merbivore", "merbivore_soft", "mono_industrial", "monokai",
    "nord_dark", "pastel_on_dark", "solarized_dark", "solarized_light", "sqlserver", "terminal",
    "textmate", "tomorrow", "tomorrow_night", "tomorrow_night_blue", "tomorrow_night_bright",
    "tomorrow_night_eighties", "twilight", "vibrant_ink", "xcode"
]

KEYBINDINGS = [
    "vscode", "emacs", "sublime", "vim"
]

st.write("""
# Simple backtrader backtesting App
* After choosing each parameter press enter.
* Interval length need to be grater than 1h if the date range is greater than  LAST 60 days
* After the chart loads the side bar will load with the backtested data, click on it to download
""" )

# tickerSymbol =  'RELIANCE.NS'
# start_date = '2020-09-30'
# end_date =  '2020-10-18'
# interval_length = '5m'
# start_cash =  '100000.0'


tickerSymbol = st.text_input("Enter Symbol (like INFY.NS) ", 'RELIANCE.NS') 
# start_date = st.text_input("Enter Start Date", '2020-09-20') 
# end_date = st.text_input("Enter End Date", '2020-10-18') 
deltaDays = st.text_input("Enter delta days", '30') 
s_date = st.date_input('Enter Start Date (takes precedence over delta days)', datetime.datetime.now()-datetime.timedelta(days = int(deltaDays)) )
e_date = st.date_input('Enter End Date', datetime.datetime.now())

start_date = s_date.strftime("%Y-%m-%d")
end_date = e_date.strftime("%Y-%m-%d")


interval_length = st.text_input("Enter Interval length (1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo)", '5m') 
start_cash = st.text_input("Enter starting Cash", '100000.0') 
tickerData = yf.Ticker(tickerSymbol)
#get the historical prices for this ticker
tickerDf = tickerData.history(interval=interval_length, start=start_date, end=end_date)
# Open	High	Low	Close	Volume	Dividends	Stock Splits
#Charting the price and volume
st.write("""
## Closing Price
""")
st.line_chart(tickerDf.Close)
st.write("""
## Volume Price
""")
st.line_chart(tickerDf.Volume)

#load default strategy

# Add ace and sliders
with io.open('strategy.py', 'r', encoding='utf8') as f:
    text = f.read()
st.sidebar.title(":memo: Editor settings")
content = st_ace(
    value=text,
    language="python",
    theme=st.sidebar.selectbox("Theme", options=THEMES),
    keybinding=st.sidebar.selectbox("Keybinding mode", options=KEYBINDINGS),
    font_size=st.sidebar.slider("Font size", 5, 24, 12),
    tab_size=4,
    show_gutter=st.sidebar.checkbox("Show gutter", value=True),
    show_print_margin=st.sidebar.checkbox("Show print margin", value=True),
    wrap=st.sidebar.checkbox("Wrap enabled", value=True),
    readonly=st.sidebar.checkbox("Read-only", value=False, key="ace-editor"),
    auto_update=False,
    key="ace-editor" 
    
)
#save content into temporary py and load its strategy
strategy_name = 'temp-'+''.join(random.choices(string.ascii_letters + string.digits, k=8)) 
with open(strategy_name+'.py', 'w') as the_file:
    the_file.write(content)

TestStrategy = getattr(importlib.import_module(strategy_name), 'TestStrategy')

### Run strategy
file_path,filename = runStrategy(tickerSymbol,tickerDf,start_cash)

###Downlaod strategy
with open(file_path) as f:
    bytes = f.read()
    b64 = base64.b64encode(bytes.encode("utf-8")).decode()
    href = f'<a href="data:file/html;base64,{b64}" download=\'{filename}.html\'>\
       Click to download \
    </a>'
st.write(''' ## Backtesting done ''')
st.markdown(href, unsafe_allow_html=True)   


## Remove temporary files
if os.path.exists(strategy_name+'.py'):
  os.remove(strategy_name+'.py')
  print("File Removed : "+strategy_name+'.py')
else:
  print("The file does not exist")





