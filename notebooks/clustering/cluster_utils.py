import numpy as np
import matplotlib.pyplot as plt
import pdb

import hdbscan
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def hdbscan_cluster(X, min_cluster_size=10, min_samples=15, cluster_selection_epsilon=0.0,
                    plot=1, dim3=False):
    '''
    Cluster the embeddings by hdbscan
    '''
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples = min_samples, 
                                cluster_selection_epsilon=cluster_selection_epsilon)
    cluster_labels = clusterer.fit_predict(X)

    if plot:
        if dim3:
            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=cluster_labels, cmap='viridis', s=1, alpha=0.5)
            ax.set_title(f'HDBSCAN Clustering with n={len(set(cluster_labels))} clusters')
            # plt.colorbar()
            plt.show()
        else:
            plt.figure(figsize=(10, 6))
            plt.scatter(X[:, 0], X[:, 1], c=cluster_labels, cmap='viridis', s=1, alpha=0.5)
            plt.title(f'HDBSCAN Clustering with n={len(set(cluster_labels))} clusters')
            plt.colorbar()
            plt.show()

    return cluster_labels


def kmeans_cluster(X, n_clusters=8, plot=1, dim3=False):
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(X)

    if plot:
        if dim3:
            fig = plt.figure(figsize=(10, 6))
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(X[:, 0], X[:, 1], X[:, 2], c=kmeans.labels_, cmap='viridis', s=1, alpha=0.7)
            ax.set_title("K-means Clustering, k = " + str(n_clusters))
            plt.show()
        else:
            plt.figure(figsize=(10, 6))
            plt.scatter(X[:, 0], X[:, 1], c=kmeans.labels_, cmap='viridis', s=1, alpha=0.7)
            plt.title("K-means Clustering, k = " + str(n_clusters))
            plt.xlabel("Dimension 1")
            plt.ylabel("Dimension 2")
            plt.colorbar()
            plt.show()
    return kmeans.labels_


def find_best_k(X, method='inertia', range_k=range(1, 11), plot=0):
    # return best k
    # methods can be 'inertia', 'silhouette'
    scores = []
    for k in range_k:
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(X)
        if method == 'inertia':
            scores.append(kmeans.inertia_)
        elif method == 'silhouette':
            scores.append(silhouette_score(X, kmeans.labels_))
        else:
            raise ValueError('unknown method %s' % method)

    if plot:
        plt.plot(range_k, scores)
        plt.title("Elbow Method")
        plt.xlabel("Number of clusters")
        plt.ylabel(method)
        plt.show()

    if method == 'inertia':
        best_score = np.amin(scores)
        best_k = range_k[np.argmin(scores)]
    elif method == 'silhouette':
        best_score = np.amax(scores)
        best_k = range_k[np.argmax(scores)]

    return best_k, best_score