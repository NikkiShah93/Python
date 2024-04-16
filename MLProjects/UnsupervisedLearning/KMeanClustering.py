## K-Means Clustering Project
## we will implement this algorithm
## from scratch using mainly numpy

## this is an unsupervised learning
## where we find clusters of data
## without any pre-defined labels

## k is the number of clusters
## we're looking for, which is defined by us
## we create random centroids for our data
## and then calculated the distance between
## the centroids and the data points
## and based on the calculated distance
## the model will assign a cluster to the points
## and then the next step is to re-position
## the centroids based on the assigned clusters
## and then repeat the first step again
## and re-calculate the distance between
## points and the new centroids
## and we can abort this process
## by either defining a max iteration #
## or a certain target in terms of changes
## from one iteration to the next

## first the imports
import numpy as np
import matplotlib.pyplot as plt