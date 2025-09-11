from _typeshed import Incomplete
from collections import OrderedDict as OrderedDict
from pyvqnet.qnn import ComplexEntangelingTemplate as ComplexEntangelingTemplate, QuantumLayerV2 as QuantumLayerV2, expval as expval
from pyvqnet.tensor import QTensor as QTensor

class HardwareEfficientAnsatz:
    '''
    A implementation of Hardware Efficient Ansatz introduced by thesis: Hardware-efficient Variational Quantum Eigensolver for Small Molecules and
    Quantum Magnets https://arxiv.org/pdf/1704.05018.pdf.

    :param n_qubits: Number of qubits.
    :param single_rot_gate_list: A single qubit rotation gate list is constructed by one or several rotation gate that act on every qubit.Currently
    support Rx, Ry, Rz.
    :param qubits: Qubits allocated by pyqpanda api.
    :param entangle_gate: The non parameterized entanglement gate.CNOT,CZ is supported.default:CNOT.
    :param entangle_rules: How entanglement gate is used in the circuit. \'linear\' means the entanglement gate will be act on every neighboring qubits. \'all\' means
            the entanglment gate will be act on any two qbuits. Default:linear.
    :param depth: The depth of ansatz, default:1.

    Example::

        import pyqpanda as pq
        from pyvqnet.tensor import QTensor,tensor
        from pyvqnet.qnn import HardwareEfficientAnsatz
        machine = pq.CPUQVM()
        machine.init_qvm()
        qlist = machine.qAlloc_many(4)
        c = HardwareEfficientAnsatz(4, ["rx", "RY", "rz"],
                                    qlist,
                                    entangle_gate="cnot",
                                    entangle_rules="linear",
                                    depth=1)
        w = tensor.ones([c.get_para_num()])

        cir = c.create_ansatz(w)
        print(cir)
        #           ┌────────────┐ ┌────────────┐ ┌────────────┐        ┌────────────┐ ┌────────────┐ ┌────────────┐
        # q_0:  |0>─┤RX(1.000000)├ ┤RY(1.000000)├ ┤RZ(1.000000)├ ───■── ┤RX(1.000000)├ ┤RY(1.000000)├ ┤RZ(1.000000)├ ────────────── ────────────── 
        #           ├────────────┤ ├────────────┤ ├────────────┤ ┌──┴─┐ └────────────┘ ├────────────┤ ├────────────┤ ┌────────────┐
        # q_1:  |0>─┤RX(1.000000)├ ┤RY(1.000000)├ ┤RZ(1.000000)├ ┤CNOT├ ───■────────── ┤RX(1.000000)├ ┤RY(1.000000)├ ┤RZ(1.000000)├ ──────────────     
        #           ├────────────┤ ├────────────┤ ├────────────┤ └────┘ ┌──┴─┐         └────────────┘ ├────────────┤ ├────────────┤ ┌────────────┐     
        # q_2:  |0>─┤RX(1.000000)├ ┤RY(1.000000)├ ┤RZ(1.000000)├ ────── ┤CNOT├──────── ───■────────── ┤RX(1.000000)├ ┤RY(1.000000)├ ┤RZ(1.000000)├     
        #           ├────────────┤ ├────────────┤ ├────────────┤        └────┘         ┌──┴─┐         ├────────────┤ ├────────────┤ ├────────────┤     
        # q_3:  |0>─┤RX(1.000000)├ ┤RY(1.000000)├ ┤RZ(1.000000)├ ────── ────────────── ┤CNOT├──────── ┤RX(1.000000)├ ┤RY(1.000000)├ ┤RZ(1.000000)├     
        #           └────────────┘ └────────────┘ └────────────┘                       └────┘         └────────────┘ └────────────┘ └────────────┘     


    '''
    n_qubits: Incomplete
    def __init__(self, n_qubits, single_rot_gate_list, qubits, entangle_gate: str = 'CNOT', entangle_rules: str = 'linear', depth: int = 1) -> None: ...
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
