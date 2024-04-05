## gradient descent in 2d and 3d + visualization
import numpy as np
import matplotlib.pyplot as plt

## lets start with a simple function for y

def y_function(x):
    return x**2

## and the derivative for this function will be 2*x
def y_derivative(x):
    return 2 * x

## and let's create some values for x and y
x = np.arange(-100, 100, 0.1)
y = y_function(x)

## lets start with an arbitrary starting position
starting_pos = (80, y_function(80))
## and we need to define a learning rate for our model
learning_rate = 0.01


for _ in range(200):
    ## the new value will be the starting position 
    ## updated by the learning rate * derivative
    new_x = starting_pos[0] - learning_rate * y_derivative(starting_pos[0])
    new_y = y_function(new_x)
    ## and then we update the starting positions
    starting_pos = (new_x, new_y)
    plt.plot(x, y)
    ## showing the starting position in the plot
    plt.scatter(starting_pos[0], starting_pos[1], color = 'red')
    ## in order to animate the optimization
    plt.pause(0.001)
    plt.clf()