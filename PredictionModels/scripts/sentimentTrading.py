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