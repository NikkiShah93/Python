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
data = yf.download(tickers = symbols_list,
                  start = start_date,
                  end = end_date)
