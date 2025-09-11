from _typeshed import Incomplete
from pyvqnet.nn.module import Module as Module
from pyvqnet.nn.parameter import Parameter as Parameter
from pyvqnet.tensor.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor

CoreTensor: Incomplete

class vmodel(Module):
    """
    vmodel
    """
    delta: Incomplete
    num_layers: Incomplete
    machine: Incomplete
    n_qubits: Incomplete
    params: Incomplete
    last: Incomplete
    def __init__(self, shape, num_layers: int = 3, q_delta: float = 0.0001) -> None: ...
    def forward(self, x): ...

def get_grad(g: CoreTensor, x: CoreTensor, params: CoreTensor, forward_circult, delta, machine, nqubits, last):
    """
    get_grad
    """
def qdrl_circuit(input, weights, qlist, clist, machine):
    """
    qdrl_circuit
    """
def build_circult(param, x, n_qubits):
    """
    build_circult
    """
