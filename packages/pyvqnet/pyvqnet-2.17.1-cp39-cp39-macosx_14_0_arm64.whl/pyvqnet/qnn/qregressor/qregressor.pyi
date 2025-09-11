import abc
import numpy as np
from _typeshed import Incomplete
from abc import abstractmethod
from pyvqnet.qnn.measure import expval as expval
from qiskit.utils import QuantumInstance as QuantumInstance

def network(input_data, weights): ...

class ObjectiveFunction(metaclass=abc.ABCMeta):
    def __init__(self, X: np.ndarray, y: np.ndarray, neural_network) -> None:
        """
        Args:
            X: The input data.
            y: The target values.
            neural_network: An instance of an quantum neural network to be used by this
                objective function.
        """
    @abstractmethod
    def objective(self, weights: np.ndarray) -> float:
        """Computes the value of this objective function given weights.

        Args:
            weights: an array of weights to be used in the objective function.

        Returns:
            Value of the function.
        """
    @abstractmethod
    def gradient(self, weights: np.ndarray) -> np.ndarray:
        """Computes gradients of this objective function given weights.

        Args:
            weights: an array of weights to be used in the objective function.

        Returns:
            Gradients of the function.
        """

class BinaryObjectiveFunction(ObjectiveFunction):
    """An objective function for binary representation of the output,
    e.g. classes of ``-1`` and ``+1``."""
    def objective(self, weights: np.ndarray) -> float: ...
    def gradient(self, weights: np.ndarray) -> np.ndarray: ...

class QRegressor:
    init_weight: Incomplete
    def __init__(self, forward_func: Incomplete | None = None, init_weight: Incomplete | None = None, optimizer: Incomplete | None = None) -> None:
        """
        forward_func: An instance of an quantum neural network.
        init_weight: Initial weight for the optimizer to start from.
        optimizer: An instance of an optimizer to be used in training. When `None` defaults to L-BFGS-B.
        """
    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        Function operation to solve the optimal solution
        """
    def predict(self, X: np.ndarray):
        """
        Predict
        """
