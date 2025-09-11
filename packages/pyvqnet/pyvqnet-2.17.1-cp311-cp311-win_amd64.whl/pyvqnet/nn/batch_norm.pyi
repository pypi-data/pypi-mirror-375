from ..device import DEV_CPU as DEV_CPU
from _typeshed import Incomplete
from pyvqnet.nn.module import Module as Module, Parameter as Parameter
from pyvqnet.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, tensor as tensor
from pyvqnet.utils.initializer import ones as ones, zeros as zeros
from typing import Callable

class BatchNormNd(Module):
    affine: Incomplete
    channel_num: Incomplete
    backend: Incomplete
    momentum: Incomplete
    beta: Incomplete
    gamma: Incomplete
    epsilon: Incomplete
    train_mode: bool
    def __init__(self, channel_num: int, momentum: float = 0.1, epsilon: float = 1e-05, affine: bool = True, beta_initializer: Callable = ..., gamma_initializer: Callable = ..., dtype: int | None = None, name: str = '') -> None: ...

class BatchNorm1d(BatchNormNd):
    '''Applies Batch Normalization over a 2D input (B,C) as described in the paper
    `Batch Normalization: Accelerating Deep Network Training by Reducing
    Internal Covariate Shift <https://arxiv.org/abs/1502.03167>`__ .

    .. math::

        y = \\frac{x - \\mathrm{E}[x]}{\\sqrt{\\mathrm{Var}[x] + \\epsilon}} * \\gamma + \\beta

    where :math:`\\gamma` and :math:`\\beta` are learnable parameters.
    Also by default, during training this layer keeps running
    estimates of its computed mean and variance,
    which are then used for normalization during evaluation.
    The running estimates are kept with a default momentum of 0.1.


    :param channel_num: `int` - the number of input features channels
    :param momentum: `float` - momentum when calculation exponentially weighted average,
     defaults to 0.1
    :param beta_initializer: `callable` - defaults to zeros
    :param gamma_initializer: `callable` - defaults to ones
    :param epsilon: `float` - numerical stability constant, defaults to 1e-5
    :param name: name of module,default:"".
    :return: a BatchNorm1d class

    Example::

        import numpy as np
        from pyvqnet.tensor import *
        from pyvqnet.nn import BatchNorm1d, BatchNorm2d
        test_conv = BatchNorm1d(4)
        test_conv.eval()
        x = QTensor(np.arange(1,17).reshape([4,4]),requires_grad=True)
        y = test_conv.forward(x)

    '''
    batchnorm: Incomplete
    def __init__(self, channel_num: int, momentum: float = 0.1, epsilon: float = 1e-05, affine: bool = True, beta_initializer: Callable = ..., gamma_initializer: Callable = ..., dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x) -> QTensor: ...

class BatchNorm2d(BatchNormNd):
    '''Applies Batch Normalization over a 4D input (B,C,H,W) as described in the paper
    `Batch Normalization: Accelerating Deep Network Training by Reducing
    Internal Covariate Shift <https://arxiv.org/abs/1502.03167>`__ .

    .. math::

        y = \\frac{x - \\mathrm{E}[x]}{\\sqrt{\\mathrm{Var}[x] + \\epsilon}} * \\gamma + \\beta

    where :math:`\\gamma` and :math:`\\beta` are learnable parameters.
    Also by default, during training this layer keeps running
    estimates of its computed mean and variance,
    which are then used for normalization during evaluation.
    The running estimates are kept with a default momentum of 0.1.

    :param channel_num: `int` - the number of input features channels
    :param momentum: `float` - momentum when calculation exponentially weighted average,
     defaults to 0.1
    :param beta_initializer: `callable` - defaults to zeros
    :param gamma_initializer: `callable` - defaults to ones
    :param epsilon: `float` - numerical stability constant, defaults to 1e-5
    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a BatchNorm2d class

    Example::

        import numpy as np
        from pyvqnet.tensor import *
        from pyvqnet.nn import BatchNorm1d, BatchNorm2d
        b= 2
        ic =2
        test_conv = BatchNorm2d(ic)
        #set train mode
        #test_conv.train()
        #set eval mode
        test_conv.eval()
        x = QTensor(np.arange(1,17).reshape([b,ic,4,1]),requires_grad=True)
        y = test_conv.forward(x)

    '''
    batchnorm: Incomplete
    def __init__(self, channel_num: int, momentum: float = 0.1, epsilon: float = 1e-05, affine: bool = True, beta_initializer: Callable = ..., gamma_initializer: Callable = ..., dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x) -> QTensor:
        """
        forward for batch norm layer
        """
