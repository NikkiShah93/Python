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
tickers = get_column_from_csv(f"{data_path}/Wilshire-5000-Stocks.csv", "Ticker")

for ticker in tickers:
    save_csv_from_yahoo(folder = f"{data_path}/stock_data", ticker=ticker)