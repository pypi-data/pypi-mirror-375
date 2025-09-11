from _typeshed import Incomplete
from itertools import combinations as combinations
from pyvqnet.tensor import QTensor as QTensor, randu as randu

def AmplitudeEmbeddingCircuit(input_feat, qlist):
    """

    Encodes :math:`2^n` features into the amplitude vector of :math:`n` qubits.
    To represent a valid quantum state vector, the L2-norm of ``features`` must be one.

    :param input_feat: numpy array which represents paramters
    :param qlist: qubits allocated by pyQpanda.qAlloc_many()
    :return: quantum circuits

    Example::

        input_feat = np.array([2.2, 1, 4.5, 3.7])
        m_machine = pq.init_quantum_machine(pq.QMachineType.CPU)
        m_qlist = m_machine.qAlloc_many(2)
        m_clist = m_machine.cAlloc_many(2)
        m_prog = pq.QProg()
        cir = AmplitudeEmbeddingCircuit(input_feat,m_qlist)
        pq.destroy_quantum_machine(m_machine)
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
    :param qlist: qubits allocated by pyQpanda.qAlloc_many()
    :return: quantum circuits

    Example::

        m_machine = pq.init_quantum_machine(pq.QMachineType.CPU)
        m_qlist = m_machine.qAlloc_many(2)
        m_clist = m_machine.cAlloc_many(2)
        m_prog = pq.QProg()

        input_feat = np.array([2.2, 1])
        C = AngleEmbeddingCircuit(input_feat,m_qlist,'X')
        print(C)
        C = AngleEmbeddingCircuit(input_feat,m_qlist,'Y')
        print(C)
        C = AngleEmbeddingCircuit(input_feat,m_qlist,'Z')
        print(C)
        pq.destroy_quantum_machine(m_machine)
    """
def RotCircuit(para, qlist):
    """

    Arbitrary single qubit rotation.Number of qlist should be 1,and number of parameters should
    be 3

    .. math::

        R(\\phi,\\theta,\\omega) = RZ(\\omega)RY(\\theta)RZ(\\phi)= \\begin{bmatrix}
        e^{-i(\\phi+\\omega)/2}\\cos(\\theta/2) & -e^{i(\\phi-\\omega)/2}\\sin(\\theta/2) \\\\\n        e^{-i(\\phi-\\omega)/2}\\sin(\\theta/2) & e^{i(\\phi+\\omega)/2}\\cos(\\theta/2)
        \\end{bmatrix}.


    :param para: numpy array which represents paramters [\\phi, \\theta, \\omega]
    :param qlist: qubits allocated by pyQpanda.qAlloc_many()
    :return: quantum circuits

    Example::

        m_machine = pq.init_quantum_machine(pq.QMachineType.CPU)
        m_clist = m_machine.cAlloc_many(2)
        m_prog = pq.QProg()
        m_qlist = m_machine.qAlloc_many(1)
        param = np.array([3,4,5])
        c = RotCircuit(param,m_qlist)
        print(c)
        pq.destroy_quantum_machine(m_machine)

    """

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

        import pyqpanda as pq
        import numpy as np
        from pyvqnet.qnn.template import StronglyEntanglingTemplate
        np.random.seed(42)
        num_qubits = 3
        shape = [2, num_qubits, 3]
        weights = np.random.random(size=shape)

        machine = pq.CPUQVM()
        machine.init_qvm()
        qubits = machine.qAlloc_many(num_qubits)

        circuit = StronglyEntanglingTemplate(weights, num_qubits=num_qubits)
        result = circuit.create_circuit(qubits)
        circuit.print_circuit(qubits)

        prob = machine.prob_run_dict(result, qubits[0], -1)
        prob = list(prob.values())
        print(prob)
        # q_0:  |0>─┤RZ(0.374540)├ ┤RY(0.950714)├ ┤RZ(0.731994)├ ───■── ────── ┤CNOT├──────────── ┤RZ(0.708073)├ >
        #           ├────────────┤ ├────────────┤ ├────────────┤ ┌──┴─┐        └──┬┬┴───────────┐ ├────────────┤ >
        # q_1:  |0>─┤RZ(0.598658)├ ┤RY(0.156019)├ ┤RZ(0.155995)├ ┤CNOT├ ───■── ───┼┤RZ(0.832443)├ ┤RY(0.212339)├ >
        #           ├────────────┤ ├────────────┤ ├────────────┤ └────┘ ┌──┴─┐    │└────────────┘ ├────────────┤ >
        # q_2:  |0>─┤RZ(0.058084)├ ┤RY(0.866176)├ ┤RZ(0.601115)├ ────── ┤CNOT├ ───■────────────── ┤RZ(0.183405)├ >
        #           └────────────┘ └────────────┘ └────────────┘        └────┘                    └────────────┘ >

        #          ┌────────────┐ ┌────────────┐        ┌────┐
        # q_0:  |0>┤RY(0.020584)├ ┤RZ(0.969910)├ ───■── ┤CNOT├ ──────
        #          ├────────────┤ └────────────┘    │   └──┬─┘ ┌────┐
        # q_1:  |0>┤RZ(0.181825)├ ────────────── ───┼── ───■── ┤CNOT├
        #          ├────────────┤ ┌────────────┐ ┌──┴─┐        └──┬─┘
        # q_2:  |0>┤RY(0.304242)├ ┤RZ(0.524756)├ ┤CNOT├ ────── ───■──
        #          └────────────┘ └────────────┘ └────┘
        #[0.6881335561525671, 0.31186644384743273]

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
    def compute_circuit(self, input_data, weights, num_qbits, num_cbits): ...
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
    :param rotation: one-parameter single-qubit gate to use, default: ``,use rx

    Example::

        import pyqpanda as pq
        import numpy as np
        from pyvqnet.qnn.template import BasicEntanglerTemplate
        np.random.seed(42)
        num_qubits = 5
        shape = [1, num_qubits]
        weights = np.random.random(size=shape)

        machine = pq.CPUQVM()
        machine.init_qvm()
        qubits = machine.qAlloc_many(num_qubits)

        circuit = BasicEntanglerTemplate(weights=weights, num_qubits=num_qubits, rotation=pq.RZ)
        result = circuit.create_circuit(qubits)
        circuit.print_circuit(qubits)

        prob = machine.prob_run_dict(result, qubits[0], -1)
        prob = list(prob.values())
        print(prob)
        #           ┌────────────┐                             ┌────┐
        # q_0:  |0>─┤RZ(0.374540)├ ───■── ────── ────── ────── ┤CNOT├
        #           ├────────────┤ ┌──┴─┐                      └──┬─┘
        # q_1:  |0>─┤RZ(0.950714)├ ┤CNOT├ ───■── ────── ────── ───┼──
        #           ├────────────┤ └────┘ ┌──┴─┐                  │
        # q_2:  |0>─┤RZ(0.731994)├ ────── ┤CNOT├ ───■── ────── ───┼──
        #           ├────────────┤        └────┘ ┌──┴─┐           │
        # q_3:  |0>─┤RZ(0.598658)├ ────── ────── ┤CNOT├ ───■── ───┼──
        #           ├────────────┤               └────┘ ┌──┴─┐    │
        # q_4:  |0>─┤RZ(0.156019)├ ────── ────── ────── ┤CNOT├ ───■──
        #           └────────────┘                      └────┘

        # [1.0, 0.0]

    """
    n_layers: Incomplete
    num_qubits: Incomplete
    weights: Incomplete
    rotation: Incomplete
    def __init__(self, weights: Incomplete | None = None, num_qubits: int = 1, rotation: str = '') -> None: ...
    def Rot(self, qubits, l, weights):
        """
        :param qubits: quantum bits
        :param l: enter the number of layers
        :param weights: input weight
        :return: quantum circuit
        """
    def create_circuit(self, qubits): ...
    def compute_circuit(self, input_data, weights, num_qbits, num_cbits): ...
    def print_circuit(self, qubits) -> None: ...

def MultiRZ_Gate(qubits, weights, wires) -> None: ...
def QubitUnitary(qubits, matrix):
    """
    Apply an arbitrary fixed unitary matrix.

    """
