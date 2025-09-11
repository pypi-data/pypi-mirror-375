from _typeshed import Incomplete
from pyvqnet.nn.module import Module as Module, Parameter as Parameter
from pyvqnet.qnn.vqc import PauliZ as PauliZ, QMachine as QMachine, cnot as cnot, rx as rx, ry as ry, rz as rz
from pyvqnet.qnn.vqc.qmeasure import expval as expval
from pyvqnet.tensor import tensor as tensor
from pyvqnet.utils.initializer import quantum_uniform as quantum_uniform

def angle_circuit(qmachine, features, num_qubits, rotation: str = 'X') -> None: ...
def weight_circuit(qmachine, weights, num_qubit, rotation: Incomplete | None = None) -> None: ...

class CirCuit_QRNN(Module):
    qm: Incomplete
    weights: Incomplete
    m_qubits: Incomplete
    def __init__(self, para_num, m_qubits) -> None: ...
    def forward(self, x): ...
    def __call__(self, x): ...
