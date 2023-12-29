## Twitter Sentiment Investing Strategy
## first we need to load the twitter sentiment dataset
## calculate the engagement ratio
## and filter out the stocks the don't have any activities
## first the packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import yfinance as yf
import os
plt.style.use('ggplot')
## path to the twitter data
data_path = '../data/sentiment_data.csv'
sentiment_data = pd.read_csv(data_path)
sentiment_data['date'] = pd.to_datetime(sentiment_data['date'])
sentiment_data = sentiment_data.set_index(['date', 'symbol'])
## lets calculate the engagement ratio
## by dividing the comments by likes
## to have a way to filter
## the bot activities
sentiment_data['engagement_ratio'] = sentiment_data['twitterComments'].div(sentiment_data['twitterLikes'])
## then we want to filter out
## low likes/comments stocks
sentiment_data = sentiment_data[(sentiment_data['twitterLikes'] > 20) & (sentiment_data['twitterComments']>5)]
## now we want to get the monthly aggregate
## and calculate the average sentiment for the month
monthly_data = sentiment_data.unstack('symbol').resample('M')['engagement_ratio'].mean().stack('symbol').to_frame('engagement_ratio')
## now we want to ranke the stocks based on this value
monthly_data['rank'] = monthly_data.groupby(level=0)['engagement_ratio'].transform(lambda x:x.rank(ascending=False)) 
## now we want to select the top 5 stocks based on this ranking
monthly_data = monthly_data[monthly_data['rank'] <=5]
monthly_data = monthly_data.reset_index(level=1)
## because we want to use the data for the next month
## we will add one day to the date
monthly_data.index = monthly_data.index + pd.DateOffset(1)
monthly_data = monthly_data.reset_index().set_index(['date','symbol'])
## now we want to create a dictionary
## with dates and the stocks that we're interested
stocks_dict = {(x).strftime('%Y-%m-%d'):monthly_data.xs(x).index.get_level_values('symbol').unique().tolist() for x in monthly_data.index.get_level_values('date').unique().tolist()}
## and the next step would be to download the new prices
## and we need to get the stock list for that
stock_list = monthly_data.index.get_level_values('symbol').unique().tolist()
## get two year of data
start_date = dt.date.today() - pd.DateOffset(months=24)
end_date = dt.date.today()
stock_price = yf.download(tickers = stock_list, start = start_date, end = end_date)
## lets calculate the portfolio return
returns_df = np.log(stock_price['Adj Close']).diff().dropna()
portfolio_df = pd.DataFrame()
for day in stocks_dict:
    end_date = (pd.to_datetime(day)+pd.offsets.MonthEnd()).strftime('%Y-%m-%d')
    stocks_to_invest = stocks_dict[day]
    ## we want to have equally weighted portfolio
    temp_df = returns_df[day:end_date][stocks_to_invest].mean(axis=1).to_frame('portfolio_return')
    ## and add it to the portfolio
    portfolio_df = pd.concat([portfolio_df,temp_df], axis= 0)
## now we're ready to visualize the returns
## and compare it with NASDAQ/QQQ
## so we need to download the data
## for the same timeframe
start_date = dt.date.today() - pd.DateOffset(months=24)
end_date = dt.date.today()
qqq_df = yf.download(tickers = 'QQQ', start = start_date, end = end_date)
## and then calculate the NASDAQ returns
qqq_returns = np.log(qqq_df['Adj Close']).diff().to_frame('qqq_returns').dropna()
## now we're ready to merge our portfolio return
## with the nasdaq one
portfolio_df = portfolio_df.merge(qqq_returns, left_index = True, right_index = True)
## the next step would be to visualize
## first we want to get the cumsum of the returns
portfolio_cumulative_returns = np.exp(np.log1p(portfolio_df).cumsum()).sub(1)
portfolio_cumulative_returns.plot(figsize = (20,10))
plt.title('Twitter Sentiment Portfolio vs NASDAQ')
plt.ylabel('Return')