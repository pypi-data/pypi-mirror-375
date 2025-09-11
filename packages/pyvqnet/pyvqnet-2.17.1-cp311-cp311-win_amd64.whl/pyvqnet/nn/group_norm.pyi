from ..device import DEV_CPU as DEV_CPU
from _typeshed import Incomplete
from pyvqnet.nn.module import Module as Module, Parameter as Parameter
from pyvqnet.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, tensor as tensor
from pyvqnet.utils.initializer import ones as ones, zeros as zeros

class _GroupNorm(Module):
    backend: Incomplete
    beta: Incomplete
    gamma: Incomplete
    epsilon: Incomplete
    affine: Incomplete
    num_channels: Incomplete
    num_groups: Incomplete
    def __init__(self, num_groups: int, num_channels: int, epsilon: float = 1e-05, affine: bool = True, dtype: int | None = None, name: str = '') -> None: ...

class GroupNorm(_GroupNorm):
    """Applies Group Normalization over a mini-batch of inputs.

    This layer implements the operation as described in
    the paper `Group Normalization <https://arxiv.org/abs/1803.08494>`__

    .. math::
        y = \\frac{x - \\mathrm{E}[x]}{ \\sqrt{\\mathrm{Var}[x] + \\epsilon}} * \\gamma + \\beta

    The input channels are separated into :attr:`num_groups` groups, each containing
    ``num_channels / num_groups`` channels. :attr:`num_channels` must be divisible by
    :attr:`num_groups`. The mean and standard-deviation are calculated
    separately over the each group. :math:`\\gamma` and :math:`\\beta` are learnable
    per-channel affine transform parameter vectors of size :attr:`num_channels` if
    :attr:`affine` is ``True``.

    :param num_groups (int): number of groups to separate the channels into
    :param num_channels (int): number of channels expected in input
    :param eps: a value added to the denominator for numerical stability. Default: 1e-5
    :param affine: a boolean value that when set to ``True``, this module
            has learnable per-channel affine parameters initialized to ones (for weights)
            and zeros (for biases). Default: ``True``.

    Shape:
        - Input: :math:`(N, C, *)` where :math:`C=\\text{num\\_channels}`
        - Output: :math:`(N, C, *)` (same shape as input)

    :return: a GroupNorm class

    Example::

        import numpy as np
        from pyvqnet.tensor import QTensor,kfloat32
        from pyvqnet.nn import GroupNorm
        test_conv = GroupNorm(2,10)
        x = QTensor(np.arange(0,60).reshape([2,10,3]),requires_grad=True,dtype=kfloat32)
        y = test_conv.forward(x)
        print(y)

    """
    group_norm: Incomplete
    def __init__(self, num_groups: int, num_channels: int, epsilon: float = 1e-05, affine: bool = True, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x) -> QTensor: ...
