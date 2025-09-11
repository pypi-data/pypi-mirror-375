from ....dtype import C_DTYPE as C_DTYPE, complex_dtype_to_float_dtype as complex_dtype_to_float_dtype, kcomplex128 as kcomplex128
from ....nn.torch import TorchModule as TorchModule, TorchModuleList as TorchModuleList
from ....tensor import QTensor as QTensor, adjoint as adjoint, full_like as full_like, ones_like as ones_like, to_tensor as to_tensor
from ..qcircuit import CCZ as NCCZ, CH as NCH, CNOT as NCNot, CR as NCR, CRX as NCRX, CRY as NCRY, CRZ as NCRZ, CRot as NCRot, CSWAP as NCSWAP, CY as NCY, CZ as NCZ, ControlledPhaseShift as NControlledPhaseShift, DoubleExcitation as NDoubleExcitation, Hadamard as NHadamard, I as NI, IsingXX as NIsingXX, IsingXY as NIsingXY, IsingYY as NIsingYY, IsingZZ as NIsingZZ, MultiControlledX as NMultiControlledX, MultiRZ as NMultiRZ, P as NP, PauliX as NPauliX, PauliY as NPauliY, PauliZ as NPauliZ, PhaseShift as NPhaseShift, RX as NRX, RXX as NRXX, RY as NRY, RYY as NRYY, RZ as NRZ, RZX as NRZX, RZZ as NRZZ, Rot as NRot, S as NS, SDG as NSDG, SWAP as NSWAP, SingleExcitation as NSingleExcitation, T as NT, TDG as NTDG, Toffoli as NToffoli, U1 as NU1, U2 as NU2, U3 as NU3, VQC_AllSinglesDoubles as VQC_AllSinglesDoubles, VQC_AngleEmbedding as VQC_AngleEmbedding, VQC_BasisEmbedding as VQC_BasisEmbedding, VQC_BasisRotation as VQC_BasisRotation, VQC_BasisState as VQC_BasisState, VQC_CCZ as VQC_CCZ, VQC_CRotCircuit as VQC_CRotCircuit, VQC_CSWAPcircuit as VQC_CSWAPcircuit, VQC_ComplexEntangledCircuit as VQC_ComplexEntangledCircuit, VQC_Controlled_Hadamard as VQC_Controlled_Hadamard, VQC_FermionicDoubleExcitation as VQC_FermionicDoubleExcitation, VQC_FermionicSingleExcitation as VQC_FermionicSingleExcitation, VQC_IQPEmbedding as VQC_IQPEmbedding, VQC_QuantumPoolingCircuit as VQC_QuantumPoolingCircuit, VQC_RotCircuit as VQC_RotCircuit, VQC_UCCSD as VQC_UCCSD, VQC_ZFeatureMap as VQC_ZFeatureMap, VQC_ZZFeatureMap as VQC_ZZFeatureMap, X1 as NX1, Y1 as NY1, Z1 as NZ1, cnot as cnot, controlledphaseshift as controlledphaseshift, cr as cr, crx as crx, cry as cry, crz as crz, cswap as cswap, cy as cy, cz as cz, double_excitation as double_excitation, hadamard as hadamard, i as i, iSWAP as NiSWAP, isingxx as isingxx, isingxy as isingxy, isingyy as isingyy, isingzz as isingzz, iswap as iswap, multicontrolledx as multicontrolledx, multirz as multirz, p as p, paulix as paulix, pauliy as pauliy, pauliz as pauliz, phaseshift as phaseshift, ring_cnot as ring_cnot, rot as rot, rx as rx, rxx as rxx, ry as ry, ryy as ryy, rz as rz, rzx as rzx, rzz as rzz, s as s, sdg as sdg, single_excitation as single_excitation, swap as swap, t as t, tdg as tdg, toffoli as toffoli, u1 as u1, u2 as u2, u3 as u3, vqc_allsinglesdoubles as vqc_allsinglesdoubles, vqc_angle_embedding as vqc_angle_embedding, vqc_basis_embedding as vqc_basis_embedding, vqc_basisrotation as vqc_basisrotation, vqc_ccz as vqc_ccz, vqc_controlled_hadamard as vqc_controlled_hadamard, vqc_crot_circuit as vqc_crot_circuit, vqc_fermionic_double_excitation as vqc_fermionic_double_excitation, vqc_fermionic_single_excitation as vqc_fermionic_single_excitation, vqc_iqp_embedding as vqc_iqp_embedding, vqc_quantumpooling_circuit as vqc_quantumpooling_circuit, vqc_rotcircuit as vqc_rotcircuit, vqc_uccsd as vqc_uccsd, vqc_zfeaturemap as vqc_zfeaturemap, vqc_zzfeaturemap as vqc_zzfeaturemap, x1 as x1, y1 as y1, z1 as z1
from ..qmatrix import double_mat_dict as double_mat_dict
from ..qop import QMachine as NQMachine, QModule as NQModule
from .qop import DiagonalOperation as DiagonalOperation, Observable as Observable, Operation as Operation, Operator as Operator, QMachine as QMachine, StateEncoder as StateEncoder
from _typeshed import Incomplete
from abc import ABCMeta
from pyvqnet.backends_mock import TorchMock as TorchMock

class RX(Operation, NRX, metaclass=ABCMeta):
    """Class for RX Gate."""
    tensor_backend: str

class RY(Operation, NRY, metaclass=ABCMeta):
    """Class for RY Gate."""
    tensor_backend: str

class RZ(Operation, NRZ, metaclass=ABCMeta):
    """Class for RZ Gate."""
    tensor_backend: str

class RING_CNOT(Operation, metaclass=ABCMeta):
    """Class for RING_CNOT Gate."""
    tensor_backend: str

class I(Observable, NI, metaclass=ABCMeta):
    """Class for Identity Gate."""
    tensor_backend: str

class PauliZ(Observable, NPauliZ, metaclass=ABCMeta):
    """Class for Pauli Z Gate."""
    tensor_backend: str

class PauliX(Observable, NPauliX, metaclass=ABCMeta):
    """Class for Pauli X Gate."""
    tensor_backend: str

class PauliY(Observable, NPauliY, metaclass=ABCMeta):
    """Class for Pauli Y Gate."""
    tensor_backend: str

class ControlledPhaseShift(Operation, NControlledPhaseShift, metaclass=ABCMeta):
    tensor_backend: str

class Hadamard(Observable, NHadamard, metaclass=ABCMeta):
    """Class for Hadamard Gate."""
    tensor_backend: str

class S(DiagonalOperation, NS, metaclass=ABCMeta):
    """Class for S Gate."""
    tensor_backend: str

class MultiRZ(DiagonalOperation, NMultiRZ, metaclass=ABCMeta):
    """Class for MultiRZ Gate."""
    tensor_backend: str

class iSWAP(Operation, NiSWAP, metaclass=ABCMeta):
    """Class for iSWAP Gate."""
    tensor_backend: str

class X1(Operation, NX1, metaclass=ABCMeta):
    """Class for X1 Gate."""
    tensor_backend: str

class Y1(Operation, NY1, metaclass=ABCMeta):
    """Class for Y1 Gate."""
    tensor_backend: str

class Z1(Operation, NZ1, metaclass=ABCMeta):
    """Class for Z1 Gate."""
    tensor_backend: str

class CRX(Operation, NCRX, metaclass=ABCMeta):
    """Class for CRX Gate."""
    tensor_backend: str

class CRY(Operation, NCRY, metaclass=ABCMeta):
    """Class for CRY Gate."""
    tensor_backend: str

class CRZ(Operation, NCRZ, metaclass=ABCMeta):
    """Class for CRZ Gate."""
    tensor_backend: str

class P(DiagonalOperation, NP, metaclass=ABCMeta):
    """Class for P Gate."""
    tensor_backend: str

class U1(DiagonalOperation, NU1, metaclass=ABCMeta):
    """Class for U1 Gate."""
    tensor_backend: str

class U2(Operation, NU2, metaclass=ABCMeta):
    """Class for U2 Gate."""
    tensor_backend: str

class U3(Operation, NU3, metaclass=ABCMeta):
    """Class for U3 Gate."""
    tensor_backend: str

class CCZ(Operation, NCCZ, metaclass=ABCMeta):
    """Class for CCZ Gate."""
    tensor_backend: str

class CY(Operation, NCY, metaclass=ABCMeta):
    """Class for CY Gate."""
    tensor_backend: str

class CNOT(Operation, NCNot, metaclass=ABCMeta):
    """Class for CNOT Gate."""
    tensor_backend: str

class CR(DiagonalOperation, NCR, metaclass=ABCMeta):
    """Class for CR Gate."""
    tensor_backend: str

class SWAP(Operation, NSWAP, metaclass=ABCMeta):
    """Class for SWAP Gate."""
    tensor_backend: str

class CSWAP(Operation, NCSWAP, metaclass=ABCMeta):
    """Class for CSWAP Gate."""
    tensor_backend: str

class CZ(DiagonalOperation, NCZ, metaclass=ABCMeta):
    """Class for CZ Gate."""
    tensor_backend: str

class RXX(Operation, NRXX, metaclass=ABCMeta):
    """Class for CZ Gate."""
    tensor_backend: str

class RYY(Operation, NRYY, metaclass=ABCMeta):
    """Class for RYY Gate."""
    tensor_backend: str

class RZZ(Operation, NRZZ, metaclass=ABCMeta):
    """Class for CZ Gate."""
    tensor_backend: str

class RZX(Operation, NRZX, metaclass=ABCMeta):
    """Class for CZ Gate."""
    tensor_backend: str

class Toffoli(Operation, NToffoli, metaclass=ABCMeta):
    """Class for CZ Gate."""
    tensor_backend: str

class MultiControlledX(Operation, NMultiControlledX, metaclass=ABCMeta):
    tensor_backend: str

class T(DiagonalOperation, NT, metaclass=ABCMeta):
    """Class for T Gate."""
    tensor_backend: str

class PhaseShift(DiagonalOperation, NPhaseShift, metaclass=ABCMeta):
    """Class for PhaseShift Gate."""
    tensor_backend: str

class IsingXX(DiagonalOperation, NIsingXX, metaclass=ABCMeta):
    """Class for IsingXX gate."""
    tensor_backend: str

class IsingXY(DiagonalOperation, NIsingXY, metaclass=ABCMeta):
    """Class for IsingXY gate."""
    tensor_backend: str

class IsingYY(DiagonalOperation, NIsingYY, metaclass=ABCMeta):
    """Class for IsingYY gate."""
    tensor_backend: str

class IsingZZ(DiagonalOperation, NIsingZZ, metaclass=ABCMeta):
    """Class for IsingZZ gate."""
    tensor_backend: str

class SingleExcitation(Operation, NSingleExcitation, metaclass=ABCMeta):
    tensor_backend: str

class DoubleExcitation(Operation, NDoubleExcitation, metaclass=ABCMeta):
    tensor_backend: str

class TDG(Operation, NTDG, metaclass=ABCMeta):
    """Class for TDG Gate."""
    tensor_backend: str

class SDG(Operation, NSDG, metaclass=ABCMeta):
    """Class for SDG Gate."""
    tensor_backend: str

class Rot(Operation, NRot, metaclass=ABCMeta):
    """Class for Rot Gate."""
    tensor_backend: str

class CH(Operation, NCH, metaclass=ABCMeta):
    """Class for CH Gate."""
    tensor_backend: str

class CRot(Operation, NCRot, metaclass=ABCMeta):
    """Class for CRot Gate."""
    tensor_backend: str

torch_op_class_dict: Incomplete

def vqc_amplitude_embedding(input_feature, q_machine: QMachine): ...
VQC_AmplitudeEmbedding = vqc_amplitude_embedding

class VQC_BasicEntanglerTemplate(TorchModule, NQModule):
    """

    Layers consisting of one-parameter single-qubit rotations on each qubit, followed by a closed chain or *ring* of
     CNOT gates.
     
    The ring of CNOT gates connects every qubit with its neighbour, with the last qubit being considered as a neighbour to the first qubit.


    :param num_layers: number of repeat layers, default: 1.
    :param num_qubits: number of qubits, default: 1.
    :param rotation: one-parameter single-qubit gate to use, default: `RX`
    :param initial: initialized same value for all paramters. default:None,parameters will be initialized randomly.
    :param dtype: data type of parameter, default:None,use float32.
    :return: A VQC_BasicEntanglerTemplate instance
    """
    n_layers: Incomplete
    num_qubits: Incomplete
    rotation: Incomplete
    vqc: Incomplete
    def __init__(self, num_layers: int = 1, num_qubits: int = 1, rotation: str = 'RX', initial=None, dtype: int | None = None) -> None: ...
    def Rot(self, gate, initial, dtype):
        """
        :param qubits: quantum bits

        :return: quantum circuit
        """
    def create_circuit(self, initial, dtype): ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine): ...

class _single_rot(TorchModule):
    n_qubits: Incomplete
    single_rot_gate_list: Incomplete
    vqc: Incomplete
    def __init__(self, single_rot_gate_list, n_qubits, initial, dtype, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine): ...

class _entangle(TorchModule):
    vqc: Incomplete
    def __init__(self, entangle_gate, entangle_rules, dtype, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine): ...

class VQC_HardwareEfficientAnsatz(TorchModule, NQModule):
    '''
    A implementation of Hardware Efficient Ansatz introduced by thesis: Hardware-efficient Variational Quantum Eigensolver for Small Molecules and
    Quantum Magnets https://arxiv.org/pdf/1704.05018.pdf.

    :param n_qubits: Number of qubits.
    :param single_rot_gate_list: A single qubit rotation gate list is constructed by one or several rotation gate that act on every qubit.Currently
    support Rx, Ry, Rz.
    :param entangle_gate: The non parameterized entanglement gate.CNOT,CZ is supported.default:CNOT.
    :param entangle_rules: How entanglement gate is used in the circuit. \'linear\' means the entanglement gate will be act on every neighboring qubits. \'all\' means
            the entanglment gate will be act on any two qbuits. Default:linear.
    :param depth: The depth of ansatz, default:1.
    :parma initial: initial one same value for paramaters,default:None,this module will initialize parameters randomly.
    :param dtype: data dtype of parameters.
    :return a VQC_HardwareEfficientAnsatz instance.

    Example::

        from pyvqnet.nn.torch import TorchModule,Linear,TorchModuleList
        from pyvqnet.qnn.vqc.torch.qcircuit import VQC_HardwareEfficientAnsatz,RZZ,RZ
        from pyvqnet.qnn.vqc.torch import Probability,QMachine
        from pyvqnet import tensor
        import pyvqnet

        pyvqnet.backends.set_backend("torch")
        pyvqnet.utils.set_random_seed(25)

        class QM(TorchModule):
            def __init__(self, name=""):
                super().__init__(name)
                self.linearx = Linear(4,2)
                self.ansatz = VQC_HardwareEfficientAnsatz(4, ["rx", "RY", "rz"],
                                            entangle_gate="cnot",
                                            entangle_rules="linear",
                                            depth=2)
                self.encode1 = RZ(wires=0)
                self.encode2 = RZ(wires=1)
                self.measure = Probability(wires=[0,2])
                self.device = QMachine(4)
            def forward(self, x, *args, **kwargs):
                self.device.reset_states(x.shape[0])
                y = self.linearx(x)
                self.encode1(params = y[:, [0]],q_machine = self.device,)
                self.encode2(params = y[:, [1]],q_machine = self.device,)
                self.ansatz(q_machine =self.device)
                return self.measure(q_machine =self.device)

        bz =3
        inputx = tensor.arange(1.0,bz*4+1).reshape([bz,4])
        inputx.requires_grad= True
        qlayer = QM()
        y = qlayer(inputx)
        y.backward()
        print(y)

        # [[0.1064599,0.2501889,0.3411652,0.3021863],
        #  [0.1064599,0.2501888,0.3411651,0.3021862],
        #  [0.1064598,0.250189 ,0.341165 ,0.3021862]]

        print(qlayer.state_dict())

        for p in qlayer.parameters():
            print(p.grad)
    '''
    n_qubits: Incomplete
    qcir: Incomplete
    dtype: Incomplete
    def __init__(self, n_qubits, single_rot_gate_list, entangle_gate: str = 'CNOT', entangle_rules: str = 'linear', depth: int = 1, initial=None, dtype: int | None = ...) -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine): ...
    def create_ansatz(self, initial, dtype):
        """
        create ansatz use weights in parameterized gates
        :param weights: varational parameters in the ansatz.
        :return: a pyqpanda Hardware Efficient Ansatz instance .
    
        """

class VQC_StronglyEntanglingTemplate(TorchModule, NQModule):
    '''
    Layers consisting of single qubit rotations and entanglers, inspired by the `circuit-centric classifier design
     <https://arxiv.org/abs/1804.00633>`__ .

    
    :param num_layers: number of repeat layers, default: 1.
    :param num_qubits: number of qubits, default: 1.
    :param ranges: sequence determining the range hyperparameter for each subsequent layer; default: None
                                using :math: `r=l \\mod M` for the :math:`l` th layer and :math:`M` qubits.
    :param initial: initial value for all parameters.default: None,initialized randomly.
    :param dtype: data type of parameter, default:None,use float32.
    Example::

        from pyvqnet.nn.torch import TorchModule,Linear,TorchModuleList
        from pyvqnet.qnn.vqc.torch.qcircuit import VQC_StronglyEntanglingTemplate
        from pyvqnet.qnn.vqc.torch import Probability, QMachine
        from pyvqnet import tensor
        import pyvqnet

        pyvqnet.backends.set_backend("torch")
        pyvqnet.utils.set_random_seed(25)
        class QM(TorchModule):
            def __init__(self, name=""):
                super().__init__(name)

                self.ansatz = VQC_StronglyEntanglingTemplate(2,
                                                    4,
                                                    None,
                                                    initial=tensor.ones([1, 1]))

                self.measure = Probability(wires=[0, 1])
                self.device = QMachine(4)

            def forward(self,x, *args, **kwargs):

                self.ansatz(q_machine=self.device)
                return self.measure(q_machine=self.device)

        bz = 1
        inputx = tensor.arange(1.0, bz * 4 + 1).reshape([bz, 4])
        qlayer = QM()
        y = qlayer(inputx)
        y.backward()
        print(y)

        # [[0.3745951,0.154298 ,0.059156 ,0.4119509]]

        print(qlayer.state_dict())

        for p in qlayer.parameters():
            print(p.grad)
    '''
    n_layers: Incomplete
    num_qubits: Incomplete
    ranges: Incomplete
    imprimitive: Incomplete
    vqc: Incomplete
    dtype: Incomplete
    def __init__(self, num_layers: int = 1, num_qubits: int = 1, ranges: list | None = None, initial=None, dtype: int | None = None) -> None: ...
    def Rot(self, l, initial, dtype): ...
    def create_circuit(self, initial, dtype): ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine) -> None: ...

class VQC_QuantumEmbedding(TorchModule, NQModule):
    '''
    use RZ,RY,RZ to create a Variational Quantum Circuit to encode classic data into quantum state.

    Quantum embeddings for machine learning
    Seth Lloyd, Maria Schuld, Aroosa Ijaz, Josh Izaac, Nathan Killoran
    https://arxiv.org/abs/2001.03622

    :param num_repetitions_input: number of repeat times to encode input in a submodule.
    :param depth_input: number of input dimension .
    :param num_unitary_layers: number of repeat times of variational quantum gates.
    :param num_repetitions: number of repeat times of submodule.
    :param initial: initial parameter, default:None.
    :param dtype: data type of parameter, default:None,use float32.
    :param name: name of this module.

    Example::

        from pyvqnet.nn.torch import TorchModule
        from pyvqnet.qnn.vqc.torch.qcircuit import VQC_QuantumEmbedding
        from pyvqnet.qnn.vqc.torch import Probability, QMachine, MeasureAll
        from pyvqnet import tensor
        import pyvqnet

        pyvqnet.backends.set_backend("torch")
        pyvqnet.utils.set_random_seed(25)
        depth_input = 2
        num_repetitions = 2
        num_repetitions_input = 2
        num_unitary_layers = 2
        nq = depth_input * num_repetitions_input
        bz = 12

        class QM(TorchModule):
            def __init__(self, name=""):
                super().__init__(name)

                self.ansatz = VQC_QuantumEmbedding(num_repetitions_input, depth_input,
                                                num_unitary_layers,
                                                num_repetitions ,
                                                initial=tensor.full([1],12.0),dtype=pyvqnet.kfloat64)

                self.measure = MeasureAll(obs={f"Z{nq-1}":1})
                self.device = QMachine(nq)

            def forward(self, x, *args, **kwargs):
                self.device.reset_states(x.shape[0])
                self.ansatz(x,q_machine=self.device)
                return self.measure(q_machine=self.device)

        inputx = tensor.arange(1.0, bz * depth_input + 1).reshape([bz, depth_input])
        qlayer = QM()
        y = qlayer(inputx)
        y.backward()
        print(y)

        # [[-0.2539539],
        #  [-0.1604781],
        #  [ 0.1492927],
        #  [-0.1711951],
        #  [-0.1577127],
        #  [ 0.1396995],
        #  [ 0.0168641],
        #  [-0.0893067],
        #  [ 0.1897008],
        #  [ 0.0941299],
        #  [ 0.055072 ],
        #  [ 0.240857 ]]

        print(qlayer.state_dict())

        for p in qlayer.parameters():
            print(p.grad)
    '''
    param_num: Incomplete
    dtype: Incomplete
    vqc: Incomplete
    def __init__(self, num_repetitions_input: int, depth_input: int, num_unitary_layers: int, num_repetitions: int, dtype: int | None = None, initial=None, name: str = '') -> None: ...
    def create_circuit(self, initial): ...
    def __call__(self, x, *args, **kwargs): ...
    def forward(self, x, q_machine): ...

class ExpressiveEntanglingAnsatz(TorchModule, NQModule):
    '''
    19 different ansatzes from paper: https://arxiv.org/pdf/1905.10876.pdf.

    :param type: circuit type from 1 to 19.
    :param num_wires: number of wires.
    :param depth: circuit depth.
    :param dtype: data type for the paramters, default:None
    :param name: name
    :return:
        a ExpressiveEntanglingAnsatz instance

    Example::

        from pyvqnet.nn.torch import TorchModule
        from pyvqnet.qnn.vqc.torch.qcircuit import ExpressiveEntanglingAnsatz
        from pyvqnet.qnn.vqc.torch import Probability, QMachine, MeasureAll
        from pyvqnet import tensor
        import pyvqnet

        pyvqnet.backends.set_backend("torch")
        pyvqnet.utils.set_random_seed(25)

        class QModel(TorchModule):
            def __init__(self, num_wires, dtype,grad_mode=""):
                super(QModel, self).__init__()

                self._num_wires = num_wires
                self._dtype = dtype
                self.qm = QMachine(num_wires, dtype=dtype,grad_mode=grad_mode)
                self.c1 = ExpressiveEntanglingAnsatz(1,3,2)
                self.measure = MeasureAll(obs={
                    "Z1":1
                })

            def forward(self, x, *args, **kwargs):
                self.qm.reset_states(x.shape[0])
                self.c1(q_machine = self.qm)
                rlt = self.measure(q_machine=self.qm)
                return rlt
            

        input_x = tensor.QTensor([[0.1, 0.2, 0.3]])

        input_x.requires_grad = True

        print(input_x.grad)

        qunatum_model = QModel(num_wires=3, dtype=pyvqnet.kcomplex64)

        batch_y = qunatum_model(input_x)
        batch_y.backward()
        print(batch_y)
        
    '''
    model: Incomplete
    def __init__(self, type: int, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...
    def __call__(self, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_1(TorchModule):
    """
    Circuit 1  from https://arxiv.org/pdf/1905.10876.pdf,
    has depth*num_wires*2 parameters.

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_2(TorchModule):
    """
    Circuit 2  from https://arxiv.org/pdf/1905.10876.pdf,
    has depth*num_wires*2 parameters.

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_3(TorchModule):
    """
    Circuit 3  from https://arxiv.org/pdf/1905.10876.pdf,
    has depth*(num_wires*3-1) parameters.

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_4(TorchModule):
    """
    Circuit 4  from https://arxiv.org/pdf/1905.10876.pdf,
    has depth*(num_wires*3-1) parameters.

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_5(TorchModule):
    """
    Circuit 5  from https://arxiv.org/pdf/1905.10876.pdf,
    has depth*(num_wires*(num_wires-1+4)) parameters.

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_6(TorchModule):
    """
    Circuit 6  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_7(TorchModule):
    """
    Circuit 7  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_8(TorchModule):
    """
    Circuit 8  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_9(TorchModule):
    """
    Circuit 9  from https://arxiv.org/pdf/1905.10876.pdf,


    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_10(TorchModule):
    """
    Circuit 10  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_11(TorchModule):
    """
    Circuit 11  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_12(TorchModule):
    """
    Circuit 12  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_13(TorchModule):
    """
    Circuit 13  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_14(TorchModule):
    """
    Circuit 14  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_15(TorchModule):
    """
    Circuit 15  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_16(TorchModule):
    """
    Circuit 16  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_17(TorchModule):
    """
    Circuit 17  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_18(TorchModule):
    """
    Circuit 18  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_19(TorchModule):
    """
    Circuit 19  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: NQMachine, *args, **kwargs): ...
