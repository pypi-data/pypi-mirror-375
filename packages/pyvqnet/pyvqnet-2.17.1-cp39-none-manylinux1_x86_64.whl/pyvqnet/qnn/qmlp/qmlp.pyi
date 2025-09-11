from _typeshed import Incomplete
from pyvqnet.nn import Parameter as Parameter
from pyvqnet.nn.linear import Linear as Linear
from pyvqnet.nn.module import Module as Module
from pyvqnet.nn.pooling import AvgPool2D as AvgPool2D
from pyvqnet.qnn.vqc import MeasureAll as MeasureAll, QMachine as QMachine, QModule as QModule, crx as crx, rot as rot, rx as rx
from pyvqnet.types import _padding_type, _size_type
from typing import Callable

def vqc_rot_cir(qm, weights, qubits) -> None: ...
def vqc_crot_cir(qm, weights, qubits) -> None: ...

class build_qmlp_vqc(QModule):
    qm: Incomplete
    nq: Incomplete
    w: Incomplete
    ma: Incomplete
    def __init__(self, nq) -> None: ...
    def forward(self, x): ...

class QMLPModel(Module):
    '''
    QMLPModel is a quantum-inspired neural network that integrates quantum circuits with classical neural network operations such as pooling and fully connected layers.
    It is designed to process quantum data and extract relevant features through quantum operations and classical layers.

    Example::
        import numpy as np
        from pyvqnet.tensor import tensor
        from pyvqnet.qnn.qmlp.qmlp import QMLPModel
        from pyvqnet.dtype import *

        input_channels = 16
        output_channels = 10
        num_qubits = 4
        kernel = (2, 2)
        stride = (2, 2)
        padding = "valid"
        batch_size = 8

        model = QMLPModel(input_channels=num_qubits,
                          output_channels=output_channels,
                          num_qubits=num_qubits,
                          kernel=kernel,
                          stride=stride,
                          padding=padding)

        x = tensor.QTensor(np.random.randn(batch_size, input_channels, 32, 32),dtype=kfloat32)

        output = model(x)

        print("Output shape:", output.shape)


    '''
    ave_pool2d: Incomplete
    quantum_circuit: Incomplete
    linear: Incomplete
    def __init__(self, input_channels: int, output_channels: int, num_qubits: int, kernel: _size_type, stride: _size_type, padding: _padding_type = 'valid', weight_initializer: Callable | None = None, bias_initializer: Callable | None = None, use_bias: bool = True, dtype: int | None = None) -> None:
        '''

        :param input_channels: `int` - number of inputs features
        :param output_channels: `int` - number of output features
        :param num_qubits: `int` - number of qubits
        :param kernel: size of the average pooling windows
        :param stride: factors by which to downscale
        :param padding: one of  "valid" or "same"
        :param weight_initializer: `callable` - defaults to normal
        :param bias_initializer: `callable` - defaults to zeros
        :param use_bias: `bool` - defaults to True
        :param dtype: default: None,use default data type.
        '''
    def forward(self, x): ...
