## we want to create a linear regression model
## using the gradient descent for minimizing the cost function
import numpy as np
import matplotlib.pyplot as plt


## lets first create some input and output values
n = 50
x = np.random.randint(low=1, high = 50, size = n)
y = 2 * x + 5

## the cost function for linear regression 
## is defined as mean squared errors 
## and we want to minimize this function
## by getting the partial derivative of slope and intercept
## and slowly change those variables
## to get to the least value for cost function
## so lets define a cost function
## which gets the slope and intercept as input
def cost_function(w, b, x, y):
    total_cost = 0
    N = x.shape[0]
    for xi, yi in zip(x, y):
        total_cost += (yi - (w*xi + b )) ** 2
    return total_cost/N
## we also need to have our optimization function
## which is gradient descent
def gradient_descent(w, b, x, y, learning_rate):
    n = x.shape[0]
    w_gradient = 0
    b_gradient = 0
    for xi, yi in zip(x, y):
        w_gradient += - (learning_rate * 2 * xi * (yi - (w * xi + b)))/n
        b_gradient += - (learning_rate * 2 * (yi - (w * xi + b)))/n
    w -= w_gradient
    b -= b_gradient 
    return w, b
## now we need to have some initial values for w and b
w = 0
b = 0
## and we also need the learning rate
learning_rate = 0.001
## and we loop through and calculate the values 
## for w and b, using the optimization function
for _ in range(700):
    w, b = gradient_descent(w, b, x, y, learning_rate)
    cost = cost_function(w, b, x, y)
    print(f'The cost function is : {cost}, for w = {w} and b = {b}')

## now calculating the yhat 
## using the optimized w and b
yhat = w * x + b

## and finally ploting the actual data vs regression line
plt.scatter(x = x, y = y, color = 'blue')
plt.plot(x, yhat, color = 'red')
plt.show()





