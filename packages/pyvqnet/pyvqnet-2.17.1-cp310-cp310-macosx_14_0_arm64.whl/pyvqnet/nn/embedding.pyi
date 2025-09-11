from ..device import DEV_CPU as DEV_CPU
from _typeshed import Incomplete
from pyvqnet.nn.module import Module as Module, Parameter as Parameter
from pyvqnet.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, tensor as tensor
from pyvqnet.utils.initializer import xavier_normal as xavier_normal
from typing import Callable

class Embedding(Module):
    '''
        This module is often used to store word embeddings and retrieve them using indices.
        The input to the module is a list of indices, and the output is the corresponding
        word embeddings.


        :param num_embeddings: `int` - number of inputs features
        :param embedding_dim: `int` - number of output features
        :param weight_initializer: `callable` - defaults to normal
        :param dtype: data type of parameters,default: None,use default data type.
        :param name: name of module,default:"".
        :return: a Embedding class

        Example::

            import numpy as np
            from pyvqnet.tensor import QTensor
            from pyvqnet.nn.embedding import Embedding
            import pyvqnet
            vlayer = Embedding(30,3)
            x = QTensor(np.arange(1,25).reshape([2,3,2,2]),dtype= pyvqnet.kint64)
            y = vlayer(x)
            print(y)

    '''
    backend: Incomplete
    weights: Incomplete
    def __init__(self, num_embeddings: int, embedding_dim: int, weight_initializer: Callable = ..., dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x) -> QTensor: ...
