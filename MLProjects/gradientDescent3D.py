## gradient descent in 3d + visualization
import numpy as np
import matplotlib.pyplot as plt

## for this case, we will define a z function
## that depends on x and y
def z_function(x, y):
    return np.sin(5*x) * np.cos(5*y) / 5

## and now that we have two variables
## we need to get partial derivative of each
def calculate_gradient(x, y):
    ## first dz/dx which is 5*1/5*cos(5*x)*cos(5*y)
    ## then dz/dy which is -5*1/5*sin(5*x)*sin(5*y)
    return np.cos(5*x)*np.cos(5*y), -np.sin(5*x)*np.sin(5*y)

## now let's create a test input examples
x = np.arange(-1, 1, 0.05)
y = np.arange(-1, 1, 0.05)

## we need to create a mesh grid
## to have a grid of values, instead of lines
X, Y = np.meshgrid(x, y)
Z = z_function(X, Y)

## we need an initial position
starting_pos = (0.5, 0.5, z_function(0.5, 0.5))
## we also need a learning rate
learning_rate = 0.01
## now we create the 3d plot
## we need the computed_zorder to be False
## so we can actually see the point on the plot
## we also pass in the zorder to each part
ax = plt.subplot(projection="3d", computed_zorder = False)

## and now we want to loop and find the min
## we can instead of defining the range
## define a specific tolerance for the changes in loss function
## and when it became smaller, we can exit the loop
for _ in range(500):
    ## first calculating the derivatives for x and y
    dzdx, dzdy = calculate_gradient(starting_pos[0], starting_pos[1])
    ## then we update the x and y values
    new_x, new_y = starting_pos[0] - learning_rate *dzdx, starting_pos[1] - learning_rate * dzdy 
    ## and finally, we update the position
    starting_pos = (new_x, new_y, z_function(new_x, new_y))
    ax.plot_surface(X, Y, Z, cmap="YlGn", zorder=0)
    ax.scatter(starting_pos[0], starting_pos[1], starting_pos[2], color = 'red', zorder=1)
    plt.pause(0.001)
    ax.clear()

