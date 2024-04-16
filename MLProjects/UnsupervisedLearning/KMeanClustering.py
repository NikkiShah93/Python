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

## we will create a class for our k-mean cluster
class KMeansClustering:
    ## and the only param that we initially need
    ## is the number of clusters ie. k
    def __init__(self, k=3):
        self.k = k
        self.centroids = None
    ## we also need a static method
    ## to calculate the euclidean distance
    @staticmethod
    def euclidean_distance(data_point, centroid):
        return np.sqrt(np.sum((centroid - data_point)**2, axis=1))
    ## the next thing is to initiate
    ## the centroids, using the data
    def fit(self, X, max_iteration=100):
        ## we want to pick the initial 
        ## centroids based on the min and max
        ## values of each feature
        self.centroids = np.random.uniform(low = np.amin(X, axis=0), high=np.amax(X, axis=0), 
                                           size = (self.k, X.shape[1]))
        ## the next step is to calculate the distance
        ## between each data point and the centroids
        for _ in range(max_iteration):
            ## we need a list to keep track 
            ## of the assigned clusters 
            y = []
            for data_point in X:
                distance = KMeansClustering.euclidean_distance(data_point, self.centroids)
                ## and we will append the index
                ## of the closest centroid to the data poin
                y.append(np.argmin(distance))
            y = np.array(y)

