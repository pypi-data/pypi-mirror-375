from _typeshed import Incomplete

__all__ = ['AmplitudeEmbeddingCircuit', 'AngleEmbeddingCircuit', 'RotCircuit', 'CRotCircuit', 'IQPEmbeddingCircuits', 'BasicEmbeddingCircuit', 'CSWAPcircuit', 'StronglyEntanglingTemplate', 'ComplexEntangelingTemplate', 'BasicEntanglerTemplate', 'CCZ', 'Controlled_Hadamard', 'FermionicSingleExcitation', 'BasisState', 'UCCSD', 'QuantumPoolingCircuit', 'FermionicSimulationGate']

def FermionicSimulationGate(qlist_1, qlist_2, theta, phi):
    """

    Fermionic SimulationG ate represent fermionic simulation gate.

    The matrix is:

    .. math::

        {\rm FSim}(\theta, \\phi) =
        \x08egin{pmatrix}
            1 & 0 & 0 & 0\\\n            0 & \\cos(\theta) & -i\\sin(\theta) & 0\\\n            0 & -i\\sin(\theta) & \\cos(\theta) & 0\\\n            0 & 0 & 0 & e^{i\\phi}\\\n        \\end{pmatrix}

    :param qlist_1: first qubit index.
    :param qlist_2: second qubit index.
    :param theta: First parameter for gate.
    :param phi: Second parameter for gate.
    :return:
            <pyqpanda3.core.QCircuit

    Examples::
       
        from pyvqnet.qnn.pq3.template import FermionicSimulationGate

        c = FermionicSimulationGate(0,1,0.2,0.5)
        print(c)


    """
def CSWAPcircuit(qlists):
    """
    The controlled-swap circuit

    .. math:: CSWAP = \\begin{bmatrix}
            1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\\\\n            0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\\\\n            0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\\\\n            0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\\\\n            0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\\\\n            0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \\\\\n            0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\\\\n            0 & 0 & 0 & 0 & 0 & 0 & 0 & 1
        \\end{bmatrix}.

    .. note:: The first qubits provided corresponds to the **control qubit**.

    :param qlists: list of qubits index, the
    first qubits is control qubit.Length of qlists have to be 3.
    :return:
            <pyqpanda3.core.QCircuit

    Example::

        from pyvqnet.qnn.pq3 import CSWAPcircuit
        import pyqpanda3.core as pq
        m_machine = pq.CPUQVM()

        m_qlist = range(3)

        c =CSWAPcircuit([m_qlist[1],m_qlist[2],m_qlist[0]])
        print(c)
        # q_0:  |0>─X─ 
        #           │  
        # q_1:  |0>─*─ 
        #           │  
        # q_2:  |0>─X─ 
                    
        #  c :   / ═
 

    """
def IQPEmbeddingCircuits(input_feat, qlist, rep: int = 1):
    """

    Encodes :math:`n` features into :math:`n` qubits using diagonal gates of an IQP circuit.

    The embedding was proposed by `Havlicek et al. (2018) <https://arxiv.org/pdf/1804.11326.pdf>`_.

    The basic IQP circuit can be repeated by specifying ``n_repeats``.

    :param input_feat: numpy array which represents paramters
    :param qlist: qubits index
    :param rep: repeat circuits block
    :return: quantum circuits

    Example::

        
        import numpy as np
        from pyvqnet.qnn.pq3.template import IQPEmbeddingCircuits
        input_feat = np.arange(1,100)
        qlist = range(3)
        circuit = IQPEmbeddingCircuits(input_feat,qlist,rep = 3)
        print(circuit)

    """
def QuantumPoolingCircuit(sources_wires, sinks_wires, params, qubits):
    """
        A quantum circuit to down samples the data.
        To ‘artificially’ reduce the number of qubits in our circuit, we first begin by creating pairs of the qubits in our system.
        After initially pairing all the qubits, we apply our generalized 2 qubit unitary to each pair.
        After applying this two qubit unitary, we then ignore one qubit from each pair of qubits for the remainder of the neural network.

        :param sources_wires: source qubits index which will be ignored.
        :param sinks_wires: target qubits index which will be reserverd.
        :param params: input parameters.
        :param qubits: qubits list index.

        :return:
            the quantum pooling circuit
    Exmaple::

        from pyvqnet.qnn.pq3.template import QuantumPoolingCircuit
        import pyqpanda3.core as pq
        from pyvqnet import tensor

        qlists = range(4)
        p = tensor.full([6], 0.35)
        cir = QuantumPoolingCircuit([0, 1], [2, 3], p, qlists)
        print(cir)

    """
def AngleEmbeddingCircuit(input_feat, qlist, rotation: str = 'X'):
    """

    Encodes :math:`N` features into the rotation angles of :math:`n` qubits, where :math:`N \\leq n`.

    The rotations can be chosen as either : 'X' , 'Y' , 'Z',
    as defined by the ``rotation`` parameter:

    * ``rotation='X'`` uses the features as angles of RX rotations

    * ``rotation='Y'`` uses the features as angles of RY rotations

    * ``rotation='Z'`` uses the features as angles of RZ rotations

    The length of ``features`` has to be smaller or equal to the number of qubits.
    If there are fewer entries in ``features`` than qlists, the circuit does
    not apply the remaining rotation gates.

    :param input_feat: numpy array which represents paramters
    :param qlist: qubits index
    :return: quantum circuits

    Example::

        from pyvqnet.qnn.pq3.template import AngleEmbeddingCircuit
        import pyqpanda3.core as pq
        from pyvqnet import tensor
        
        m_qlist = range(2)

        input_feat = np.array([2.2, 1])
        C = AngleEmbeddingCircuit(input_feat,m_qlist,'X')
        print(C)
        C = AngleEmbeddingCircuit(input_feat,m_qlist,'Y')
        print(C)
        C = AngleEmbeddingCircuit(input_feat,m_qlist,'Z')
        print(C)
 
    """
def RotCircuit(para, qlist: int):
    """

    Arbitrary single qubit rotation.Number of qlist should be 1,and number of parameters should
    be 3

    .. math::

        R(\\phi,\\theta,\\omega) = RZ(\\omega)RY(\\theta)RZ(\\phi)= \\begin{bmatrix}
        e^{-i(\\phi+\\omega)/2}\\cos(\\theta/2) & -e^{i(\\phi-\\omega)/2}\\sin(\\theta/2) \\\\\n        e^{-i(\\phi-\\omega)/2}\\sin(\\theta/2) & e^{i(\\phi+\\omega)/2}\\cos(\\theta/2)
        \\end{bmatrix}.


    :param para: numpy array which represents paramters [\\phi, \\theta, \\omega]
    :param qlist: qubits index
    :return: quantum circuits

    Example::

        from pyvqnet.qnn.pq3.template import RotCircuit
        import pyqpanda3.core as pq
        from pyvqnet import tensor

        m_qlist = 1

        param =tensor.QTensor([3,4,5])
        c = RotCircuit(param,m_qlist)
        print(c)
 

    """
def BasicEmbeddingCircuit(input_feat, qlist):
    """

    For example, for ``features=([0, 1, 1])``, the quantum system will be
    prepared in state :math:`|011 \\rangle`.

    :param input_feat: binary input of shape ``(n, )``
    :param qlist: qlist that the template acts on
    :return: quantum circuits

    Example::

        from pyvqnet.qnn.pq3.template import BasicEmbeddingCircuit
        import pyqpanda3.core as pq
        from pyvqnet import tensor
        input_feat = tensor.QTensor([1,1,0])
        
        qlist = range(3)
        circuit = BasicEmbeddingCircuit(input_feat,qlist)
        print(circuit)

    """
def CRotCircuit(para, control_qlists, rot_qlists):
    """

    The controlled-Rot operator

    .. math:: CR(\\phi, \\theta, \\omega) = \\begin{bmatrix}
            1 & 0 & 0 & 0 \\\\\n            0 & 1 & 0 & 0\\\\\n            0 & 0 & e^{-i(\\phi+\\omega)/2}\\cos(\\theta/2) & -e^{i(\\phi-\\omega)/2}\\sin(\\theta/2)\\\\\n            0 & 0 & e^{-i(\\phi-\\omega)/2}\\sin(\\theta/2) & e^{i(\\phi+\\omega)/2}\\cos(\\theta/2)
        \\end{bmatrix}.

    :param para: numpy array which represents paramters [\\phi, \\theta, \\omega]
    :param control_qlists: control qubit index
    :param rot_qlists: Rot qubit index
    :return: quantum circuits

    Example::

        from pyvqnet.qnn.pq3.template import CRotCircuit
        import pyqpanda3.core as pq
        import numpy as np
        m_qlist = range(1)
        control_qlist = [1]
        param = np.array([3,4,5])
        cir = CRotCircuit(param,control_qlist,m_qlist)

        print(cir)

    """

class ComplexEntangelingTemplate:
    """
        Strongly entangled layers consisting of U3 gates and CNOT gates.
        This ansatz is from the following paper: https://arxiv.org/abs/1804.00633.

        :param weights: parameters, shape of [depth,num_qubits,3]
        :param num_qubits: number of qubits.
        :param depth: depth of sub-circuit.
        
        Example::

            from pyvqnet.qnn.pq3 import ComplexEntangelingTemplate
            import pyqpanda3.core as pq
            from pyvqnet.tensor import *
            depth =3
            num_qubits = 8
            shape = [depth, num_qubits, 3]
            weights = tensor.randn(shape)

            machine = pq.CPUQVM()

            qubits = range(num_qubits)

            circuit = ComplexEntangelingTemplate(weights, num_qubits=num_qubits,depth=depth)
            result = circuit.create_circuit(qubits)
            circuit.print_circuit(qubits)

            #           ┌──────────────────────────────────────┐                                                                                                     >
            # q_0:  |0>─┤U3(1.27039528, 1.15187562, 0.28685147)├─── ───*── ────── ───────────────────────────────────────── ──────────────────────────────────────── >
            #           ├──────────────────────────────────────┴─┐  ┌──┴─┐        ┌───────────────────────────────────────┐                                          >
            # q_1:  |0>─┤U3(-2.12268782, -0.27144274, 0.75200504)├─ ┤CNOT├ ───*── ┤U3(-0.83864456, 0.02301329, 1.67608392)├ ──────────────────────────────────────── >
            #           ├───────────────────────────────────────┬┘  └────┘ ┌──┴─┐ └───────────────────────────────────────┘ ┌──────────────────────────────────────┐ >
            # q_2:  |0>─┤U3(-0.58534127, 1.96181667, 0.74326313)├── ────── ┤CNOT├ ───*───────────────────────────────────── ┤U3(0.33437967, 0.87757057, 0.39915627)├ >
            #           ├───────────────────────────────────────┴─┐        └────┘ ┌──┴─┐                                    └──────────────────────────────────────┘ >
            # q_3:  |0>─┤U3(-1.13692939, -1.65865850, -0.18795860)├ ────── ────── ┤CNOT├─────────────────────────────────── ───*──────────────────────────────────── >
            #           ├────────────────────────────────────────┬┘               └────┘                                    ┌──┴─┐                                   >
            # q_4:  |0>─┤U3(1.82289147, -1.10953617, -0.35277700)├─ ────── ────── ───────────────────────────────────────── ┤CNOT├────────────────────────────────── >
            #           ├────────────────────────────────────────┤                                                          └────┘                                   >
            # q_5:  |0>─┤U3(-0.17311576, 1.74340403, -1.01236224)├─ ────── ────── ───────────────────────────────────────── ──────────────────────────────────────── >
            #           ├──────────────────────────────────────┬─┘                                                                                                   >
            # q_6:  |0>─┤U3(1.20991015, 0.98113006, 0.59199965)├─── ────── ────── ───────────────────────────────────────── ──────────────────────────────────────── >
            #           ├──────────────────────────────────────┴─┐                                                                                                   >
            # q_7:  |0>─┤U3(-0.22300248, -0.20013784, 1.18366325)├─ ────── ────── ───────────────────────────────────────── ──────────────────────────────────────── >
            #           └────────────────────────────────────────┘                                                                                                   >
            #  c :   / ═
                    

            #                                                                                                                                        >
            # q_0:  |0>────────────────────────────────────────── ──────────────────────────────────────── ───────────────────────────────────────── >
            #                                                                                                                                        >
            # q_1:  |0>────────────────────────────────────────── ──────────────────────────────────────── ───────────────────────────────────────── >
            #                                                                                                                                        >
            # q_2:  |0>────────────────────────────────────────── ──────────────────────────────────────── ───────────────────────────────────────── >
            #          ┌────────────────────────────────────────┐                                                                                    >
            # q_3:  |0>┤U3(1.66549909, -0.40679094, -0.46809316)├ ──────────────────────────────────────── ───────────────────────────────────────── >
            #          └────────────────────────────────────────┘ ┌──────────────────────────────────────┐                                           >
            # q_4:  |0>───*────────────────────────────────────── ┤U3(0.16954927, 0.46014482, 0.78943044)├ ───────────────────────────────────────── >
            #          ┌──┴─┐                                     └──────────────────────────────────────┘ ┌───────────────────────────────────────┐ >
            # q_5:  |0>┤CNOT├──────────────────────────────────── ───*──────────────────────────────────── ┤U3(0.05255963, 0.02863836, -0.06451511)├ >
            #          └────┘                                     ┌──┴─┐                                   └───────────────────────────────────────┘ >
            # q_6:  |0>────────────────────────────────────────── ┤CNOT├────────────────────────────────── ───*───────────────────────────────────── >
            #                                                     └────┘                                   ┌──┴─┐                                    >
            # q_7:  |0>────────────────────────────────────────── ──────────────────────────────────────── ┤CNOT├─────────────────────────────────── >
            #                                                                                              └────┘                                    >
            #  c :   / 
                    

            #          ┌────┐                                             ┌───────────────────────────────────────┐                                                          >
            # q_0:  |0>┤CNOT├ ─────────────────────────────────────────── ┤U3(0.82386994, 0.63560528, -2.15876579)├ ───*── ────── ────────────────────────────────────────── >
            #          └──┬─┘                                             └───────────────────────────────────────┘ ┌──┴─┐        ┌────────────────────────────────────────┐ >
            # q_1:  |0>───┼── ─────────────────────────────────────────── ───────────────────────────────────────── ┤CNOT├ ───*── ┤U3(-0.59525901, 0.26916015, -0.36771873)├ >
            #             │                                                                                         └────┘ ┌──┴─┐ └────────────────────────────────────────┘ >
            # q_2:  |0>───┼── ─────────────────────────────────────────── ───────────────────────────────────────── ────── ┤CNOT├ ───*────────────────────────────────────── >
            #             │                                                                                                └────┘ ┌──┴─┐                                     >
            # q_3:  |0>───┼── ─────────────────────────────────────────── ───────────────────────────────────────── ────── ────── ┤CNOT├──────────────────────────────────── >
            #             │                                                                                                       └────┘                                     >
            # q_4:  |0>───┼── ─────────────────────────────────────────── ───────────────────────────────────────── ────── ────── ────────────────────────────────────────── >
            #             │                                                                                                                                                  >
            # q_5:  |0>───┼── ─────────────────────────────────────────── ───────────────────────────────────────── ────── ────── ────────────────────────────────────────── >
            #             │   ┌─────────────────────────────────────────┐                                                                                                    >
            # q_6:  |0>───┼── ┤U3(-1.02229035, -0.84974003, -0.09020582)├ ───────────────────────────────────────── ────── ────── ────────────────────────────────────────── >
            #             │   └─────────────────────────────────────────┘ ┌───────────────────────────────────────┐                                                          >
            # q_7:  |0>───*── ─────────────────────────────────────────── ┤U3(0.61632144, -1.16613913, 2.19624877)├ ────── ────── ────────────────────────────────────────── >
            #                                                             └───────────────────────────────────────┘                                                          >
            #  c :   / 
                    

            #                                                                                                                                        >
            # q_0:  |0>────────────────────────────────────────── ──────────────────────────────────────── ───────────────────────────────────────── >
            #                                                                                                                                        >
            # q_1:  |0>────────────────────────────────────────── ──────────────────────────────────────── ───────────────────────────────────────── >
            #          ┌────────────────────────────────────────┐                                                                                    >
            # q_2:  |0>┤U3(0.00240794, -0.25518408, -0.06359871)├ ──────────────────────────────────────── ───────────────────────────────────────── >
            #          └────────────────────────────────────────┘ ┌──────────────────────────────────────┐                                           >
            # q_3:  |0>───*────────────────────────────────────── ┤U3(1.08181977, 1.61849511, 0.50123793)├ ───────────────────────────────────────── >
            #          ┌──┴─┐                                     └──────────────────────────────────────┘ ┌───────────────────────────────────────┐ >
            # q_4:  |0>┤CNOT├──────────────────────────────────── ───*──────────────────────────────────── ┤U3(-1.16502428, 0.62407655, 0.59613824)├ >
            #          └────┘                                     ┌──┴─┐                                   └───────────────────────────────────────┘ >
            # q_5:  |0>────────────────────────────────────────── ┤CNOT├────────────────────────────────── ───*───────────────────────────────────── >
            #                                                     └────┘                                   ┌──┴─┐                                    >
            # q_6:  |0>────────────────────────────────────────── ──────────────────────────────────────── ┤CNOT├─────────────────────────────────── >
            #                                                                                              └────┘                                    >
            # q_7:  |0>────────────────────────────────────────── ──────────────────────────────────────── ───────────────────────────────────────── >
            #                                                                                                                                        >
            #  c :   / 
                    

            #                                                     ┌────┐                                             ┌────────────────────────────────────────┐  >
            # q_0:  |0>────────────────────────────────────────── ┤CNOT├ ─────────────────────────────────────────── ┤U3(0.12422837, -0.41322461, -1.13118017)├─ >
            #                                                     └──┬─┘                                             └────────────────────────────────────────┘  >
            # q_1:  |0>────────────────────────────────────────── ───┼── ─────────────────────────────────────────── ─────────────────────────────────────────── >
            #                                                        │                                                                                           >
            # q_2:  |0>────────────────────────────────────────── ───┼── ─────────────────────────────────────────── ─────────────────────────────────────────── >
            #                                                        │                                                                                           >
            # q_3:  |0>────────────────────────────────────────── ───┼── ─────────────────────────────────────────── ─────────────────────────────────────────── >
            #                                                        │                                                                                           >
            # q_4:  |0>────────────────────────────────────────── ───┼── ─────────────────────────────────────────── ─────────────────────────────────────────── >
            #          ┌────────────────────────────────────────┐    │                                                                                           >
            # q_5:  |0>┤U3(-0.18666784, -0.86305261, 0.11458389)├ ───┼── ─────────────────────────────────────────── ─────────────────────────────────────────── >
            #          └────────────────────────────────────────┘    │   ┌─────────────────────────────────────────┐                                             >
            # q_6:  |0>───*────────────────────────────────────── ───┼── ┤U3(-0.07135861, -1.39787292, -2.28447723)├ ─────────────────────────────────────────── >
            #          ┌──┴─┐                                        │   └─────────────────────────────────────────┘ ┌─────────────────────────────────────────┐ >
            # q_7:  |0>┤CNOT├──────────────────────────────────── ───*── ─────────────────────────────────────────── ┤U3(-0.45126161, -0.46080309, -0.81497729)├ >
            #          └────┘                                                                                        └─────────────────────────────────────────┘ >
            #  c :   / 
                    

            #                                                           ┌────┐ 
            # q_0:  |0>───*── ────── ────── ────── ────── ────── ────── ┤CNOT├ 
            #          ┌──┴─┐                                           └──┬─┘ 
            # q_1:  |0>┤CNOT├ ───*── ────── ────── ────── ────── ────── ───┼── 
            #          └────┘ ┌──┴─┐                                       │   
            # q_2:  |0>────── ┤CNOT├ ───*── ────── ────── ────── ────── ───┼── 
            #                 └────┘ ┌──┴─┐                                │   
            # q_3:  |0>────── ────── ┤CNOT├ ───*── ────── ────── ────── ───┼── 
            #                        └────┘ ┌──┴─┐                         │   
            # q_4:  |0>────── ────── ────── ┤CNOT├ ───*── ────── ────── ───┼── 
            #                               └────┘ ┌──┴─┐                  │   
            # q_5:  |0>────── ────── ────── ────── ┤CNOT├ ───*── ────── ───┼── 
            #                                      └────┘ ┌──┴─┐           │   
            # q_6:  |0>────── ────── ────── ────── ────── ┤CNOT├ ───*── ───┼── 
            #                                             └────┘ ┌──┴─┐    │   
            # q_7:  |0>────── ────── ────── ────── ────── ────── ┤CNOT├ ───*── 
            #                                                    └────┘        
            #  c :   / 
         

    """
    weights: Incomplete
    num_qubits: Incomplete
    depth: Incomplete
    def __init__(self, weights, num_qubits, depth) -> None: ...
    def create_circuit(self, qubits): ...
    def compute_circuit(self): ...
    def print_circuit(self, qubits) -> None: ...

class StronglyEntanglingTemplate:
    """
    Layers consisting of single qubit rotations and entanglers, inspired by the `circuit-centric classifier design
     <https://arxiv.org/abs/1804.00633>`__ .

    The argument ``weights`` contains the weights for each layer. The number of layers :math:`L` is therefore derived
    from the first dimension of ``weights``.

    The 2-qubit CNOT gate,act on the :math:`M` number of qubits, :math:`i = 1,...,M`. The second qubit of each gate is given by
    :math:`(i+r)\\mod M`, where :math:`r` is a  hyperparameter called the *range*, and :math:`0 < r < M`.

    :param weights: weight tensor of shape ``(L, M, 3)`` , default: None, use random tensor with shape ``(1,1,3)`` .
    :param num_qubits: number of qubits, default: 1.
    :param ranges: sequence determining the range hyperparameter for each subsequent layer; default: None
                                using :math: `r=l \\mod M` for the :math:`l` th layer and :math:`M` qubits.
    :return: quantum circuits

    Example::

        from pyvqnet.qnn.pq3 import StronglyEntanglingTemplate
        import pyqpanda3.core as pq
        from pyvqnet.tensor import *
        import numpy as np
        np.random.seed(42)
        num_qubits = 3
        shape = [2, num_qubits, 3]
        weights = np.random.random(size=shape)

        machine = pq.CPUQVM()

        qubits = range(num_qubits)

        circuit = StronglyEntanglingTemplate(weights, num_qubits=num_qubits )
        result = circuit.compute_circuit()
        print(result)
        circuit.print_circuit(qubits)
        #           ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               ┌────┐                  ┌──────────────┐ ┌──────────────┐ >
        # q_0:  |0>─┤RZ(0.37454012)├ ┤RY(0.95071431)├ ┤RZ(0.73199394)├ ───*── ────── ┤CNOT├ ──────────────── ┤RZ(0.70807258)├ ┤RY(0.02058449)├ >
        #           ├──────────────┤ ├──────────────┤ ├──────────────┤ ┌──┴─┐        └──┬─┘ ┌──────────────┐ ├──────────────┤ ├──────────────┤ >
        # q_1:  |0>─┤RZ(0.59865848)├ ┤RY(0.15601864)├ ┤RZ(0.15599452)├ ┤CNOT├ ───*── ───┼── ┤RZ(0.83244264)├ ┤RY(0.21233911)├ ┤RZ(0.18182497)├ >
        #           ├──────────────┤ ├──────────────┤ ├──────────────┤ └────┘ ┌──┴─┐    │   └──────────────┘ ├──────────────┤ ├──────────────┤ >
        # q_2:  |0>─┤RZ(0.05808361)├ ┤RY(0.86617615)├ ┤RZ(0.60111501)├ ────── ┤CNOT├ ───*── ──────────────── ┤RZ(0.18340451)├ ┤RY(0.30424224)├ >
        #           └──────────────┘ └──────────────┘ └──────────────┘        └────┘                         └──────────────┘ └──────────────┘ >
        #  c :   / ═
                

        #          ┌──────────────┐        ┌────┐        
        # q_0:  |0>┤RZ(0.96990985)├ ───*── ┤CNOT├ ────── 
        #          └──────────────┘    │   └──┬─┘ ┌────┐ 
        # q_1:  |0>──────────────── ───┼── ───*── ┤CNOT├ 
        #          ┌──────────────┐ ┌──┴─┐        └──┬─┘ 
        # q_2:  |0>┤RZ(0.52475643)├ ┤CNOT├ ────── ───*── 
        #          └──────────────┘ └────┘               
        #  c :   / 
    """
    n_layers: Incomplete
    num_qubits: Incomplete
    weights: Incomplete
    ranges: Incomplete
    imprimitive: Incomplete
    def __init__(self, weights: Incomplete | None = None, num_qubits: int = 1, ranges: Incomplete | None = None) -> None: ...
    def Rot(self, qubits, l, weights):
        """
        :param qubits: quantum bits
        :param l: enter the number of layers
        :param weights: input weight
        :return: quantum circuit
        """
    def create_circuit(self, qubits): ...
    def compute_circuit(self): ...
    def print_circuit(self, qubits) -> None: ...

class BasicEntanglerTemplate:
    """
    Layers consisting of one-parameter single-qubit rotations on each qubit, followed by a closed chain or *ring* of
     CNOT gates.
     
    The ring of CNOT gates connects every qubit with its neighbour, with the last qubit being considered as a neighbour to the first qubit.

    The number of layers :math:`L` is determined by the first dimension of the argument ``weights``.
    When using a single wire, the template only applies the single
    qubit gates in each layer.


    :param weights: Weight tensor of shape ``(L, len(qubits))`` . Each weight is used as a parameter
                                for the rotation, default: None, use random tensor with shape ``(1,1)`` .
    :param num_qubits: number of qubits, default: 1.
    :param rotation: one-parameter single-qubit gate to use, default: `pyqpanda.RX`

    Example::

        import pyqpanda3.core as pq
        import numpy as np
        from pyvqnet.qnn.pq3 import BasicEntanglerTemplate
        np.random.seed(42)
        num_qubits = 5
        shape = [1, num_qubits]
        weights = np.random.random(size=shape)

        machine = pq.CPUQVM()
        
        qubits = range(num_qubits)

        circuit = BasicEntanglerTemplate(weights=weights, num_qubits=num_qubits, rotation=pq.RZ)
        result = circuit.compute_circuit()
        circuit.print_circuit(qubits)

        #           ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               ┌────┐                  ┌──────────────┐ ┌──────────────┐ >
        # q_0:  |0>─┤RZ(0.37454012)├ ┤RY(0.95071431)├ ┤RZ(0.73199394)├ ───*── ────── ┤CNOT├ ──────────────── ┤RZ(0.70807258)├ ┤RY(0.02058449)├ >
        #           ├──────────────┤ ├──────────────┤ ├──────────────┤ ┌──┴─┐        └──┬─┘ ┌──────────────┐ ├──────────────┤ ├──────────────┤ >
        # q_1:  |0>─┤RZ(0.59865848)├ ┤RY(0.15601864)├ ┤RZ(0.15599452)├ ┤CNOT├ ───*── ───┼── ┤RZ(0.83244264)├ ┤RY(0.21233911)├ ┤RZ(0.18182497)├ >
        #           ├──────────────┤ ├──────────────┤ ├──────────────┤ └────┘ ┌──┴─┐    │   └──────────────┘ ├──────────────┤ ├──────────────┤ >
        # q_2:  |0>─┤RZ(0.05808361)├ ┤RY(0.86617615)├ ┤RZ(0.60111501)├ ────── ┤CNOT├ ───*── ──────────────── ┤RZ(0.18340451)├ ┤RY(0.30424224)├ >
        #           └──────────────┘ └──────────────┘ └──────────────┘        └────┘                         └──────────────┘ └──────────────┘ >
        #  c :   / ═
                

        #          ┌──────────────┐        ┌────┐        
        # q_0:  |0>┤RZ(0.96990985)├ ───*── ┤CNOT├ ────── 
        #          └──────────────┘    │   └──┬─┘ ┌────┐ 
        # q_1:  |0>──────────────── ───┼── ───*── ┤CNOT├ 
        #          ┌──────────────┐ ┌──┴─┐        └──┬─┘ 
        # q_2:  |0>┤RZ(0.52475643)├ ┤CNOT├ ────── ───*── 
        #          └──────────────┘ └────┘               
        #  c :   / 
                



        #           ┌──────────────┐                             ┌────┐ 
        # q_0:  |0>─┤RZ(0.37454012)├ ───*── ────── ────── ────── ┤CNOT├ 
        #           ├──────────────┤ ┌──┴─┐                      └──┬─┘ 
        # q_1:  |0>─┤RZ(0.95071431)├ ┤CNOT├ ───*── ────── ────── ───┼── 
        #           ├──────────────┤ └────┘ ┌──┴─┐                  │   
        # q_2:  |0>─┤RZ(0.73199394)├ ────── ┤CNOT├ ───*── ────── ───┼── 
        #           ├──────────────┤        └────┘ ┌──┴─┐           │   
        # q_3:  |0>─┤RZ(0.59865848)├ ────── ────── ┤CNOT├ ───*── ───┼── 
        #           ├──────────────┤               └────┘ ┌──┴─┐    │   
        # q_4:  |0>─┤RZ(0.15601864)├ ────── ────── ────── ┤CNOT├ ───*── 
        #           └──────────────┘                      └────┘        
        #  c :   / ═

    """
    n_layers: Incomplete
    num_qubits: Incomplete
    weights: Incomplete
    rotation: Incomplete
    def __init__(self, weights: Incomplete | None = None, num_qubits: int = 1, rotation=...) -> None: ...
    def Rot(self, qubits, l, weights):
        """
        :param qubits: quantum bits
        :param l: enter the number of layers
        :param weights: input weight
        :return: quantum circuit
        """
    def create_circuit(self, qubits): ...
    def compute_circuit(self): ...
    def print_circuit(self, qubits) -> None: ...

class RandomTemplate:
    """
    Layers of randomly chosen single qubit rotations and 2-qubit entangling gates, acting on randomly chosen qubits.

    The argument ``weights`` contains the weights for each layer. The number of layers :math:`L` is therefore derived
    from the first dimension of ``weights``.

    The number of random rotations is derived from the second dimension of ``weights``. The number of
    two-qubit gates is determined by ``ratio_imprim``. For example, a ratio of ``0.3`` with ``30`` rotations
    will lead to the use of ``10`` two-qubit gates.

    :param weights: weight tensor of shape ``(L, k)``. Each weight is used as a parameter
                                for the rotation, default: None, use random tensor with shape ``(1,1)`` .
    :param num_qubits: number of qubits, default: 1.
    :param ratio_imprim: value between 0 and 1 that determines the ratio of imprimitive to rotation gates.
    :param rotation: List of Pauli-X, Pauli-Y and/or Pauli-Z gates. The frequency determines how often a particular
     rotation type is used. Defaults to the use of all three rotations with equal frequency.
    :param seed: seed to generate random architecture, defaults to 42.


    Example::

        import pyqpanda3.core as pq
        import numpy as np
        from pyvqnet.qnn.pq3 import RandomTemplate
        num_qubits = 2
        weights = np.array([[0.1, -2.1, 1.4]])

        machine = pq.CPUQVM()
        
        qubits = range(num_qubits)

        circuit = RandomTemplate(weights, num_qubits=num_qubits, seed=12)
        result = circuit.compute_circuit()
        circuit.print_circuit(qubits)
        # q_0:  |0>─┤CNOT├ ┤RZ(0.10000000)├─ ───*── ┤CNOT├ ──────────────── 
        #           └──┬─┘ ├──────────────┴┐ ┌──┴─┐ └──┬─┘ ┌──────────────┐ 
        # q_1:  |0>────*── ┤RX(-2.10000000)├ ┤CNOT├ ───*── ┤RZ(1.40000000)├ 
        #                  └───────────────┘ └────┘        └──────────────┘ 
        #  c :   / ═

    """
    seed: Incomplete
    rotations: Incomplete
    n_layers: Incomplete
    num_qubits: Incomplete
    weights: Incomplete
    ratio_imprimitive: Incomplete
    def __init__(self, weights: Incomplete | None = None, num_qubits: int = 1, ratio_imprim: float = 0.3, rotations: Incomplete | None = None, seed: int = 42) -> None: ...
    def select_random(self, n_samples, seed: Incomplete | None = None):
        """
        Returns a randomly sampled subset of Wires of length 'n_samples'.

        Args:
            n_samples (int): number of subsampled wires
            seed (int): optional random seed used for selecting the wires

        Returns:
            Wires: random subset of wires
        """
    def create_circuit(self, qubits): ...
    def compute_circuit(self): ...
    def print_circuit(self, qubits) -> None: ...

class SimplifiedTwoDesignTemplate:
    '''
    Layers consisting of a simplified 2-design architecture of Pauli-Y rotations and controlled-Z entanglers
    proposed in `Cerezo et al. (2020) <https://arxiv.org/abs/2001.00550>`_.

    A 2-design is an ensemble of unitaries whose statistical properties are the same as sampling random unitaries
    with respect to the Haar measure up to the first 2 moments.

    The template is not a strict 2-design, since
    it does not consist of universal 2-qubit gates as building blocks, but has been shown in
    `Cerezo et al. (2020) <https://arxiv.org/abs/2001.00550>`_ to exhibit important properties to study "barren plateaus"
    in quantum optimization landscapes.

    The template starts with an initial layer of single qubit Pauli-Y rotations, before the main
    :math:`L` layers are applied. The basic building block of the main layers are controlled-Z entanglers
    followed by a pair of Pauli-Y rotation gates (one for each wire).
    Each layer consists of an "even" part whose entanglers start with the first qubit,
    and an "odd" part that starts with the second qubit.

    The argument ``initial_layer_weights`` contains the rotation angles of the initial layer of Pauli-Y rotations,
    while ``weights`` contains the pairs of Pauli-Y rotation angles of the respective layers. Each layer takes
    :math:`\\lfloor M/2 \\rfloor + \\lfloor (M-1)/2 \\rfloor = M-1` pairs of angles, where :math:`M` is the number of wires.
    The number of layers :math:`L` is derived from the first dimension of ``weights``.

    :param initial_layer_weights: weight tensor for the initial rotation block, shape ``(M,)`` .
    :param weights: tensor of rotation angles for the layers, shape ``(L, M-1, 2)``.
    :param num_qubits: number of qubits, default: 1.


    Example::

        import pyqpanda3.core as pq
        import numpy as np
        from pyvqnet.qnn.pq3 import SimplifiedTwoDesignTemplate
        num_qubits = 3
        pi = np.pi
        init_weights = [pi, pi, pi]
        weights_layer1 = [[0., pi],
                            [0., pi]]
        weights_layer2 = [[pi, 0.],
                            [pi, 0.]]
        weights = [weights_layer1, weights_layer2]

        machine = pq.CPUQVM()

        qubits = range(num_qubits)

        circuit = SimplifiedTwoDesignTemplate(init_weights, weights, num_qubits=num_qubits)
        result = circuit.compute_circuit()
        circuit.print_circuit(qubits)

        #           ┌────┐ ┌──────────────┐         ┌────┐                  
        # q_0:  |0>─┤CNOT├ ┤RZ(0.10000000)├─ ───*── ┤CNOT├ ──────────────── 
        #           └──┬─┘ ├──────────────┴┐ ┌──┴─┐ └──┬─┘ ┌──────────────┐ 
        # q_1:  |0>────*── ┤RX(-2.10000000)├ ┤CNOT├ ───*── ┤RZ(1.40000000)├ 
        #                  └───────────────┘ └────┘        └──────────────┘ 
        #  c :   / ═
                



        #           ┌──────────────┐      ┌──────────────┐                            ┌──────────────┐                       
        # q_0:  |0>─┤RY(3.14159265)├ ──*─ ┤RY(0.00000000)├ ──── ──────────────── ──*─ ┤RY(3.14159265)├ ──── ──────────────── 
        #           ├──────────────┤ ┌─┴┐ ├──────────────┤      ┌──────────────┐ ┌─┴┐ ├──────────────┤      ┌──────────────┐ 
        # q_1:  |0>─┤RY(3.14159265)├ ┤CZ├ ┤RY(3.14159265)├ ──*─ ┤RY(0.00000000)├ ┤CZ├ ┤RY(0.00000000)├ ──*─ ┤RY(3.14159265)├ 
        #           ├──────────────┤ └──┘ └──────────────┘ ┌─┴┐ ├──────────────┤ └──┘ └──────────────┘ ┌─┴┐ ├──────────────┤ 
        # q_2:  |0>─┤RY(3.14159265)├ ──── ──────────────── ┤CZ├ ┤RY(3.14159265)├ ──── ──────────────── ┤CZ├ ┤RY(0.00000000)├ 
        #           └──────────────┘                       └──┘ └──────────────┘                       └──┘ └──────────────┘ 
        #  c :   / ═
          


    '''
    weights: Incomplete
    initial_layer_weights: Incomplete
    num_qubits: Incomplete
    wires: Incomplete
    n_layers: Incomplete
    def __init__(self, initial_layer_weights, weights, num_qubits: int = 1) -> None: ...
    def create_circuit(self, qubits): ...
    def compute_circuit(self): ...
    def print_circuit(self, qubits) -> None: ...

def Controlled_Hadamard(qubits):
    """
    The controlled-Hadamard gates

    .. math:: CH = \\begin{bmatrix}
            1 & 0 & 0 & 0 \\\\\n            0 & 1 & 0 & 0 \\\\\n            0 & 0 & \\frac{1}{\\sqrt{2}} & \\frac{1}{\\sqrt{2}} \\\\\n            0 & 0 & \\frac{1}{\\sqrt{2}} & -\\frac{1}{\\sqrt{2}}
        \\end{bmatrix}.

    :param qubits: qubits index.

    Examples::

        import pyqpanda3.core as pq

        machine = pq.CPUQVM()
        
        qubits =range(2)
        from pyvqnet.qnn.pq3 import Controlled_Hadamard

        cir = Controlled_Hadamard(qubits)
        print(cir)

                                                        
        # q_0:  |0>────────────────── ──*─ ──────────────── 
        #           ┌───────────────┐ ┌─┴┐ ┌──────────────┐ 
        # q_1:  |0>─┤RY(-0.78539816)├ ┤CZ├ ┤RY(0.78539816)├ 
        #           └───────────────┘ └──┘ └──────────────┘ 
        #  c :   / ═
          
    """
def CCZ(qubits):
    """
    CCZ (controlled-controlled-Z) gate.

    .. math::

        CCZ =
        \\begin{pmatrix}
        1 & 0 & 0 & 0 & 0 & 0 & 0 & 0\\\\\n        0 & 1 & 0 & 0 & 0 & 0 & 0 & 0\\\\\n        0 & 0 & 1 & 0 & 0 & 0 & 0 & 0\\\\\n        0 & 0 & 0 & 1 & 0 & 0 & 0 & 0\\\\\n        0 & 0 & 0 & 0 & 1 & 0 & 0 & 0\\\\\n        0 & 0 & 0 & 0 & 0 & 1 & 0 & 0\\\\\n        0 & 0 & 0 & 0 & 0 & 0 & 1 & 0\\\\\n        0 & 0 & 0 & 0 & 0 & 0 & 0 & -1
        \\end{pmatrix}
    
    :param qubits: qubits index。

    :return:
           pyqpanda3 QCircuit
    
    Examples::

        import pyqpanda3.core as pq

        machine = pq.CPUQVM()
        
        qubits = range(3)
        from pyvqnet.qnn.pq3 import CCZ

        cir = CCZ(qubits)
        print(cir)
        # q_0:  |0>─────── ─────── ───*── ─── ────── ─────── ───*── ───*── ┤T├──── ───*── 
        #                             │              ┌─┐        │   ┌──┴─┐ ├─┴───┐ ┌──┴─┐ 
        # q_1:  |0>────*── ─────── ───┼── ─── ───*── ┤T├──── ───┼── ┤CNOT├ ┤T.dag├ ┤CNOT├ 
        #           ┌──┴─┐ ┌─────┐ ┌──┴─┐ ┌─┐ ┌──┴─┐ ├─┴───┐ ┌──┴─┐ ├─┬──┘ ├─┬───┘ ├─┬──┘ 
        # q_2:  |0>─┤CNOT├ ┤T.dag├ ┤CNOT├ ┤T├ ┤CNOT├ ┤T.dag├ ┤CNOT├ ┤T├─── ┤H├──── ┤H├─── 
        #           └────┘ └─────┘ └────┘ └─┘ └────┘ └─────┘ └────┘ └─┘    └─┘     └─┘    
        #  c :   / ═

    """
def FermionicSingleExcitation(weight, wires, qubits):
    '''Circuit to exponentiate the tensor product of Pauli matrices representing the
    single-excitation operator entering the Unitary Coupled-Cluster Singles
    and Doubles (UCCSD) ansatz. UCCSD is a VQE ansatz commonly used to run quantum
    chemistry simulations.

    The Coupled-Cluster single-excitation operator is given by

    .. math::

        \\hat{U}_{pr}(\\theta) = \\mathrm{exp} \\{ \\theta_{pr} (\\hat{c}_p^\\dagger \\hat{c}_r
        -\\mathrm{H.c.}) \\},

    :param weight: input paramter acts on qubits p.
    :param wires: Wires that the template acts on. The wires represent the subset of orbitals in the interval [r, p]. Must be of minimum length 2. The first wire is interpreted as r and the last wire as p.
                Wires in between are acted on with CNOT gates to compute the parity of the set of qubits.
    :param qubits: qubits list index.

    :return:
           pyqpanda3 QCircuit

    Examples::

        from pyvqnet.qnn.pq3 import FermionicSingleExcitation, expval

        weight = 0.5
        import pyqpanda3.core as pq
        machine = pq.CPUQVM()

        qlists = range(3)

        cir = FermionicSingleExcitation(weight, [1, 0, 2], qlists)

        prog = pq.QProg()
        prog<<cir
        pauli_dict = {\'Z0\': 1}
        exp2 = expval(machine, prog, pauli_dict)
        print(f"vqnet {exp2}")

    '''
def BasisState(basis_state, wires, qubits):
    """
    Prepares a basis state on the given wires using a sequence of Pauli-X gates.

    :param wires:wires that the template acts on.
    :param qubits: qubits list index.

    :return:
         pyqpanda3 QCircuit
    """
def UCCSD(weights, wires, s_wires, d_wires, init_state, qubits):
    '''
    
    Implements the Unitary Coupled-Cluster Singles and Doubles (UCCSD) ansatz.

    The UCCSD ansatz calls the
     `FermionicSingleExcitation` and `FermionicDoubleExcitation`
    templates to exponentiate the coupled-cluster excitation operator. UCCSD is a VQE ansatz
    commonly used to run quantum chemistry simulations.

    The UCCSD unitary, within the first-order Trotter approximation, is given by:

    .. math::

        \\hat{U}(\\vec{\\theta}) =
        \\prod_{p > r} \\mathrm{exp} \\Big\\{\\theta_{pr}
        (\\hat{c}_p^\\dagger \\hat{c}_r-\\mathrm{H.c.}) \\Big\\}
        \\prod_{p > q > r > s} \\mathrm{exp} \\Big\\{\\theta_{pqrs}
        (\\hat{c}_p^\\dagger \\hat{c}_q^\\dagger \\hat{c}_r \\hat{c}_s-\\mathrm{H.c.}) \\Big\\}

    where :math:`\\hat{c}` and :math:`\\hat{c}^\\dagger` are the fermionic annihilation and
    creation operators and the indices :math:`r, s` and :math:`p, q` run over the occupied and
    unoccupied molecular orbitals, respectively. Using the `Jordan-Wigner transformation
    <https://arxiv.org/abs/1208.5986>`_ the UCCSD unitary defined above can be written in terms
    of Pauli matrices as follows (for more details see
    `arXiv:1805.04340 <https://arxiv.org/abs/1805.04340>`_):

    .. math::

        \\hat{U}(\\vec{\\theta}) = && \\prod_{p > r} \\mathrm{exp} \\Big\\{ \\frac{i\\theta_{pr}}{2}
        \\bigotimes_{a=r+1}^{p-1} \\hat{Z}_a (\\hat{Y}_r \\hat{X}_p - \\mathrm{H.c.}) \\Big\\} \\\\\n        && \\times \\prod_{p > q > r > s} \\mathrm{exp} \\Big\\{ \\frac{i\\theta_{pqrs}}{8}
        \\bigotimes_{b=s+1}^{r-1} \\hat{Z}_b \\bigotimes_{a=q+1}^{p-1}
        \\hat{Z}_a (\\hat{X}_s \\hat{X}_r \\hat{Y}_q \\hat{X}_p +
        \\hat{Y}_s \\hat{X}_r \\hat{Y}_q \\hat{Y}_p +
        \\hat{X}_s \\hat{Y}_r \\hat{Y}_q \\hat{Y}_p +
        \\hat{X}_s \\hat{X}_r \\hat{X}_q \\hat{Y}_p -
        \\{\\mathrm{H.c.}\\}) \\Big\\}.


    :param weights : Size ``(len(s_wires) + len(d_wires),)`` tensor containing the parameters
        :math:`\\theta_{pr}` and :math:`\\theta_{pqrs}` entering the Z rotation in
        `FermionicSingleExcitation` and `FermionicDoubleExcitation`.
    :param wires: wires that the template acts on
    :param s_wires: Sequence of lists containing the wires ``[r,...,p]``
        resulting from the single excitation
        :math:`\\vert r, p \\rangle = \\hat{c}_p^\\dagger \\hat{c}_r \\vert \\mathrm{HF} \\rangle`,
        where :math:`\\vert \\mathrm{HF} \\rangle` denotes the Hartee-Fock reference state.
    :param d_wires: Sequence of lists, each containing two lists that
        specify the indices ``[s, ...,r]`` and ``[q,..., p]`` defining the double excitation
        :math:`\\vert s, r, q, p \\rangle = \\hat{c}_p^\\dagger \\hat{c}_q^\\dagger \\hat{c}_r
        \\hat{c}_s \\vert \\mathrm{HF} \\rangle`.
    :param init_state: Length ``len(wires)`` occupation-number vector representing the
        HF state. ``init_state`` is used to initialize the wires.
    :param qubits: quantum qubits index.

    Examples::

        import pyqpanda3.core as pq
        from pyvqnet.tensor import tensor
        from pyvqnet.qnn.pq3 import UCCSD, expval
        machine = pq.CPUQVM()
        
        qlists = range(6)
        weight = tensor.zeros([8])
        cir = UCCSD(weight,wires = [0,1,2,3,4,5,6],
                                        s_wires=[[0, 1, 2], [0, 1, 2, 3, 4], [1, 2, 3], [1, 2, 3, 4, 5]],
                                        d_wires=[[[0, 1], [2, 3]], [[0, 1], [2, 3, 4, 5]], [[0, 1], [3, 4]], [[0, 1], [4, 5]]],
                                        init_state=[1, 1, 0, 0, 0, 0],
                                        qubits=qlists)

        prog = pq.QProg()
        prog<<cir
        pauli_dict = {\'Z0\': 1}
        exp2 = expval(machine, prog, pauli_dict)
        print(f"vqnet {exp2}")

    '''

class RandomTemplate:
    """
    Layers of randomly chosen single qubit rotations and 2-qubit entangling gates, acting on randomly chosen qubits.

    The argument ``weights`` contains the weights for each layer. The number of layers :math:`L` is therefore derived
    from the first dimension of ``weights``.

    The number of random rotations is derived from the second dimension of ``weights``. The number of
    two-qubit gates is determined by ``ratio_imprim``. For example, a ratio of ``0.3`` with ``30`` rotations
    will lead to the use of ``10`` two-qubit gates.

    :param weights: weight tensor of shape ``(L, k)``. Each weight is used as a parameter
                                for the rotation, default: None, use random tensor with shape ``(1,1)`` .
    :param num_qubits: number of qubits, default: 1.
    :param ratio_imprim: value between 0 and 1 that determines the ratio of imprimitive to rotation gates.
    :param rotation: List of Pauli-X, Pauli-Y and/or Pauli-Z gates. The frequency determines how often a particular
     rotation type is used. Defaults to the use of all three rotations with equal frequency.
    :param seed: seed to generate random architecture, defaults to 42.


    """
    seed: Incomplete
    rotations: Incomplete
    n_layers: Incomplete
    num_qubits: Incomplete
    weights: Incomplete
    ratio_imprimitive: Incomplete
    def __init__(self, weights: Incomplete | None = None, num_qubits: int = 1, ratio_imprim: float = 0.3, rotations: Incomplete | None = None, seed: int = 42) -> None: ...
    def select_random(self, n_samples, seed: Incomplete | None = None):
        """
        Returns a randomly sampled subset of Wires of length 'n_samples'.

        Args:
            n_samples (int): number of subsampled wires
            seed (int): optional random seed used for selecting the wires

        Returns:
            Wires: random subset of wires
        """
    def create_circuit(self, qubits): ...
    def compute_circuit(self): ...
    def print_circuit(self, qubits) -> None: ...

# Names in __all__ with no definition:
#   AmplitudeEmbeddingCircuit
