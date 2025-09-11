import abc
from ..device import DEV_CPU as DEV_CPU
from ..types import _padding_type, _size_type
from .functional import adaptive_avg_pool2d as adaptive_avg_pool2d
from _typeshed import Incomplete
from abc import abstractmethod
from pyvqnet.nn.module import Module as Module
from pyvqnet.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, tensor as tensor

class AdaptiveAvgPool2d(Module):
    out_size: Incomplete
    def __init__(self, out_size, name: str = '') -> None: ...
    def forward(self, x): ...

class PoolingLayer(Module, metaclass=abc.ABCMeta):
    """
    PoolingLayer
    """
    pool_func: Incomplete
    kernel: Incomplete
    stride: Incomplete
    padding: Incomplete
    backend: Incomplete
    @abstractmethod
    def __init__(self, kernel: _size_type, stride: _size_type, padding: _padding_type = 'valid', name: str = ''):
        """
        Represents abstract pooling layer
        """
    def forward(self, x) -> QTensor: ...

class MaxPool1D(PoolingLayer):
    '''
    Max pooling layer
    reference https://pytorch.org/docs/stable/generated/nn.MaxPool1d.html#nn.MaxPool1d

    :param kernel: size of the max pooling windows
    :param strides: factor by which to downscale
    :param padding: one of "none", "valid" or "same"
    :param name: name of module,default:"".
    :return: MaxPool1D layer

    Note:
        ``padding=\'valid\'`` is the same as no padding.

        out_length = ceil((input_size - (kerkel_size - 1) )/stride)

        ``padding=\'same\'`` pads the input so the output has the shape as the input.

        out_length = ceil(input_size/stride)

    Example::

        import numpy as np
        from pyvqnet.tensor import QTensor
        from pyvqnet.nn import MaxPool1D
        test_mp = MaxPool1D([3],[2],"same")
        x= QTensor(np.array([0, 1, 0, 4, 5,
                                    2, 3, 2, 1, 3,
                                    4, 4, 0, 4, 3,
                                    2, 5, 2, 6, 4,
                                    1, 0, 0, 5, 7],dtype=float).reshape([1,5,5]),requires_grad=True)

        y= test_mp.forward(x)
        print(y)

    '''
    pool_func: Incomplete
    def __init__(self, kernel: _size_type, stride: _size_type, padding: _padding_type = 'valid', name: str = '') -> None: ...
    def forward(self, x) -> QTensor: ...

class AvgPool1D(PoolingLayer):
    '''
    Average pooling layer
    reference https://pytorch.org/docs/stable/generated/nn.AvgPool1d.html#nn.AvgPool1d

    :param kernel: size of the average pooling windows
    :param strides: factor by which to downscale
    :param padding: one of "none", "valid" or "same"
    :param name: name of module,default:"".
    :return: AvgPool1D layer

    Note:
        ``padding=\'valid\'`` is the same as no padding.

        out_length = ceil((input_size - (kerkel_size - 1) )/stride)

        ``padding=\'same\'`` pads the input so the output has the shape as the input.

        out_length = ceil(input_size/stride)

    Example::

        import numpy as np
        from pyvqnet.tensor import QTensor
        from pyvqnet.nn import AvgPool1D
        test_mp = AvgPool1D([3],[2],"same")
        x= QTensor(np.array([0, 1, 0, 4, 5,
                                    2, 3, 2, 1, 3,
                                    4, 4, 0, 4, 3,
                                    2, 5, 2, 6, 4,
                                    1, 0, 0, 5, 7],dtype=float).reshape([1,5,5]),requires_grad=True)

        y= test_mp.forward(x)
        print(y)

    '''
    pool_func: Incomplete
    def __init__(self, kernel: _size_type, stride: _size_type, padding: _padding_type = 'valid', name: str = '') -> None: ...
    def forward(self, x) -> QTensor: ...

class MaxPool2D(PoolingLayer):
    '''
    Max pooling layer
    reference https://pytorch.org/docs/stable/generated/nn.MaxPool2d.html?highlight=pooling

    :param kernel: size of the max pooling windows
    :param strides: factor by which to downscale
    :param padding: one of "none", "valid" or "same"
    :param name: name of module,default:"".
    :return: MaxPool2D layer

    Note:
        ``padding=\'valid\'`` is the same as no padding.

        out_length = ceil((input_size - (kerkel_size - 1) )/stride)

        ``padding=\'same\'`` pads the input so the output has the shape as the input.

        out_length = ceil(input_size/stride)

    Example::

        test_mp = MaxPool2D([2,2],[2,2],"same")
        x= QTensor(np.array([0, 1, 0, 4, 5, 4,
                                    2, 3, 2, 1, 3, 4,
                                    4, 4, 0, 4, 3, 4,
                                    2, 5, 2, 6, 4, 3,
                                    1, 0, 0, 5, 7, 2],dtype=float).reshape([1,1,6,6]),
                                    requires_grad=True)

        y= test_mp.forward(x)

    '''
    pool_func: Incomplete
    stride: Incomplete
    padding: Incomplete
    def __init__(self, kernel: _size_type, stride: _size_type, padding: _padding_type = 'valid', name: str = '') -> None: ...
    def forward(self, x): ...

class AvgPool2D(PoolingLayer):
    '''    Perform 2D average pooling.

    reference:
        https://pytorch.org/docs/stable/generated/nn.AvgPool2d.html?highlight=avgpooling

    :param kernel: size of the average pooling windows
    :param strides: factors by which to downscale
    :param padding: one of  "valid" or "same"

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: AvgPool2D layer

    Note:
        ``padding=\'valid\'`` is the same as no padding.

        out_length = ceil((input_size - (kerkel_size - 1) )/stride)

        ``padding=\'same\'`` pads the input so the output has the shape as the input.

        out_length = ceil(input_size/stride)

    Example::

        test_mp = AvgPool2D([2,2],[2,2],"same")
        x= QTensor(np.array([0, 1, 0, 4, 5, 4,
                                    2, 3, 2, 1, 3, 4,
                                    4, 4, 0, 4, 3, 4,
                                    2, 5, 2, 6, 4, 3,
                                    1, 0, 0, 5, 7, 2],dtype=float).reshape([1,1,6,6]),
                                    requires_grad=True)

        y= test_mp.forward(x)

    '''
    pool_func: Incomplete
    def __init__(self, kernel: _size_type, stride: _size_type, padding: _padding_type = 'valid', name: str = '') -> None: ...
    def forward(self, x): ...
