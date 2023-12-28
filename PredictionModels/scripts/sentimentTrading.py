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