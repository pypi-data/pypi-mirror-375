from _typeshed import Incomplete
from pyvqnet.nn.module import Module as Module, Parameter as Parameter
from pyvqnet.tensor.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor
from pyvqnet.utils.initializer import zeros as zeros

CoreTensor: Incomplete

class PQCLayer(Module):
    '''
    parameterized quantum circuit Layer.It contains paramters can be trained.

    Example::
        from pyvqnet.qnn.pqc import PQCLayer
        import pyvqnet.tensor as tensor
        import numpy as np
        pqlayer = PQCLayer(machine="cpu", quantum_number=4, rep=3, measure_qubits="Z0 Z1")

        x = tensor.QTensor(np.random.rand(1, 8))

        output = pqlayer(x)

        print("Output:", output)

    '''
    machine: Incomplete
    qlist: Incomplete
    history_expectation: Incomplete
    weights: Incomplete
    measure_qubits: Incomplete
    def __init__(self, machine: str = 'cpu', quantum_number: int = 4, rep: int = 3, measure_qubits: str = 'Z0 Z1') -> None:
        """
        machine: 'str' - compute machine
        quantum_number: 'int' - should tensor's gradient be tracked, defaults to False
        rep: 'int' - Ansatz circuits repeat block times
        measure_qubits: 'str' - measure qubits
        """
    def forward(self, x):
        """
            forward function
        """

def cnot_rz_rep_cir(qubits, param, rep: int = 3):
    """
    cnot_rz_rep_cir
    """
def paramterized_quautum_circuits(input: CoreTensor, param: CoreTensor, qubits, rep: int):
    """
    use qpanda to define circuit

    """
def Hamiltonian(input: str):
    '''
        Interchange two axes of an array.

        :param input: expect measure qubits.
        :return: hamiltion operator

        Examples::
        Hamiltonian("Z0 Z1" )
    '''
