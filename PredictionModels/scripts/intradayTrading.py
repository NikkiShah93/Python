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
import matplotlib
from arch import arch_model
from tqdm import tqdm
import pandas as pd
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
intraday_5min_df['date'] = intraday_5min_df.index.date
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
daily_df['variance'] = daily_df['Adj Close'].rolling(180).var()
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
daily_df['predictions'] = daily_df['Adj Close'].rolling(180).apply(lambda x : predict_volatility(x))
