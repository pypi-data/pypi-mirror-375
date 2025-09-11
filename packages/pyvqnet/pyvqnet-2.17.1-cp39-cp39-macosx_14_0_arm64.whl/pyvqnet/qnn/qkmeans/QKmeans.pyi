from .circuit import QKmeansCircuits as QKmeansCircuits
from _typeshed import Incomplete
from pyqpanda import CPUQVM as CPUQVM
from pyvqnet.nn.module import Module as Module, Parameter as Parameter
from pyvqnet.tensor import tensor as tensor

class QKmeans:
    '''
    Quantum K-means clustering algorithm.

        Example::
            from circuit import QKmeansCircuits
            from QKmeans import QKmeans
            import numpy as np
            import matplotlib.pyplot as plt
            if __name__ == "__main__":
            qkmeans = QKmeans(k=3, epoch=5, num_qubits=3)
            qkmeans.run()
    '''
    k: Incomplete
    epoch: Incomplete
    qkmeans_circuits: Incomplete
    def __init__(self, k: int = 3, epoch: int = 5, num_qubits: int = 3) -> None:
        """

        :param k: int, optional (default=3)
            The number of clusters (centroids) to partition the data into.

        :param epoch: int, optional (default=5)
            The number of iterations the K-means algorithm will run.

        :param num_qubits: int, optional (default=3)
            The number of quantum bits (qubits) to be used in the quantum circuit for calculating distances between data points and centroids.
        """
    def initialize_centers(self, points): ...
    def find_nearest_neighbour(self, points, centroids): ...
    def find_centroids(self, points, centers): ...
    def preprocess(self, points): ...
    def draw_plot(self, points, centroids: Incomplete | None = None, label: bool = True) -> None: ...
    def run(self, n: int = 100, std: int = 2) -> None: ...
    def get_data(self, n, k, std): ...
