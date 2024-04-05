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

## now we create the 3d plot
ax = plt.subplot(projection="3d")
ax.plot_surface(X, Y, Z, cmap="viridis")

plt.show()

