from ..device import DEV_CPU as DEV_CPU
from _typeshed import Incomplete
from pyvqnet.nn.module import Module as Module, Parameter as Parameter
from pyvqnet.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, no_grad as no_grad
from pyvqnet.utils.initializer import zeros as zeros
from typing import Callable

class Identity(Module):
    """A placeholder identity operator that is argument-insensitive.

    :param name: name of module.

    """
    def __init__(self, name: str = '') -> None: ...
    def forward(self, input) -> QTensor: ...

class Torch_Linear(Module):
    '''
    Linear module (fully-connected layer) like torch.
    :math:`y = xA^T + b`

    :param input_channels: `int` - number of inputs features
    :param output_channels: `int` - number of output features
    :param weight_initializer: `callable` - defaults to normal
    :param bias_initializer: `callable` - defaults to zeros
    :param use_bias: `bool` - defaults to True
    :param device: default: None,use cpu. if use GPU,set DEV_GPU_0.
    :param dtype: default: None,use default data type.
    :param name: name of module,default:"".
    :return: a Linear class

    Example::

        from pyvqnet.nn import Torch_Linear
        from pyvqnet.utils import initializer
        from pyvqnet import QTensor
        import numpy as np
        c1 =2
        c2 = 3
        cin = 7
        cout = 5
        n = Torch_Linear(cin,cout,initializer.ones,initializer.ones)
        input = QTensor(np.arange(1.0,c1*c2*cin+1,dtype=np.float32).reshape((c1,c2,cin)),requires_grad=True)
        y = n.forward(input)

    '''
    backend: Incomplete
    use_bias: Incomplete
    output_channels: Incomplete
    input_channels: Incomplete
    weight: Incomplete
    bias: Incomplete
    def __init__(self, input_channels: int, output_channels: int, weight_initializer: Callable | None = None, bias_initializer: Callable | None = None, use_bias: bool = True, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x) -> QTensor: ...

class Linear(Module):
    '''
    Linear module (fully-connected layer).
    :math:`y = x@A.T + b`

    :param input_channels: `int` - number of inputs features
    :param output_channels: `int` - number of output features
    :param weight_initializer: `callable` - defaults to normal
    :param bias_initializer: `callable` - defaults to zeros
    :param use_bias: `bool` - defaults to True
    :param device: default: None,use cpu. if use GPU,set DEV_GPU_0.
    :param dtype: default: None,use default data type.
    :param name: name of module,default:"".
    :return: a Linear class

    Example::

        from pyvqnet.nn import Linear
        from pyvqnet.utils import initializer
        from pyvqnet import QTensor
        import numpy as np
        c1 =2
        c2 = 3
        cin = 7
        cout = 5
        n = Linear(cin,cout,initializer.ones,initializer.ones)
        input = QTensor(np.arange(1.0,c1*c2*cin+1,dtype=np.float32).reshape((c1,c2,cin)),requires_grad=True)
        y = n.forward(input)

    '''
    backend: Incomplete
    use_bias: Incomplete
    output_channels: Incomplete
    input_channels: Incomplete
    weights: Incomplete
    bias: Incomplete
    def __init__(self, input_channels: int, output_channels: int, weight_initializer: Callable | None = None, bias_initializer: Callable | None = None, use_bias: bool = True, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x) -> QTensor: ...
