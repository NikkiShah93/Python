## In this script we will go through the matplotlib library
## and explore different functionalities that can come in handy

## first the imports
import matplotlib.pyplot as plt
import numpy as np

## we will use numpy for generating data
x = np.linspace(-5, 5, 100)
y = np.sin(x)/(2 * np.pi) 

## the first/simple type of plot would be scatter
# plt.scatter(x, y, color = 'green', marker = '*', s = 50, alpha=0.5)
# plt.show()

## now lets generate an example for line plot
years = np.arange(2000, 2025, 1)
price = (np.sin(years/2)*np.cos(years)/2*np.pi) * 10000 + 500

## the default plot is a line plot 
plt.plot(years, price, color='green')
plt.show()
