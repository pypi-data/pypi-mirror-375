from _typeshed import Incomplete
from pyvqnet.nn.module import Module
from pyvqnet.tensor import tensor
from typing import Callable

__all__ = ['Conv1D', 'Conv2D', 'ConvT2D', 'check_conv_c_same']

def check_conv_c_same(x_c, w_c) -> None: ...

class Conv1D(Module):
    '''\\\n    1D Convolution module. Inputs to the conv module are of shape
    (batch_size, input_channels, height)

    :param input_channels: `int` - Number of input channels.
    :param output_channels: `int` - Number of kernels.
    :param kernel_size: `int` - Size of a single kernel.
     kernel shape = [input_channels,output_channels,kernel_size,1].
    :param stride: `int` - Stride, defaults to (1, 1).
    :param padding: `str` - Padding, controls the amount of padding applied to the input. It can be either a string {‘valid’, ‘same’} or a tuple of ints giving the amount of implicit padding applied on both sides.defaults to "valid"
    :param use_bias: `bool` - if use bias, defaults to True.
    :param kernel_initializer: `callable` - Defaults to _xavier_normal.
    :param bias_initializer: `callable` - Defaults to _zeros.
    :param dilation_rate: `int` - Dilation rate,defaults: 1.
    :param group: `int` -  Number of group. Default: 1.

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a Conv1D class

    Note:
        ``padding=\'valid\'`` is the same as no padding.

        out_length = ceil((input_size - (kerkel_size - 1) )/stride)

        ``padding=\'same\'`` pads the input so the output has the shape as the input.

        out_length = ceil(input_size/stride)

    Example::

        b= 2
        ic =3
        oc = 2
        test_conv = Conv1D(ic,oc,3,2,"same",True,initializer.ones,initializer.ones)
        x0 = QTensor(np.arange(1,b*ic*5*5 +1).reshape([b,ic,25]),requires_grad=True)
        x = test_conv.forward(x0)
        print(x)

    '''
    def __init__(self, input_channels: int, output_channels: int, kernel_size: int, stride: int = 1, padding: str | int = 'valid', use_bias: bool = True, kernel_initializer: Callable | None = None, bias_initializer: Callable | None = None, dilation_rate: int = 1, group: int = 1, dtype: int | None = None, name: str = '') -> None: ...
    weights: Incomplete
    bias: Incomplete
    def reset_parameters(self, kernel_initializer, bias_initializer) -> None: ...
    def forward(self, x: tensor.QTensor) -> tensor.QTensor: ...

class Conv2D(Module):
    '''
    Convolution module. Inputs to the conv module are of shape
     (batch_size, input_channels, height, width)

    :param input_channels: `int` - Number of input channels
    :param output_channels: `int` - Number of kernels
    :param kernel_size: `tuple` - Size of a single kernel.
    :param stride: `tuple` - Stride, defaults to (1, 1)
    :param padding: Padding, controls the amount of padding of the input. It can be either a string {‘valid’, ‘same’} or a tuple of ints giving the amount of implicit padding applied on the input,defaults to "valid"
    :param use_bias: `bool` - if use bias, defaults to True
    :param kernel_initializer: `callable` - Defaults to _xavier_normal
    :param bias_initializer: `callable` - Defaults to _zeros
    :param dilation_rate: `tuple` - Spacing between kernel elements. Default: (1,1)
    :param group: `int` - Number of group. Default: 1
    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a Conv2D class

    Note:
        ``padding=\'valid\'`` is the same as no padding.

        out_length = ceil((input_size - (kerkel_size - 1) )/stride)

        ``padding=\'same\'`` pads the input so the output has the shape as the input.

        out_length = ceil(input_size/stride)

    Example::

        import numpy as np
        from pyvqnet.tensor import QTensor
        from pyvqnet.nn import Conv2D
        import pyvqnet
        b= 2
        ic =3
        oc = 2
        test_conv = Conv2D(ic,oc,(3,3),(2,2),"same")
        x0 = QTensor(np.arange(1,b*ic*5*5+1).reshape([b,ic,5,5]),requires_grad=True,dtype=pyvqnet.kfloat32)
        x = test_conv.forward(x0)
        print(x)

    '''
    def __init__(self, input_channels: int, output_channels: int, kernel_size: tuple[int, int] | list[int] | int, stride: tuple[int, int] | list[int] | int = (1, 1), padding: tuple[int, int] | list[int] | int | str = 'valid', use_bias: bool = True, kernel_initializer: Callable | None = None, bias_initializer: Callable | None = None, dilation_rate: tuple[int, int] | list[int] | int = (1, 1), group: int = 1, dtype: int | None = None, name: str = '') -> None: ...
    weights: Incomplete
    bias: Incomplete
    def reset_parameters(self, kernel_initializer, bias_initializer) -> None: ...
    def forward(self, x: tensor.QTensor) -> tensor.QTensor:
        """
        forward function
        """
Conv2d = Conv2D

class ConvT2D(Module):
    '''
    ConvTransposed module. Inputs to the module are of shape
     (batch_size, input_channels, height, width)

    :param input_channels: `int` - Number of input channels
    :param output_channels: `int` - Number of kernels
    :param kernel_size: `int` - Size of a single kernel. Each kernel is kernel_size x kernel_size
    :param stride: `tuple` - Stride, defaults to (1, 1)
    :param padding:  Padding, controls the amount of padding of the input. It can be either a string {‘valid’, ‘same’} or a tuple of ints giving the amount of implicit padding applied on the input,defaults to "valid"
    :param use_bias: `bool` - if use bias, defaults to True
    :param kernel_initializer: `callable` - Defaults to xavier_normal
    :param bias_initializer: `callable` - Defaults to zeros
    :param dilation_rate: `int` - Spacing between kernel elements. Default: 1
    :param out_padding: Additional size added to one side of each dimension in the output shape. Default: (0,0)
    :param group: `int` - Number of group. Default: 1

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a ConvT2D class

    Note:
        ``padding=\'valid\'`` is the same as no padding.

        out_length = input_size*stride + (kerkel_size - stride)

        ``padding=\'same\'`` pads the input so the output has the shape as the input.

        out_length = input_size*stride

    Example::

        test_conv = ConvT2D(3, 2, [3, 3], [1, 1], "valid",True,initializer.ones, initializer.ones)
        x = QTensor(np.arange(1, 1 * 3 * 5 * 5+1).reshape([1, 3, 5, 5]), requires_grad=True)
        y = test_conv.forward(x)
        print(y)

    '''
    weights: Incomplete
    bias: Incomplete
    def reset_parameters(self, kernel_initializer, bias_initializer) -> None: ...
    out_padding: Incomplete
    def __init__(self, input_channels: int, output_channels: int, kernel_size: tuple[int, int] | list[int] | int, stride: tuple[int, int] | list[int] | int = (1, 1), padding: tuple[int, int] | list[int] | int | str = 'valid', use_bias: bool = True, kernel_initializer: Callable | None = None, bias_initializer: Callable | None = None, dilation_rate: tuple[int, int] | list[int] | int = (1, 1), out_padding: tuple[int, int] | list[int] | int = (0, 0), group: int = 1, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x: tensor.QTensor) -> tensor.QTensor: ...
