from matplotlib import animation as animation
from pyvqnet.nn import Module as Module, Parameter as Parameter
from pyvqnet.nn.loss import MeanSquaredError as MeanSquaredError
from pyvqnet.optim.adam import Adam as Adam
from pyvqnet.qnn.vqc import MeasureAll as MeasureAll, QMachine as QMachine, QModule as QModule, cnot as cnot, rx as rx, ry as ry, rz as rz, u3 as u3
from pyvqnet.tensor import QTensor as QTensor, kfloat32 as kfloat32, tensor as tensor

def layer_circuit(qm, qubits, weights) -> None: ...

CIRCUIT_SIZE: int

def encoder(encodings): ...
