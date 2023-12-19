## we'll use Yahoo Finance to get the data
import yfinance as yf 
## then we pass in a symbol for the stock we want to use
## this case Apple
apple = yf.Ticker("AAPL")
## this is an object
## we need to then query the historical data
apple = apple.history(perid = "max")
## this will give us a pandas df
## so we can use it like one
## first add the tomorrow's value to each row
apple["tomorrow"] = apple["Open"].shift(-1)
## we also need to add a flag to see if it's up or down
apple["target"] = (apple["Open"] < apple['tomorrow']).astype(int)
## we need to get rid of the extra columns
del apple["Dividends"]
del apple["Stock Splits"]

