from _typeshed import Incomplete
from pyvqnet.backends import global_backend as global_backend
from pyvqnet.optim.optimizer import Optimizer as Optimizer

vqnet_core: Incomplete

class Adadelta(Optimizer):
    """
    ADADELTA: An Adaptive Learning Rate Method (https://arxiv.org/abs/1212.5701)


    :param params: params of model which need to be optimized
    :param lr: learning_rate of model (default: 0.01)
    :param beta: for computing a running average of squared gradients (default: 0.99)
    :param epsilon: term added to the denominator to improve numerical stability (default: 1e-8)
    :return: a Adadelta optimizer

    Example::

        from pyvqnet.optim import adadelta
        import numpy as np
        from pyvqnet.tensor import QTensor
        w = np.arange(24).reshape(1,2,3,4).astype(np.float64)
        param = QTensor(w)
        param.grad = QTensor(np.arange(24).reshape(1,2,3,4).astype(np.float64))
        params = [param]
        opti = adadelta.Adadelta(params)

        for i in range(1,3):
            opti._step()
    """
    epsilon: Incomplete
    beta: Incomplete
    t: int
    def __init__(self, params, lr: float = 0.01, beta: float = 0.99, epsilon: float = 1e-08) -> None: ...
    def update_params(self) -> None: ...
