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
