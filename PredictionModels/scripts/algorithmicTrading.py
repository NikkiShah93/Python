## packages required for this module
## pandas, numpy, matplotlib, statmodels, pandas_datareader, datetime, yfinance, sklearn, PyPortfolioOpt

## lets first import all the packages we need
import yfinance as yf
import pandas as pd
import numpy as np
from statsmodels.regression.rolling import RollingOLS
import statsmodels.api as sm
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import datetime as dt
import pandas_ta
import warnings
warnings.filterwarnings('ignore')

## next we want to get the list
## of the SP500 companies
## https://en.wikipedia.org/wiki/List_of_S%26P_500_companies
sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
## we only need the symbols
## and we need to do some cleanings on that field
## replacing dots with dashes and
## getting rid of the spaces, and making sure they're all uppercased
sp500['Symbol'] = sp500['Symbol'].str.replace('.','-').str.upper().str.strip()
## and then getting all the unique values, as a list
symbols_list = sp500['Symbol'].unique().tolist()

## lets define our start and end dates
## going back 8 years
end_date = '2023-12-20'
start_date = pd.to_datetime(end_date) - pd.DateOffset(365*8)
## lets download the SP500 stock prices
## we will use stack so it'd be easier to work with the df
data = yf.download(tickers = symbols_list,
                  start = start_date,
                  end = end_date).stack()
## we then want to assign names to each index
data.index.names = ['date', 'ticker']
## makeing all the column names lower
data.columns = data.columns.str.lower()
## in the next step
## we want to start calculating the features and indicators for each stock
## 1. Garman-Klass Volatility
## 2. RSI
## 3. Bollinger Bands
## 4. ATR
## 5. MACD
## 6. Dollar Volume

## German-Klass gives a measure over volatility of an asset
data['german_klass_vol'] = ((np.log(data['high'])-np.log(data['low']))**2)/2-(2*np.log(data['adj close'])-1)*(np.log(data['adj close'])-np.log(data['open']))**2
## then for RSI we use the pandas_ta library
## we have to group the df by ticker and then apply the function
data['rsi'] = data.groupby(level=1)['adj close'].transform(lambda x:pandas_ta.rsi(close=x, length = 20))
## now for the Bollinger Bands
## we will use pandas_ta
## and get low, mid, and high values
data['bb_low'] = data.groupby(level=1)['adj close'].transform(lambda x: pandas_ta.bbands(close=np.log1p(x), length = 20).iloc[:,0])
data['bb_mid'] = data.groupby(level=1)['adj close'].transform(lambda x: pandas_ta.bbands(close=np.log1p(x), length = 20).iloc[:,1])
data['bb_high'] = data.groupby(level=1)['adj close'].transform(lambda x: pandas_ta.bbands(close=np.log1p(x), length = 20).iloc[:,2])
## for ATR
## we need 3 columns, so we can't use transform and need to use apply
## and we need to define a function to calculate the values
def compute_atr(stock_data):
    ## the atr fn takes 3 inputs
    ## high, low, and close
    atr = pandas_ta.atr(high = stock_data['high'],
                   low = stock_data['low'],
                   close = stock_data['close'],
                   length = 14)
    ## and we need to return a normalized df
    ## so we sub mean and div by std
    return atr.sub(atr.mean()).div(atr.std())
## now we need to calculate the ATR
data['atr'] = data.groupby(level=1, group_keys = False).apply(compute_atr)
## for MACD
## we need to define our own duction 
def compute_macd(close):
    macd = pandas_ta.macd(close = close, length=20).iloc[:,0]
    return macd.sub(macd.mean()).div(macd.std())
data['macd'] = data.groupby(level=1, group_keys = False)['adj close'].apply(compute_macd)
## for Dollar Volume
## we have to divide by 1m 
data['dollar_volume'] = (data['adj close']*data['volume'])/1e6
## now for the next step
## we want to aggregate to monthly level
## and then get the top 150 most liquid stock for each month
## to reduce the training time and experiment w featurs & stategies
## for the dollar volume, we only need to get the monthly mean for each stock
## list of columns we want to operate on 
skip_list = ['dollar_volume', 'volume', 'open','high','low', 'close']
last_cols = [c for c in data.columns if c not in skip_list]
monthly_data = pd.concat([data.unstack('ticker')[last_cols].resample('M').last().stack('ticker'),
           data.unstack('ticker')['dollar_volume'].resample('M').mean().stack('ticker').to_frame('dollar_volume')], 
          axis = 1)


