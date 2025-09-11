from ...device import DEV_CPU as DEV_CPU
from ...tensor import QTensor as QTensor
from ...torch.initializer import he_uniform as he_uniform, zeros as zeros
from ..parameter import Parameter as Parameter
from .module import TorchModule as TorchModule
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock
from typing import Callable

class Linear(TorchModule):
    '''

    Linear module (fully connected layer), :math:`y = x@A.T + b`.

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.

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

        import numpy as np
        import pyvqnet
        from pyvqnet.tensor import QTensor
        from pyvqnet.nn.torch import Linear
        import pyvqnet.utils
        pyvqnet.backends.set_backend("torch")
        pyvqnet.utils.set_random_seed(42)
        c1 =2
        c2 = 3
        cin = 4
        cout = 2
        n = Linear(cin,cout)
        input = QTensor(np.arange(1,c1*c2*cin+1).reshape((c1,c2,cin)),requires_grad=True,dtype=pyvqnet.kfloat32)
        y = n.forward(input)
        print(y)
        print(n.parameters())

        # [[[ 3.1388626, 0.1697076],
        #   [ 7.696633 , 0.3359371],
        #   [12.254404 , 0.5021666]],

        #  [[16.812174 , 0.6683961],
        #   [21.369944 , 0.8346253],
        #   [25.927713 , 1.0008545]]]
        # <QTensor [2, 3, 2] DEV_CPU kfloat32>
        # [Parameter containing:
        # tensor([[ 0.3823,  0.4150, -0.1171,  0.4593],
        #         [-0.1096,  0.1009, -0.2434,  0.2936]], requires_grad=True), Parameter containing:
        # tensor([ 0.4408, -0.3668], requires_grad=True)]

    '''
    backend: Incomplete
    use_bias: Incomplete
    output_channels: Incomplete
    input_channels: Incomplete
    weight: Incomplete
    bias: Incomplete
    def __init__(self, input_channels: int, output_channels: int, weight_initializer: Callable | None = None, bias_initializer: Callable | None = None, use_bias: bool = True, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...
TorchLinear = Linear
