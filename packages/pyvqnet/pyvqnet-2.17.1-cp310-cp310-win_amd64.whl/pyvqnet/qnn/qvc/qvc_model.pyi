from _typeshed import Incomplete
from pyvqnet.nn.module import Module as Module
from pyvqnet.nn.parameter import Parameter as Parameter
from pyvqnet.tensor import tensor as tensor
from pyvqnet.tensor.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor

CoreTensor: Incomplete

def qvc_circuits_with_noise(input, weights, qlist, clist, qvm):
    """
    add noisemodel
    """

class Qvc(Module):
    """
    QVC
    """
    weights: Incomplete
    delta: Incomplete
    machine: Incomplete
    n_qubits: Incomplete
    bias: Incomplete
    last: Incomplete
    def __init__(self, shape, q_delta: float = 0.01) -> None: ...
    def forward(self, x): ...

def get_cnot(nqubits): ...
def build_circult(weights: CoreTensor, xx, nqubits):
    """
    build_circult
    """
