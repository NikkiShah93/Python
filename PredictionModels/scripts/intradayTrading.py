## Intra Day Strategy Using GARCH Model
## Using simulated daily data
## and the intraday 5-min data
## Define a function to fit GARCH Model
## on the daily data
## to predict one day ahead volatility
## in a rolling window
## Calculate prediction premium and form a daily signal from it
## Merge with intraday data and calculate intraday indicators to form the intraday signal
## Generate the position entry and hold until the end of day
## Finally, calculate the final strategy returns
## first the imports
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from arch import arch_model
import pandas as pd
import pandas_ta
import numpy as np
## then load the simulated daily and 5-min data
min_data_path = '../data/simulated_5min_data.csv'
daily_data_path = '../data/simulated_daily_data.csv'
## loading the data
daily_df = pd.read_csv(daily_data_path)
## fixig the date 
## and then set the index to be date
daily_df['Date'] = pd.to_datetime(daily_df['Date'])
daily_df = daily_df.set_index('Date')
## calculating the log return
daily_df['log_ret'] = np.log(daily_df['Adj Close']).diff()
daily_df = daily_df.drop('Unnamed: 7', axis =1)
intraday_5min_df = pd.read_csv(min_data_path)
intraday_5min_df['datetime'] = pd.to_datetime(intraday_5min_df['datetime'])
intraday_5min_df.drop('Unnamed: 6', axis= 1, inplace = True)
intraday_5min_df = intraday_5min_df.set_index('datetime')
intraday_5min_df['date'] = pd.to_datetime(intraday_5min_df.index.date)
## now we want to define a func 
## to fit the GARCH model 
## and predict 1-day ahead volatility 
## in a rolling window
## we will first calculate the 6-month
## rolling variance and then
## we are creating a function
## in a 6-month rolling window to fit 
## a garch model and predict
## the next day variance
## we need to test to find 
## what orders would work best 
## first, calculate the 6-month rolling variance
daily_df['variance'] = daily_df['log_ret'].rolling(180).var()
## for simplicity
## we will only use 2020 forward
daily_df = daily_df['2020-01-01':]
## and lets define the function
def predict_volatility(x):
    ## p is auto regressive order
    ## q is moving avg order
    garch_model = arch_model(y=x, p=1, q=3).fit(update_freq = 5, disp = 'off')
    ## then we want to forcast one day ahead
    ## and it will generate mean and var
    ## and we want to only get var
    variance_forcast = garch_model.forecast(horizon=1).variance.iloc[-1,0]
    return variance_forcast
## now we want to get the predictions of the model
daily_df['predictions'] = daily_df['log_ret'].rolling(180).apply(lambda x : predict_volatility(x))
## now we want to calculate 
## prediction premium
## and form a signal from it
## by calculating its 6-month
## rolling standard deviation
daily_df['prediction_premium'] = (daily_df['predictions']-daily_df['variance'])/daily_df['variance']
daily_df['premium_std'] = daily_df['prediction_premium'].rolling(180).std()
## and to get the daily signal
daily_df['signal_daily'] = daily_df.apply(lambda x: 1 if (x['prediction_premium'] > x['premium_std'] *1.5)
                                         else (-1 if  x['prediction_premium'] < x['premium_std'] *-1.5
                                              else np.nan), axis=1)
## we can plot a histogram
## to see how many long (1) signals
## and how many short (-1) signals 
## we have in the set
daily_df['signal_daily'].plot(kind = 'hist')
## we will be using the current day signal
## to predict the next day's values
## so we need to shift the signal by one
daily_df['signal_daily'] = daily_df['signal_daily'].shift(1)
## next, we want to merge the new df
## with the intraday df
## and calculate the intraday indicators
## to form the intraday signals
final_df = intraday_5min_df.reset_index().merge(daily_df[['signal_daily']].reset_index(),
                                    left_on = 'date',
                                    right_on = 'Date').set_index('datetime')
final_df.drop(['date', 'Date'], axis = 1, inplace = True)
## now we're ready to calculate the indicators
## usig the pandas_ta
final_df['rsi'] = pandas_ta.rsi(close = final_df['close'], length = 20)
## lower bound
final_df['lband'] = pandas_ta.bbands(close=final_df['close'], length = 20).iloc[:,0]
## upper bound
final_df['uband'] = pandas_ta.bbands(close = final_df['close'], length = 20).iloc[:,2]
## now we're ready to calculate intraday signal
## which we will define as
## rsi > 70 and and close > uband
final_df['signal_intraday'] = final_df.apply(lambda x: 1 if (x['rsi'] > 70 and x['close'] > x['uband'])
                                            else (-1 if (x['rsi'] < 30 and x['close'] < x['lband']) 
                                                 else np.nan),
                                             axis = 1)
## now we're ready to generate the position entry
## and hold until the end of the day
## the strategy is to short
## when both daily and intraday signals 
## are 1, and long when both are -1
final_df['return_sign'] = final_df.apply(lambda x: -1 if (x['signal_daily'] == 1 and x['signal_intraday'] == 1)
                                                        else (1 if (x['signal_daily'] == -1 and x['signal_intraday'] == -1)
                                                                 else np.nan),
                                        axis = 1)
## we will go into the position
## in the first signal of the day
## and hold for the entire day
## and we can have the first signal
## filling the rest of the day
final_df['return'] = final_df.groupby(pd.Grouper(freq='D'))['return_sign'].transform(lambda x : x.ffill())
final_df['forward_return'] = final_df['return'].shift(-1)
final_df['strategy_return'] = final_df['forward_return']*final_df['return_sign']
## and finally, we can calculate the daily return
daily_return_df = final_df.groupby(pd.Grouper(freq='D'))['strategy_return'].sum()
strategy_cumulative_return = np.exp(np.log1p(daily_return_df).cumsum()).sub(1)
## and plotting the strategy return
strategy_cumulative_return.plot(figsize = (20,10))
plt.title('Intraday Strategy Return')
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1))
plt.ylabel('Return')