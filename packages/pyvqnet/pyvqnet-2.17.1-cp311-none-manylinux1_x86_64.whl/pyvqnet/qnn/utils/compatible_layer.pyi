from _typeshed import Incomplete
from pyvqnet.nn.module import Module as Module
from pyvqnet.nn.parameter import Parameter as Parameter
from pyvqnet.tensor.tensor import QTensor as QTensor
from pyvqnet.utils.initializer import ones as ones, quantum_uniform as quantum_uniform

CoreTensor: Incomplete

class Compatiblelayer(Module):
    """
        An abstract wrapper to use other framework's quantum circuits(such as Qiskit
         `qiskit.QuantumCircuit`, TFQ `cirq.Circuit`) to forward and backward in the form of vqnet.
        Your should define the quantums circuits in the forward() and backward() functions.

        Note:
            `pyvqnet.utils.qikitlayer.QiskitLayer` is an implementation
             of using Qiskit's circuits to run in vqnet.

    """
    m_para: Incomplete
    para_num: Incomplete
    def __init__(self, circuits, para_num) -> None: ...
    def forward(self, x) -> None: ...
