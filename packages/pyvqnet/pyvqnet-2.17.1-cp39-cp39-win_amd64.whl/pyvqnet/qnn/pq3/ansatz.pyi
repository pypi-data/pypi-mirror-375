from _typeshed import Incomplete
from collections import OrderedDict as OrderedDict
from pyvqnet.tensor import QTensor as QTensor

class HardwareEfficientAnsatz:
    '''
    A implementation of Hardware Efficient Ansatz introduced by thesis: Hardware-efficient Variational Quantum Eigensolver for Small Molecules and
    Quantum Magnets https://arxiv.org/pdf/1704.05018.pdf.

    :param qubits: Qubits index.
    :param single_rot_gate_list: A single qubit rotation gate list is constructed by one or several rotation gate that act on every qubit.Currently
    support Rx, Ry, Rz.
    :param entangle_gate: The non parameterized entanglement gate.CNOT,CZ is supported.default:CNOT.
    :param entangle_rules: How entanglement gate is used in the circuit. \'linear\' means the entanglement gate will be act on every neighboring qubits. \'all\' means
            the entanglment gate will be act on any two qbuits. Default:linear.
    :param depth: The depth of ansatz, default:1.

    Example::

        import pyqpanda3.core as pq
        from pyvqnet.tensor import QTensor,tensor
        from pyvqnet.qnn.pq3.ansatz import HardwareEfficientAnsatz
        machine = pq.CPUQVM()
        
        qlist = range(4)
        c = HardwareEfficientAnsatz(qlist,["rx", "RY", "rz"],
                                entangle_gate="cnot",
                                entangle_rules="linear",
                                depth=1)
        w = tensor.ones([c.get_para_num()])

        cir = c.create_ansatz(w)
        print(cir)
    '''
    n_qubits: Incomplete
    def __init__(self, qubits, single_rot_gate_list, entangle_gate: str = 'CNOT', entangle_rules: str = 'linear', depth: int = 1) -> None: ...
    def get_para_num(self):
        """
        Get parameter numbers need for this ansatz
        """
    def create_ansatz(self, weights):
        """
        create ansatz use weights in parameterized gates
        :param weights: varational parameters in the ansatz.
        :return: a pyqpanda  Hardware Efficient Ansatz instance .
    
        """
