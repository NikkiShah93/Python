import pandas as pd
## we'll use Yahoo Finance to get the data
import yfinance as yf 
## we also need the sklearn for ML
## we'll use random forest for this model
## it helps to avoid over-fitting the model
## can indentify non-linear relationships
from sklearn.ensemble import RandomForestClassifier
## we also need the precision score for performance measures
from sklearn.metrics import precision_score
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
## then we need to specify our predictors 
predictors = ["Close", "Volume", "High","Low"]
## now we have to pass in the training set to the model
model.fit(train[predictors], train["Target"])
## then test the model with testing set
## and then measure the accuracy
predictions = model.predict(test[predictors])
predictions = pd.Series(predictions, index= test.index)
score = precision_score(test["Target"], predictions)
print(score)

## now for back testing
## first, we need to create a prediction function

def predict(train, test, predictors, model):
    model.fit(train[predictors], train["Target"])
    predictions = model.predict(test[predictors])
    predictions = pd.Series(predictions, index = test.index, name = "Predictions")
    score = precision_score(test["Target"], predictions)
    combined = pd.concat([test['Target'], predictions], axis = 1)
    return combined

## then we need to write our back test function
## the start is defined to process 10 years of data (10x250)
## and step is defined to process one year at a time
def backtest(data, model, predictors, start = 2500, step = 250):
    ## we want to loop through our data 
    ## and make predictions, year-by-year
    all_predictions = []
    for i in range(start,data.shape[0], step):
        train = data.iloc[:i].copy()
        test = data.iloc[i:i+step].copy()
        predictions = predict(train, test, predictors, model)
        all_predictions.append(predictions)
    return pd.concat(all_predictions)
## now let's test everything
predictions = backtest(apple, model, predictors)
score = precision_score(predictions["Target"], predictions["Predictions"])
print(score)
## we're not doing that well
## and we need to add additional predictors into our model
## starting with more rolling averages 
## giving it more period breakdowns to compare the values
## dod, wow, mom, etc.
horizons = [2, 5, 30, 60, 90, 250, 500, 750, 1000]
new_predictors = []
## then we need to loop through
## and calculate the average
for h in horizons:
    ## lets get the rolling average for that period
    ## and then calculate the ratio
    rolling_average = apple.rolling(h).mean()
    ratio_column_name = f"Close_Ratio_{h}"
    apple[ratio_column_name] = apple["Close"]/rolling_average["Close"]
    ## lets also calculate the trend
    ## and get the sum of the days that the stock actually went up
    trend_column_name = f"Trend_{h}"
    apple[trend_column_name] = apple.shift(1).rolling(h).sum()["Target"]
    new_predictors.extend([ratio_column_name, trend_column_name])
## now we have more columns in our df
print(apple.head(10))
## there are many missing values
## so lets get rid of them
apple.dropna(inplace=True)
## now we need to re-create the model
model = RandomForestClassifier(n_estimators = 500, min_samples_split = 200, random_state = 1)
## and re-define the predict function
def predict(train, test, predictors, model):
    ## training the model the same as before
    model.fit(train[predictors], train["Target"])
    ## and this time, we want to get the probability
    ## getting all the rows but only the second column
    prediction = model.predict_proba(test[predictors])[:,1]
    ## now we want to give a higher threshold
    prediction[prediction >= 0.6] = 1
    prediction[prediction < 0.6] = 0
    prediction = pd.Series(prediction, index = test.index, name = "Predictions")
    combined = pd.concat([test["Target"], prediction], axis = 1)
    return combined
predictions = backtest(apple, model, new_predictors)
score = precision_score(predictions["Target"], predictions["Predictions"])
print(score)