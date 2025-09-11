from _typeshed import Incomplete
from pyvqnet import nn as nn
from pyvqnet.nn.module import Module as Module
from pyvqnet.tensor import tensor as tensor
from pyvqnet.utils.initializer import normal as normal, normal_ as normal_, xavier_uniform_ as xavier_uniform_

class TTOLayer(Module):
    '''
    Tensor Train Operator Layer for tensor decompositions in deep learning models.

    The TTOLayer decomposes input tensors using a tensor train (TT) format, enabling efficient representations
    of high-dimensional data. This layer allows learning tensor decompositions with rank constraints,
    reducing the computational complexity and memory usage compared to traditional fully connected layers.

    Example::
        from pyvqnet.tensor import tensor
        import numpy as np
        from pyvqnet.dtype import kfloat32
        inp_modes = [4, 5]
        out_modes = [4, 5]
        mat_ranks = [1, 3, 1]
        tto_layer = TTOLayer(inp_modes, out_modes, mat_ranks)

        batch_size = 2
        len = 4
        embed_size = 5
        inp = tensor.QTensor(np.random.randn(batch_size, len, embed_size), dtype=kfloat32)

        output = tto_layer(inp)

        print("Input shape:", inp.shape)
        print("Output shape:", output.shape)
    '''
    inp_modes: Incomplete
    out_modes: Incomplete
    mat_ranks: Incomplete
    dim: Incomplete
    mat_cores: Incomplete
    biases: Incomplete
    def __init__(self, inp_modes, out_modes, mat_ranks, biases_initializer=...) -> None:
        """
        Tensor Train Operator Layer for tensor decompositions in deep learning models.

        :param inp_modes: list of int
            A list representing the dimensions (modes) of the input tensor. Each element corresponds to the size of a specific mode in the input tensor.

        :param out_modes: list of int
            A list representing the dimensions (modes) of the output tensor. Each element corresponds to the size of a specific mode in the output tensor.

        :param mat_ranks: list of int
            A list representing the ranks of the tensor cores (factorization ranks) for the tensor decomposition. It defines the number of components used for each mode in the tensor train decomposition.

        :param biases_initializer: callable, optional (default=tensor.zeros)
            The initializer function for the biases. It defines how to initialize the biases in the layer.
        """
    def forward(self, inp): ...
