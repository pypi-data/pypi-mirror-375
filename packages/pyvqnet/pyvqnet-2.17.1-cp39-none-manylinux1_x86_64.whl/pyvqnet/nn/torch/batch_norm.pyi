from ... import DEV_CPU as DEV_CPU, kint64 as kint64, tensor as tensor
from ...utils.initializer import ones as ones, zeros as zeros
from ..parameter import Parameter as Parameter
from .module import TorchModule as TorchModule
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock
from typing import Callable

class BatchNormNd(TorchModule):
    '''Applies Batch Normalization described in the paper
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
        :return: a BatchNormNd class


        '''
    affine: Incomplete
    channel_num: Incomplete
    backend: Incomplete
    momentum: Incomplete
    beta: Incomplete
    gamma: Incomplete
    epsilon: Incomplete
    train_mode: bool
    def __init__(self, channel_num: int, momentum: float = 0.1, epsilon: float = 1e-05, affine: bool = True, beta_initializer: Callable = ..., gamma_initializer: Callable = ..., dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...
BatchNorm2d = BatchNormNd
BatchNorm1d = BatchNormNd
