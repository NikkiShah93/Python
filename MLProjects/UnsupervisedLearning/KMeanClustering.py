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
    def euclidean_distance(data_point, centroids):
        return np.sqrt(np.sum((centroids - data_point)**2, axis=1))
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

            ## now we need to re-center our centroids
            ## using the calculated distances
            cluster_indices = []
            for i in range(self.k):
                ## we need the index
                ## of the points that belong
                ## to the current cluster
                cluster_indices.append(np.argwhere(y == i))
            ## and then we need to re-evaluate the centroids
            cluster_centroids = []
            for i, val in enumerate(cluster_indices):
                ## when we don't have any points
                ## belonging to that cluster
                ## we will just use the same center
                if len(val) == 0:
                    cluster_centroids.append(self.centroids[i])
                else:
                    ## otherwise, we want the average
                    ## of all the data points that were assigned
                    ## to that specific cluster
                    cluster_centroids.append(np.mean(X[val], axis=0)[0])
            ## and then creating the new centroids
            ## based on the new list
            ## and we can check to see if the change
            ## is less than a certain threshhold
            if np.max(self.centroids - np.array(cluster_centroids)) < 0.001:
                break
            else:
                self.centroids = np.array(cluster_centroids)
        ## and then finally, return the clusters/labels
        return y

## now let's test our class with some random data
x = np.random.randint(low=0, high=500, size = (300, 3))
kmmodel = KMeansClustering(k=4)
y = kmmodel.fit(x, max_iteration=50)
## the labels for each data point
print(y)
## and the calculated centroids
print(kmmodel.centroids)
## and then plot the result
fig = plt.figure(figsize=(10,5))
ax = fig.add_axes([.1,.1,.9,.9], projection='3d')
## and for the color of each cluster
## we will use the returned labels 
ax.scatter(x[:,0], x[:,1], x[:, 2], c=y)
## and showing the cluster centroids of the current model
ax.scatter(kmmodel.centroids[:,0], kmmodel.centroids[:,1], kmmodel.centroids[:,2], 
           c=range(kmmodel.centroids.shape[0]), marker='*', s=100)
ax.set_title('K-Means Clustering Result')
ax.set_xlabel(r'$x$')
ax.set_ylabel(r'$y$')
ax.set_zlabel(r'$z$')
plt.show()