from ... import DEV_CPU as DEV_CPU, tensor as tensor
from ...utils.initializer import ones as ones, zeros as zeros
from ..group_norm import _GroupNorm
from ..parameter import Parameter as Parameter
from .module import TorchModule as TorchModule
from pyvqnet.backends_mock import TorchMock as TorchMock

class GroupNorm(TorchModule, _GroupNorm):
    """Applies Group Normalization over a mini-batch of inputs.

    This layer implements the operation as described in
    the paper `Group Normalization <https://arxiv.org/abs/1803.08494>`__

    .. math::
        y = \\frac{x - \\mathrm{E}[x]}{ \\sqrt{\\mathrm{Var}[x] + \\epsilon}} * \\gamma + \\beta

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.

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

    """
    def __init__(self, num_groups: int, num_channels: int, epsilon: float = 1e-05, affine: bool = True, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...
