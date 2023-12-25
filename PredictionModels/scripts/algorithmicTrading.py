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
           data.unstack('ticker')['dollar_volume'].resample('M').mean().stack('ticker').to_frame('dollar_volume')], axis = 1).dropna()
## now we want to calculate 5-year rolling average of dollar volume
monthly_data['dollar_volume_5_yr'] = monthly_data.loc[:,'dollar_volume'].unstack('ticker').rolling(5*12, min_periods = 12).mean().stack('ticker')
## then we want to rank the stock using the new metric
monthly_data['dollar_volume_ranking'] = monthly_data.groupby(level=0)['dollar_volume_5_yr'].rank(ascending = False)
## and only get the top 150 stockes
monthly_data = monthly_data[monthly_data['dollar_volume_ranking']<=150].drop(['dollar_volume_ranking', 'dollar_volume_5_yr','dollar_volume'], axis=1)
## now the next step is to calculate the monthly returns for different periods
## we need to define our own function
def calculate_return(df):
    lags = [1,2,3,6,9,12]
    outlier_cutoff = 0.005
    for lag in lags:
        df[f'return_{lag}m'] = df['adj close'].pct_change(lag).pipe(lambda x:x.clip(lower = x.quantile(outlier_cutoff),upper = x.quantile(1-outlier_cutoff))).add(1).pow(1/lag).sub(1)
    return df
monthly_data = monthly_data.groupby(level=1, group_keys = False).apply(calculate_return).dropna()

## now we need to download Fama-French Factors
## and calculate rolling factor betas
## this step is used to estimate the exposure of assets
## to the common risk factors using linear regression
## the five factors are market risk, size, value, operating profitability, annd investment
## we will use the pandas_datareader library for this
## and get the monthly level data 
factor_data = web.DataReader('F-F_Research_Data_5_Factors_2x3',
              'famafrench',
              start = '2010')[0].drop('RF', axis = 1)
## need to fix the index first
factor_data.index = factor_data.index.to_timestamp()
## and then fix the date to be the end of the month
## and getting the actual values instead of %
factor_data = factor_data.resample('M').last().div(100)
factor_data.index.name = 'date'
## now we need to join our factors with the 
## return_1m
factor_data = factor_data.join(monthly_data['return_1m']).sort_index()
## we want to remove the stocks with less than 10 months of data
valid_stocks = factor_data.groupby(level =1).size()[factor_data.groupby(level =1).size() >=10].index
## then using the valid stocks to filter out low data point tickers
factor_data = factor_data[factor_data.index.get_level_values('ticker').isin(valid_stocks)]
## now we're ready to calculate rolling factor betas
## using the RollingOLS from statmodels
## giving the return of 1m as endog and the rest of the df as exog
## with the window of 24 or the no of rows available for that ticker
## and then dropping the constant column
betas = factor_data.groupby(level=1, group_keys = False).apply(lambda x:RollingOLS(endog = x['return_1m'],
                                                                          exog=sm.add_constant(x.drop('return_1m', axis=1)),
                                                                          window = min(24, x.shape[0]),
                                                                          min_nobs = len(x.columns)+1).fit(params_only=True).params.drop('const', axis=1))
## we need to shift the betas for one month for each stock
## because these are the values we have at the begining of the month
## for instance, we will have the beta for Oct in Nov
## so before joining them with our main df 
## we need to fix that
monthly_data = monthly_data.join(betas.groupby(level=1).shift())
## we will have many missing values in the df
## and want to replace them with the mean value 
factors = ['Mkt-RF','SMB','HML','RMW','CMA']
monthly_data.loc[:, factors] = monthly_data.groupby(level=1, group_keys = False)[factors].apply(lambda x:x.fillna(x.mean()))
## we no longer need the adj close at this point
monthly_data.drop('adj close',axis=1, inplace = True)
## now we're ready to apply ML to our df
## we have 18 main features
## and want to decide at each month
## which stocks do we want to keep in our portfolio
## we could decide which stocks to long or to short
## and the volume in the portfolio
## at this point
## we have to decide on the ML and approach to use
## we want to use a supervised algorithm
## that can group these stocks
## and that's why we picked the k-means clustering method
## to group the stocks based on their features
## you can have pre-defined centroids for each cluster after doing some research
## lets start with k-means++ initialization and take it from there
## we have to specify how many clusters we want
## we can start with low numbers and take it from there
## to get the optimum number
## for this data, 4 seems to be a good number of clusters
from sklearn.cluster import KMeans
## we want to define a function
## that can assign clusters
def get_cluster(df):
    ## it'll create a KMeans model
    ## asking for 4 clusters
    ## making sure the result is re-creatable
    ## and telling it to use random initialization for our 1st model
    df['cluster'] = KMeans(n_clusters = 4,
                          random_state = 0,
                          init='random').fit(df).labels_
    return df
## now we want to apply the clustering function
clustered_data = monthly_data.dropna().groupby('date', group_keys = False).apply(get_cluster)
