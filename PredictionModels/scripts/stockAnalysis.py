## Invest Portfolio
## first the libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import time
import yfinance as yf
import os
import cufflinks as cf
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.subplots import make_subplots
import warnings
warnings.simplefilter("ignore")
init_notebook_mode(connected = True)
## to use plotly locally
cf.go_offline()
## the function to get column from csv
def get_column_from_csv(file, col_name):
    ## tries to load a file
    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        print(f"{file} does not exist!")
    else:
        return df[col_name]
## and the function that downloads the data
def save_csv_from_yahoo(folder, ticker):
    stock = yf.Ticker(ticker)
    try:
        print(f"get the data for {ticker}")
        ## getting the data for past 5 year
        data = stock.history(period = "5y")
        ## giving it a 2 sec break
        time.sleep(2)
        file_name = f"{folder}/{ticker.replace('.','_')}.csv"
        data.to_csv(file_name)
        print(f"file {file_name} has been saved")
    except Exception as e:
        print(f"Getting data for {ticker} had {e} issue!")

## getting the tickers for Wilshire
## in the data folder
data_path = "../data"
stock_data_path = f"{data_path}/stock_data"
tickers = get_column_from_csv(f"{data_path}/Wilshire-5000-Stocks.csv", "Ticker")

for ticker in tickers:
    save_csv_from_yahoo(folder = stock_data_path, ticker=ticker)
## end and start dates
start_date = dt.date.today() - pd.Dateoffset(months = 36)
end_date = dt.date.today()
## getting a df from csv
def get_stock_df_from_csv(folder, ticker):
    try:
        ## and getting the first colunn as index
        file_name = f"{folder}/{ticker.replace('.','_')}.csv"
        df = pd.read_csv(file_name, index_col = 0)
    except Exception as e:
        print(f"{file_name} had {e} issue!")
    else:
        return df
## only getting the stocks that have been downloaded
files = [f for f in os.listdir(stock_data_path) if f.endswith('.csv')]
tickers = [os.path.splitext(x)[0] for x in files if os.path.splitext(x)[0]!= '.ds_Store']
## we're only interested in returns
def add_daily_return(df):
    ## today's close / yesterday's
    df['daily_return'] = (df['Close']/df['Close'].shift(1)) - 1
    ## or np.log(df['Close']).diff()
    return df
def add_cum_return(df):
    df['cum_return'] = (1 + df['daily_return']).cumprod()
    ## or np.exp(np.log1p(df['daily_return']).cumsum()).sub(1)
    return df 
## now adding the Bollinger Bands
## BB plot 2 lines using a moving average 
## and the standard deviation defines how apart
## the lines will be
def add_bollinger_bands(df, window = 20):
    df['middle_band'] = df['Close'].rolling(window = window).mean()
    df['upper_band'] = df['middle_band'] + 1.96 * df['Close'].rolling(window=window).std()
    df['lower_band'] = df['middle_band'] + 1.96 * df['Close'].rolling(window=window).std()
    return df
## now the Ichimoku
## which is considered an all in one indicator
## and provides information on momentum
## and is made up of 5 lines
## Conversion Line - represent support, resistance and reversals
## Baseline - represent support, resistance and confirms trend changes
## Leading Span A - used to identify future areas of support and resistance
## Leading Span B - used to identify future areas of support and resistance
## Lagging Span - shows possible support and resistance
## Cloud - space between Span A & B, represents the divergence in price evolution

## Formulas
## Lagging Span = price shifted back 26 periods
## Baseline = (Highest Value in Period / Lowest Value in Period)/2 (26 sessions)
## Conversion Line = (Highest Value in Period / Lowest Value in Period)/2 (9 sessions)
## Leading Span A = (Conversion Value + Base Value)/2 (26 sessions)
## Leading Span B = (Conversion Value + Base Value)/2 (52 sessions)
def add_Ichimoku(df):
    df['conversion_line'] = (df['High'].rolling(9).max() + df['Low'].rolling(9).min())/2
    df['baseline'] = (df['High'].rolling(26).max() + df['Low'].rolling(26).min())/2
    df['leading_span_a'] = ((df['conversion_line'] + df['baseline'])/2).shift(26)
    df['leading_span_b'] = ((df['High'].rolling(52).max() + df['Low'].rolling(52).min())/2).shift(26)
    df['lagging_span'] = (df['Close'].shift(-26)) 
    return df
## now adding the indicators to our data
stock_data_w_ind_path =  f"{data_path}/stock_data_w_indicators"
for t in tickers:
    try:
        print(f"working on:{t}")
        new_df = get_stock_df_from_csv(folder = stock_data_path, ticker = t)
        new_df = add_daily_return(new_df)
        new_df = add_cum_return(new_df)
        new_df = add_bollinger_bands(new_df)
        new_df = add_Ichimoku(new_df)
        new_df.to_csv(f"{stock_data_path}/{t}.csv")
    except Exception as e:
        print('No file was found!')
## for plotting candlesticks
def plot_with_boll_bands(df, ticker):
    fig = go.figure()
    candle = go.Candlestick(x = df.index,
                            open = df['Open'], high = df['High'], 
                            low = df['Low'], close = df['Close'], 
                            name = "Candlestick")
    ## the line = is for styling
    upper_line = go.Scatter(x = df.index, y = df['upper_band'], 
                            line = dict(color='rgba(250, 0, 0,0.75)', 
                                        width=1), 
                            name = "Upper Band")
    mid_line = go.Scatter(x = df.index, y = df['middle_band'], 
                            line = dict(color='rgba(0, 0, 250,0.75)', 
                                        width=1), 
                            name = "Middle Band")
    lower_line = go.Scatter(x = df.index, y = df['lower_band'], 
                            line = dict(color='rgba(0, 250, 0,0.75)', 
                                        width=0.7), 
                            name = "Lower Band")
    ## to add the plot to the screen
    fig.add_trace(candle)
    fig.add_trace(upper_line)
    fig.add_trace(mid_line)
    fig.add_trace(lower_line)
    ## then we have to change some things
    ## and add the cabability to zoon in and out with rangeslider
    fig.update_xaxes(title = "Date", rangeslider_visible = True)
    fig.update_yaxes(title = "Price", rangeslider_visible = True)
    fig.update_layout(title = f"{ticker} Bollinger Bands", height = 1200, 
                      width = 1800, showlegend=True)
    fig.show()