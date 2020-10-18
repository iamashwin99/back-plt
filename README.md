# chikku strategy

* 5 min candle



# Buy signal

shadow not more than 30% in opposite dirn



buy and sell at 0.2% higer than High





def candle:

close above 9 and 21 ema

low below 9 and 21 ema

rsi>55

hi-low < 0.5% of close

if any red candle post this , they should Have not crossed Xcandles low





buy at @0.25% higer than xcandle high

sl - min(1% of trade ammt or double the size of candle body)

Targget :-  RR= 1 else if ( xclose>55Ema and xclose>VWAP xclose>144) for each true make rr+1  prefer  [8 34 55 144] 



min(^,volatility)

# Sell signal





# Order seizing 

single Trade capital (2k) = 10% of total capital (20k)

SL (200) = 10% of single Trade capital (2k) 

order quantity = SL/dif_in_close_and_minMax