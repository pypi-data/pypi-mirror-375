from .functional import dropout as dropout
from _typeshed import Incomplete
from pyvqnet.nn.module import Module as Module
from pyvqnet.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, tensor as tensor

class Dropout(Module):
    '''
    Dropout module.

    :param dropout_rate: `float` - probability that a neuron will be set to zero
    :param name: module name ,default="".
    :return: a Dropout class

    Example::

        b = 2
        ic = 3
        from pyvqnet._core import Tensor as CoreTensor
        from pyvqnet.nn.dropout import Dropout
        x = QTensor(CoreTensor.range(-1*ic*5*5,(b-1)*ic*5*5-1).reshape([b,ic,5,5]),
        requires_grad=True)
        droplayer = Dropout(0.5)
        droplayer.train()
        y = droplayer(x)
        y.backward(QTensor(np.ones(y.shape)*2))
        droplayer.eval()
        y = droplayer(x)


    '''
    dropout_rate: Incomplete
    def __init__(self, dropout_rate: float = 0.5, name: str = '') -> None: ...
    def forward(self, x) -> QTensor: ...

def drop_path(x: tensor.QTensor, drop_prob: float = 0.0, training: bool = False) -> tensor.QTensor: ...

class DropPath(Module):
    dropout_rate: Incomplete
    def __init__(self, dropout_rate: float = 0.5, name: str = '') -> None:
        """Drop paths (Stochastic Depth) per sample (when applied in main path of
            residual blocks).
            We follow the implementation
                https://github.com/rwightman/pytorch-image-models/blob/a2727c1bf78ba0d7b5727f5f95e37fb7f8866b1f/timm/models/layers/drop.py  # noqa: E501
                
            :param dropout_rate: dropout probability, default:0.5.
            :param name: name of module.

            :return:
                DropPath Module.
            
            Examples::

                import pyvqnet.nn as nn
                import pyvqnet.tensor as tensor

                x = tensor.randu([4])
                y = nn.DropPath()(x)
                
        """
    def forward(self, x, *args, **kwargs): ...
