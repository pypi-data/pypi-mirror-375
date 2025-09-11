from ...tensor import to_tensor as to_tensor
from ...torch.initializer import he_uniform as he_uniform, zeros as zeros
from ..conv import Conv1D as NConv1D, Conv2D as NConv2D, ConvT2D as NConvT2D
from ..parameter import Parameter as Parameter
from .module import TorchModule as TorchModule
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock
from typing import Callable

class ConvT2D(TorchModule, NConvT2D):
    '''

    Transposed Convolution for 2d input.  
    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.

    :param input_channels: `int` - Number of input channels
    :param output_channels: `int` - Number of kernels
    :param kernel_size: `int` - Size of a single kernel. Each kernel is kernel_size x kernel_size
    :param stride: `tuple` - Stride, defaults to (1, 1)
    :param padding:  Padding, controls the amount of padding of the input. It can be a tuple of ints giving the amount of implicit padding applied on the input,defaults to (0,0)
    :param use_bias: `bool` - if use bias, defaults to True
    :param kernel_initializer: `callable` - Defaults to xavier_normal
    :param bias_initializer: `callable` - Defaults to zeros
    :param dilation_rate: `int` - Spacing between kernel elements. Default: 1
    :param out_padding: Additional size added to one side of each dimension in the output shape. Default: (0,0)
    :param group: `int` - Number of group. Default: 1

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a ConvT2D class

    '''
    out_padding: Incomplete
    def __init__(self, input_channels: int, output_channels: int, kernel_size: tuple[int, int] | list[int] | int, stride: tuple[int, int] | list[int] | int = (1, 1), padding: tuple[int, int] | list[int] | int = (0, 0), use_bias: bool = True, kernel_initializer: Callable | None = None, bias_initializer: Callable | None = None, dilation_rate: tuple[int, int] | list[int] | int = (1, 1), out_padding: tuple[int, int] | list[int] | int = (0, 0), group: int = 1, dtype: int | None = None, name: str = '') -> None: ...
    weights: Incomplete
    bias: Incomplete
    def reset_parameters(self, kernel_initializer, bias_initializer) -> None: ...
    def forward(self, x): ...

class Conv1D(TorchModule, NConv1D):
    '''

    Convolution for 1d input.

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.


    :param input_channels: `int` - Number of input channels.
    :param output_channels: `int` - Number of kernels.
    :param kernel_size: `int` - Size of a single kernel.
     kernel shape = [input_channels,output_channels,kernel_size,1].
    :param stride: `int` - Stride, defaults to (1, 1).
    :param padding: `str` - Padding, controls the amount of padding applied to the input. 
        It can be either a string {‘valid’, ‘same’} or a tuple of ints giving the amount of implicit padding applied on both sides.defaults to "valid"
    :param use_bias: `bool` - if use bias, defaults to True.
    :param kernel_initializer: `callable` - Defaults to _xavier_normal.
    :param bias_initializer: `callable` - Defaults to _zeros.
    :param dilation_rate: `int` - Dilation rate,defaults: 1.
    :param group: `int` -  Number of group. Default: 1.

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a Conv1D class
    '''
    def __init__(self, input_channels: int, output_channels: int, kernel_size: int, stride: int = 1, padding: str | int = 'valid', use_bias: bool = True, kernel_initializer: Callable | None = None, bias_initializer: Callable | None = None, dilation_rate: int = 1, group: int = 1, dtype: int | None = None, name: str = '') -> None: ...
    weights: Incomplete
    bias: Incomplete
    def reset_parameters(self, kernel_initializer, bias_initializer) -> None: ...
    def forward(self, x): ...

class Conv2D(TorchModule, NConv2D):
    '''

    Convolution for 2d input.

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.


    :param input_channels: `int` - Number of input channels
    :param output_channels: `int` - Number of kernels
    :param kernel_size: `tuple` - Size of a single kernel.
    :param stride: `tuple` - Stride, defaults to (1, 1)
    :param padding: Padding, controls the amount of padding of the input. It can be either a string {‘valid’, ‘same’} or a tuple of ints giving the amount of implicit padding applied on the input,defaults to "valid"
    :param use_bias: `bool` - if use bias, defaults to True
    :param kernel_initializer: `callable` - Defaults to _xavier_normal
    :param bias_initializer: `callable` - Defaults to _zeros
    :param dilation_rate: `int` - Spacing between kernel elements. Default: 1
    :param group: `int` - Number of group. Default: 1
    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a Conv2D class

    '''
    def __init__(self, input_channels: int, output_channels: int, kernel_size: tuple[int, int] | list[int] | int, stride: tuple[int, int] | list[int] | int = (1, 1), padding: tuple[int, int] | list[int] | int | str = 'valid', use_bias: bool = True, kernel_initializer: Callable | None = None, bias_initializer: Callable | None = None, dilation_rate: tuple[int, int] | list[int] | int = (1, 1), group: int = 1, dtype: int | None = None, name: str = '') -> None: ...
    weights: Incomplete
    bias: Incomplete
    def reset_parameters(self, kernel_initializer, bias_initializer) -> None: ...
    def forward(self, x): ...
Conv2d = Conv2D
