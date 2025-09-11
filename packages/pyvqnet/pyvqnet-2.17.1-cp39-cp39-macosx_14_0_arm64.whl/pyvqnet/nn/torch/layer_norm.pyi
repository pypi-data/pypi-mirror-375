from ... import DEV_CPU as DEV_CPU, tensor as tensor
from ...utils.initializer import ones as ones, zeros as zeros
from ..layer_norm import LayerNormNd as NLayerNormNd
from ..parameter import Parameter as Parameter
from .module import TorchModule as TorchModule
from pyvqnet.backends_mock import TorchMock as TorchMock

class LayerNormNd(TorchModule, NLayerNormNd):
    '''Applies Layer Normalization over a mini-batch of N-dim inputs as described in
    the paper `Layer Normalization <https://arxiv.org/abs/1607.06450>`__

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.

    .. math::
        y = \\frac{x - \\mathrm{E}[x]}{ \\sqrt{\\mathrm{Var}[x] + \\epsilon}} * \\gamma + \\beta

    The mean and standard-deviation are calculated over the last `D` dimensions size.
    
    For example, if :attr:`normalized_shape`
    is ``(3, 5)`` (a 2-dimensional shape), the mean and standard-deviation are computed over
    the last 2 dimensions of the input (i.e. ``input.mean((-2, -1))``).

    For input like (B,C,H,W,D), :attr:`norm_shape` can be [C,H,W,D],[H,W,D],[W,D] or [D].

    :param norm_shape: `float` - normalize shape
    :param epsilon: `float` - numerical stability constant, defaults to 1e-5
    :param affine: `bool` - whether use apply affine transform, defaults to True

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".

    :return: a LayerNormNd class
    '''
    def __init__(self, normalized_shape: int | list[int] | tuple[int, ...], epsilon: float = 1e-05, affine: bool = True, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...

class LayerNorm2d(LayerNormNd):
    '''Applies Layer Normalization over a mini-batch of 4 dim inputs as described in
    the paper `Layer Normalization <https://arxiv.org/abs/1607.06450>`__

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.

    .. math::
        y = \\frac{x - \\mathrm{E}[x]}{ \\sqrt{\\mathrm{Var}[x] + \\epsilon}} * \\gamma + \\beta

    The mean and standard-deviation are calculated over the last 3 dimensions size.


    For input like (B,C,H,W), :attr:`norm_shape` should be C * H * W. or [C * H * W].

    :param norm_shape: `int` - normalize shape
    :param epsilon: `float` - numerical stability constant, defaults to 1e-5
    :param affine: `bool` - whether use apply affine transform, defaults to True

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".

    :return: a LayerNorm2d class
    '''
    def __init__(self, normalized_shape: int | list[int] | tuple[int, ...], epsilon: float = 1e-05, affine: bool = True, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...

class LayerNorm1d(LayerNorm2d):
    '''Applies Layer Normalization over a mini-batch of 2 dim inputs as described in
    the paper `Layer Normalization <https://arxiv.org/abs/1607.06450>`__

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.

    .. math::
        y = \\frac{x - \\mathrm{E}[x]}{ \\sqrt{\\mathrm{Var}[x] + \\epsilon}} * \\gamma + \\beta

    The mean and standard-deviation are calculated over the last dimensions size.


    For input like (B,C), :attr:`norm_shape` should be C . or [C].

    :param norm_shape: `int` - normalize shape
    :param epsilon: `float` - numerical stability constant, defaults to 1e-5
    :param affine: `bool` - whether use apply affine transform, defaults to True

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".

    :return: a LayerNorm1d class
    '''
    def __init__(self, normalized_shape: int | list[int] | tuple[int, ...], epsilon: float = 1e-05, affine: bool = True, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...
LayerNorm = LayerNormNd
