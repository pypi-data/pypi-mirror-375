from ...device import DEV_CPU as DEV_CPU
from ...tensor import to_tensor as to_tensor
from ...utils.initializer import xavier_normal as xavier_normal
from ..parameter import Parameter as Parameter
from .module import TorchModule as TorchModule
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock
from typing import Callable

class Embedding(TorchModule):
    '''
    This module is often used to store word embeddings and retrieve them using indices.
    The input to the module is a list of indices, and the output is the corresponding
    word embeddings.

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.


    :param num_embeddings: `int` - number of inputs features
    :param embedding_dim: `int` - number of output features
    :param weight_initializer: `callable` - defaults to normal
    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a Embedding class
    '''
    backend: Incomplete
    weights: Incomplete
    def __init__(self, num_embeddings: int, embedding_dim: int, weight_initializer: Callable = ..., dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...
