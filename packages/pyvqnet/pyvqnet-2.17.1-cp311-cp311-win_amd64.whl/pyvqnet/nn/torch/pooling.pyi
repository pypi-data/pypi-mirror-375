from ...tensor import to_tensor as to_tensor
from ...types import _padding_type, _size_type
from ..pooling import PoolingLayer as PoolingLayer
from .module import TorchModule as TorchModule
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock

class AdaptiveAvgPool2d(TorchModule):
    out_size: Incomplete
    def __init__(self, out_size, name: str = '') -> None: ...
    def forward(self, x): ...

class MaxPool1D(TorchModule, PoolingLayer):
    '''

    Max Pooling for 1d input.

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    :param kernel: size of the max pooling windows
    :param strides: factor by which to downscale
    :param padding: Implicit negative infinity padding to be added on both sides, must be >= 0 and <= kernel_size / 2 
    :param name: name of module,default:"".
    :return: MaxPool1D layer
    '''
    def __init__(self, kernel: _size_type, stride: _size_type, padding: _padding_type = 0, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...

class MaxPool2D(TorchModule, PoolingLayer):
    '''

    Max Pooling for 2d input.

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    :param kernel: size of the max pooling windows
    :param strides: factor by which to downscale
    :param padding: Implicit negative infinity padding to be added on both sides, must be >= 0 and <= kernel_size / 2 
    :param name: name of module,default:"".
    :return: MaxPool2D layer
    '''
    def __init__(self, kernel: _size_type, stride: _size_type, padding: _padding_type = (0, 0), dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...

class AvgPool1D(TorchModule, PoolingLayer):
    '''

    Avgerage Pooling for 1d input.

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    :param kernel: size of the max pooling windows
    :param strides: factor by which to downscale
    :param padding: Implicit negative infinity padding to be added on both sides, must be >= 0 and <= kernel_size / 2 
    :param name: name of module,default:"".
    :return: AvgPool1D layer
    '''
    def __init__(self, kernel: _size_type, stride: _size_type, padding: _padding_type = 0, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...

class AvgPool2D(TorchModule, PoolingLayer):
    '''

    Avgerage Pooling for 1d input.

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    :param kernel: size of the max pooling windows
    :param strides: factor by which to downscale
    :param padding: Implicit negative infinity padding to be added on both sides, must be >= 0 and <= kernel_size / 2 
    :param name: name of module,default:"".
    :return: AvgPool2D layer
    '''
    def __init__(self, kernel: _size_type, stride: _size_type, padding: _padding_type = (0, 0), dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...
