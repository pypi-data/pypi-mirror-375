from _typeshed import Incomplete
from pyvqnet.backends import global_backend as global_backend
from pyvqnet.optim.optimizer import Optimizer as Optimizer
from pyvqnet.tensor import kfloat32 as kfloat32

vqnet_core: Incomplete

class Adam(Optimizer):
    """
    Adam: A Method for Stochastic Optimization (https://arxiv.org/abs/1412.6980)


    :param params: params of model which need to be optimized
    :param lr: learning_rate of model (default: 0.01)
    :param beta1: coefficients used for computing running averages of gradient and
     its square (default: 0.9)
    :param beta2: coefficients used for computing running averages of gradient and
     its square (default: 0.999)
    :param epsilon: term added to the denominator to improve numerical stability (default: 1e-8)
    :param weight_decay: weight decay (L2 penalty) (default: 0)
    :param amsgrad: whether to use the AMSGrad variant of this algorithm from
     the paper `On the Convergence of Adam and Beyond`_(default: False)
    :return: a Adam optimizer

    Example::

        from pyvqnet.optim import adam
        import numpy as np
        from pyvqnet.tensor import QTensor
        w = np.arange(24).reshape(1,2,3,4).astype(np.float64)
        param = QTensor(w)
        param.grad = QTensor(np.arange(24).reshape(1,2,3,4).astype(np.float64))
        params = [param]
        opti = adam.Adam(params)

        for i in range(1,3):
            opti.step()
    """
    beta1: Incomplete
    beta2: Incomplete
    epsilon: Incomplete
    t: int
    amsgrad: Incomplete
    weight_decay: Incomplete
    def __init__(self, params, lr: float = 0.01, beta1: float = 0.9, beta2: float = 0.999, epsilon: float = 1e-08, weight_decay: int = 0, amsgrad: bool = False) -> None: ...
    def update_params(self) -> None: ...

class AdamW(Optimizer):
    """
    Implements AdamW algorithm.


    :param params: params of model which need to be optimized
    :param lr: learning_rate of model (default: 0.01)
    :param beta1: coefficients used for computing running averages of gradient and
     its square (default: 0.9)
    :param beta2: coefficients used for computing running averages of gradient and
     its square (default: 0.999)
    :param epsilon: term added to the denominator to improve numerical stability (default: 1e-8)
    :param weight_decay: weight_decay ,default 0.01.
    :param amsgrad: whether to use the AMSGrad variant of this algorithm from
     the paper `On the Convergence of AdamW and Beyond`_(default: False)
    :return: a AdamW optimizer

    Example::

        from pyvqnet.optim import adam
        import numpy as np
        from pyvqnet.tensor import QTensor
        w = np.arange(24).reshape(1,2,3,4).astype(np.float64)
        param = QTensor(w)
        param.grad = QTensor(np.arange(24).reshape(1,2,3,4).astype(np.float64))
        params = [param]
        opti = adam.AdamW(params)

        for i in range(1,3):
            opti.step()
    """
    beta1: Incomplete
    beta2: Incomplete
    epsilon: Incomplete
    t: int
    weight_decay: Incomplete
    amsgrad: Incomplete
    def __init__(self, params, lr: float = 0.01, beta1: float = 0.9, beta2: float = 0.999, epsilon: float = 1e-08, weight_decay: float = 0.01, amsgrad: bool = False) -> None: ...
    def update_params(self) -> None: ...
