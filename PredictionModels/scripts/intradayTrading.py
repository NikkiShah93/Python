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
intraday_5min_df['log_ret'] = np.log(intraday_5min_df['close']).diff()
intraday_5min_df = intraday_5min_df.set_index('datetime')
