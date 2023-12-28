## Twitter Sentiment Investing Strategy
## first we need to load the twitter sentiment dataset
## calculate the engagement ratio
## and filter out the stocks the don't have any activities
## first the packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
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
