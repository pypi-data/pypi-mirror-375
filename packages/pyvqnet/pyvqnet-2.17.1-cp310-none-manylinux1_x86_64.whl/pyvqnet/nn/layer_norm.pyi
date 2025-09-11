from ..device import DEV_CPU as DEV_CPU
from _typeshed import Incomplete
from pyvqnet.nn.module import Module as Module, Parameter as Parameter
from pyvqnet.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, tensor as tensor
from pyvqnet.utils.initializer import ones as ones, zeros as zeros

class LayerNorm1d(Module):
    '''Applies Layer Normalization over a mini-batch of 2D inputs as described in
    the paper `Layer Normalization <https://arxiv.org/abs/1607.06450>`__

    .. math::
        y = \\frac{x - \\mathrm{E}[x]}{ \\sqrt{\\mathrm{Var}[x] + \\epsilon}} * \\gamma + \\beta

    The mean and standard-deviation are calculated over the last dimensions size, where `norm_size`
    is the value  of :attr:`norm_size`.

    :param norm_size: `float` - normalize size, equals to last dim
    :param epsilon: `float` - numerical stability constant, defaults to 1e-5
    :param affine: `bool` - whether use apply affine transform, defaults to True
    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".

    :return: a LayerNorm1d class

    Example::

        import numpy as np
        import pyvqnet
        from pyvqnet.tensor import QTensor
        from pyvqnet.nn.layer_norm import LayerNorm1d
        test_conv = LayerNorm1d(4)
        x = QTensor(np.arange(1,17).reshape([4,4]),requires_grad=True,dtype=pyvqnet.kfloat32)
        y = test_conv.forward(x)
        print(y)

    '''
    backend: Incomplete
    beta: Incomplete
    gamma: Incomplete
    epsilon: Incomplete
    layernorm: Incomplete
    affine: Incomplete
    norm_shape: Incomplete
    def __init__(self, norm_size: int, epsilon: float = 1e-05, affine: bool = True, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x) -> QTensor: ...

class LayerNorm2d(Module):
    '''Applies Layer Normalization over a mini-batch of 4D inputs as described in
    the paper `Layer Normalization <https://arxiv.org/abs/1607.06450>`__

    .. math::
        y = \\frac{x - \\mathrm{E}[x]}{ \\sqrt{\\mathrm{Var}[x] + \\epsilon}} * \\gamma + \\beta

    The mean and standard-deviation are calculated over the last  `D` dimensions size.

    For input like (B,C,H,W), :attr:`norm_size` should equals to C * H * W.

    :param norm_size: `float` - normalize size，equals to C * H * W
    :param epsilon: `float` - numerical stability constant, defaults to 1e-5
    :param affine: `bool` - whether use apply affine transform, defaults to True

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".

    :return: a LayerNorm2d class

    Example::

        import numpy as np
        import pyvqnet
        from pyvqnet.tensor import QTensor
        from pyvqnet.nn.layer_norm import LayerNorm2d
        ic = 4
        test_conv = LayerNorm2d(8)
        x = QTensor(np.arange(1,17).reshape([2,2,4,1]),requires_grad=True,dtype=pyvqnet.kfloat32)
        y = test_conv.forward(x)
        print(y)

    '''
    backend: Incomplete
    beta: Incomplete
    gamma: Incomplete
    epsilon: Incomplete
    layernorm: Incomplete
    affine: Incomplete
    norm_shape: Incomplete
    def __init__(self, norm_size: int, epsilon: float = 1e-05, affine: bool = True, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x) -> QTensor: ...

class LayerNormNd(Module):
    '''Applies Layer Normalization over a mini-batch of N-dim inputs as described in
    the paper `Layer Normalization <https://arxiv.org/abs/1607.06450>`__

    
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

    Example::

        import numpy as np
        from pyvqnet.tensor import QTensor,kfloat32
        from pyvqnet.nn.layer_norm import LayerNormNd
        ic = 4
        test_conv = LayerNormNd([2,2])
        x = QTensor(np.arange(1,17).reshape([2,2,2,2]),requires_grad=True,dtype=kfloat32)
        y = test_conv.forward(x)
        print(y)

    '''
    backend: Incomplete
    beta: Incomplete
    gamma: Incomplete
    epsilon: Incomplete
    layernorm: Incomplete
    normalized_shape: Incomplete
    begin_norm_axis: int
    affine: Incomplete
    def __init__(self, normalized_shape: int | list[int] | tuple[int, ...], epsilon: float = 1e-05, affine: bool = True, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x) -> QTensor: ...
LayerNorm = LayerNormNd
