# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pprint
import sys
from yahoo_finance_api2 import share
from yahoo_finance_api2.exceptions import YahooFinanceError

import datetime
import json
import requests
import pandas as pd
def spfloat(a,i):
    if a[i] is None:
        return spfloat(a,i-1)
    else:
        return float(a[i])

# %%

def get5minData(symbol,period,outname):
    my_share = share.Share(symbol)
    symbol_data = None

    try:
        symbol_data = my_share.get_historical(share.PERIOD_TYPE_DAY,
                                            period,
                                            share.FREQUENCY_TYPE_MINUTE,
                                            5)
    except YahooFinanceError as e:
        print(e.message)
        sys.exit(1)


    # %%
    datalist=[]
    dates = list(symbol_data["timestamp"])
    opens = list(symbol_data["open"])
    highs = list(symbol_data["high"])
    lows = list(symbol_data["low"])
    closes = list(symbol_data["close"])
    volumes = list(symbol_data["volume"])
    for i in range(len(dates)):
        
        d = [dates[i],spfloat(opens,i),spfloat(highs,i),spfloat(lows,i),spfloat(closes,i),spfloat(volumes,i)]
        d[0]=datetime.datetime.fromtimestamp(d[0]/1000)
        datalist.append(d)

    final_df = pd.DataFrame(datalist, columns=['date','open','high','low','close','volume'])
    final_df.set_index('date',inplace = True)


    # %%
    final_df.to_csv(outname+'.csv')
