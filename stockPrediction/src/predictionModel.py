## we'll use Yahoo Finance to get the data
import yfinance as yf 
## we also need the sklearn for ML
## we'll use random forest for this model
## it helps to avoid over-fitting the model
## can indentify non-linear relationships
from sklearn.ensemble import RandomForestClassifier
## then we pass in a symbol for the stock we want to use
## this case Apple
apple = yf.Ticker("AAPL")
## this is an object
## we need to then query the historical data
apple = apple.history(perid = "max")
## this will give us a pandas df
## so we can use it like one
## first, we need to get rid of the extra columns
del apple["Dividends"]
del apple["Stock Splits"]
## then add the tomorrow's value to each row
apple["Tomorrow"] = apple["Close"].shift(-1)
## we also need to add a flag to see if it's up or down
apple["Target"] = (apple["Close"] < apple['Tomorrow']).astype(int)
## we only care about the last 10 years of data
apple = apple.loc["2013-01-01":].copy()
## let's work on the actual model
## we'll start with a low estimator for now
## and split the data to help avoid over-fitting
## and random state of 1
## to have more control over the model
model = RandomForestClassifier(n_estimators=100, min_samples_split=50, random_state=1)
## we need to use the past data for training
## to avoid the leakage 
train = apple.iloc[:-100]
test = apple.iloc[-100:]
