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
## now we want to plot our clusters
## for better understanding
## we will define a function for that as well
def plot_cluster(data):
    plt.style.use('ggplot')
    ## separating the clusters
    cluster_0 = data[data['cluster']==0]
    cluster_1 = data[data['cluster']==1]
    cluster_2 = data[data['cluster']==2]
    cluster_3 = data[data['cluster']==3]
    ## and then plotting scatter plots with them
    ## we will use RSI here, because we didn't normalize that matric
    plt.scatter(cluster_0.iloc[:,0],cluster_0.iloc[:,6], color = 'blue', label = 'Cluster 0')
    plt.scatter(cluster_1.iloc[:,0],cluster_1.iloc[:,6], color = 'green', label = 'Cluster 1')
    plt.scatter(cluster_2.iloc[:,0],cluster_2.iloc[:,6], color = 'black', label = 'Cluster 2')
    plt.scatter(cluster_3.iloc[:,0],cluster_3.iloc[:,6], color = 'red', label = 'Cluster 3')
    plt.legend()
    plt.show()
    return 0
## we want to plot for each month
for i in clustered_data.index.get_level_values('date').unique().tolist():
    g = clustered_data.xs(i)
    plt.title(f'Date {i}')
    ## uncomment if checking the graphs
    # plot_cluster(g)
## if we look at the plots, 
## we will notice that the clusters are assigned randomly
## and we want to change that
## the strategy would be to follow stock momentum
## in order to do that, we have to specify the centroids for our model
## and we'll be using the RSI values
target_rsi_values = [30, 45, 55, 70]
## we want the number of clusters, and number of features
initial_centroids = np.zeros((len(target_rsi_values), 18))
## and then use the target values in the RSI column of the array
initial_centroids[:,6] = target_rsi_values
## and use this centroid in our KMeans model
## create a new function (or modify the old one)
## to use the defined initial centroid
def get_cluster_with_init(df):
    df['cluster'] = KMeans(n_clusters = 4,
                          random_state = 0,
                          init=initial_centroids).fit(df).labels_
    return df
## and just apply the new function to the set
clustered_data = monthly_data.dropna().groupby('date', group_keys = False).apply(get_cluster_with_init)
## and then plot the new clusters
for i in clustered_data.index.get_level_values('date').unique().tolist():
    g = clustered_data.xs(i)
    plt.title(f'Date {i}')
    ## uncomment if checking the grapghs
    # plot_cluster(g)
## now we know if the stocks with high RSI are in cluster 3
## we want our porfolio to be stocks that are in that cluster
## for the previous perids
## now for the next step
## we want to for each month
## select assets based on the cluster
## and form a portfolio based on the Efficient Frontier max sharpe ratio optimization
## first we only get the stocks that are in a given cluster
## and if the momentum is persistent
## then those stocks should continue to outperform 
## in the following month
## we will pick cluster 3, 
## which seems to be having the stocks that we're interested
filtered_data = clustered_data[clustered_data['cluster'] ==3].copy()
## and then reset the index to have the tickers in the columns
filtered_data = filtered_data.reset_index(level = 1)
## then assign the 1st day of the next month,
## to the previous month clusters
filtered_data.index = filtered_data.index+pd.DateOffset(1)
filtered_data = filtered_data.reset_index().set_index(['date', 'ticker'])
## and now we want to create a dictionary
## that as the month as the key
## and the stocks as a list of vals for that key
months = filtered_data.index.get_level_values('date').unique().tolist()
stocks_dict = {}
for month in months:
    ## changing the ts to dt
    stocks_dict[month.strftime('%Y-%m-%d')] = filtered_data.xs(month).index.unique().tolist()
## the next step is to define the optimization function
## we will define a weight optimizer function 
## that'll be using PyPortfolioOpt and EfficientFrontier
## to optimize for weights
## we need to use the last year's prices 
## apply the single stock weight bounds constraint for diversification
## with min as half equaly weighed and max as 10% portfolio
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
## and then create the func
def optimize_weight(prices, lower_bound = 0):
    ## for calculating the returns
    ## we will use the expected returns
    ## and use the prices and 252 as freq 
    ## which is the # of date to trade in a year
    returns = expected_returns.mean_historical_return(prices = prices,
                              frequency = 252)
    ## and for our covariance
    ## we will use the risk models
    ## and supply the same vals
    cov = risk_models.sample_cov(prices = prices,
                     frequency = 252)
    ## and then we have to create the EF model
    ## and input the created vals in the prior step
    ## + the weight bounds and the solver
    ef = EfficientFrontier(expected_returns=returns,
                          cov_matrix=cov,
                          weight_bounds=(lower_bound,.1),
                          solver='SCS')
    ## for weights
    ## we will use max sharpe from EF
    weights = ef.max_sharpe()
    return ef.clean_weights()
## we need at least one year prior to the current df
## so we should download a new set of data
## with that start date
## we want to only get the stocks info 
## for the ones that we have in our current set
start_date = monthly_data.index.get_level_values('date').unique()[0]-pd.DateOffset(months=12)
end_date = monthly_data.index.get_level_values('date').unique()[-1]

stocks = monthly_data.index.get_level_values('ticker').unique().tolist()
fresh_data = yf.download(tickers = stocks, start = start_date, end = end_date)
## the next step will be
## to calculate the daily returns
## for each stock that could land in our pf
## and then loop over each month
## select the stocks, and calculate the weight
## for the next month
## and if the maximum sharpe fails for a month
## then we will use the equally-weighed weights
## and then calculate the daily returns
returns_df = np.log(fresh_data['Adj Close']).diff()
portfolio_df = pd.DataFrame()
## loop through the dictionary
for start_date in stocks_dict:
    try:
        ## end date will be the end of the current month
        end_date = (pd.to_datetime(start_date)+pd.offsets.MonthEnd(0)).strftime('%Y-%m-%d')
        ## and then we need to get the sctocks for that date
        stocks_to_use = stocks_dict[start_date]
        ## now we have to use our optimizer
        ## to calculate the weights
        optimization_start_date = (pd.to_datetime(start_date)-pd.DateOffset(months = 12)).strftime('%Y-%m-%d')
        optimization_end_date = (pd.to_datetime(start_date)-pd.DateOffset(days = 1)).strftime('%Y-%m-%d')
        ## and then create our optimization df
        optimization_df = fresh_data[optimization_start_date:optimization_end_date]['Adj Close'][stocks_to_use]
        ## supply the half of the equaly weighed stocks as lower bound
        lower_bound = round((1/len(stocks_to_use)*.5),3)
        ## for catching the cases that 
        ## max sharpe won't work
        ## we will just use the equal weights
        try:
            weights = optimize_weight(optimization_df,lower_bound=lower_bound)
            ## and then convert the weights to df
            ## so it'll be easy to merge with the returns df
            weights = pd.DataFrame(weights, index=pd.Series(0))
        except:
            print(f'Max Sharpe failed for {start_date}, replacing with equal weights')
            weights = pd.DataFrame({col:1/len(stocks_to_use) for col in stocks_to_use}, index = pd.Series(0))
        ## current month returns
        current_returns = returns_df[start_date:end_date]
        ## then we have to merge it with our weights 
        ## using the stocks ticker
        current_returns = current_returns.stack().to_frame('returns').reset_index(level=0)\
                            .merge(weights.stack().to_frame('weights').reset_index(level=0, drop=True),
                                  left_index=True,
                                  right_index=True)\
                            .reset_index().set_index(['Date', 'index']).unstack().stack()
        ## fixing the index names
        current_returns.index.names = ['date', 'ticker']
        ## and then calculating the daily weighted return for each stock
        current_returns['weighted_return'] = current_returns['weights']*current_returns['returns']
        ## and sum all of the returns to get the total daily return
        current_returns = current_returns.groupby(level=0)['weighted_return'].sum().to_frame('Strategy Return')
        ## and the last step would be to concat the returns df to the portfolio
        portfolio_df = pd.concat([portfolio_df, current_returns], axis = 0)
    except Exception as e:
        print(e)
portfolio_df.drop_duplicates(inplace = True)
## now we want to compare our returns with SP500
## we should download the SP500 stock
spy = yf.download(tickers = 'SPY',
                 start='2015-01-01',
                 end=dt.date.today())
spy_net = np.log(spy['Adj Close']).diff().to_frame().dropna().rename({'Adj Close':'SPY Buy&Hold'}, axis = 1)
portfolio_df_w_spy = portfolio_df.merge(spy_net, left_index=True, right_index=True)
## and calculate the cumulative return
portfolio_cumulative_return = np.exp(np.log1p(portfolio_df_w_spy).cumsum())-1
## and finally ploting the values
plt.style.use('ggplot')
portfolio_cumulative_return.plot(figsize=(20,10))
plt.title('Unsupervised Strategy Returns Over Time')
plt.show()
## which shows significantly better performance
## for stategy developed here