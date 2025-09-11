import tensornetwork as tn
from . import gates as gates
from .abstractcircuit import AbstractCircuit as AbstractCircuit
from .cons import backend as backend, contractor as contractor, dtypestr as dtypestr, move_tensor_to_same_complex_dtype as move_tensor_to_same_complex_dtype, move_tensor_to_same_device as move_tensor_to_same_device, npdtype as npdtype, rdtypestr as rdtypestr
from .mps_base import FiniteMPS as FiniteMPS
from .quantum import QuOperator as QuOperator, QuVector as QuVector
from _typeshed import Incomplete
from typing import Any, Sequence

Gate = gates.Gate
Tensor = Any

def split_tensor(tensor: Tensor, center_left: bool = True, split: dict[str, Any] | None = None) -> tuple[Tensor, Tensor]:
    """
    Split the tensor by SVD or QR depends on whether a truncation is required.

    :param tensor: The input tensor to split.
    :type tensor: Tensor
    :param center_left: Determine the orthogonal center is on the left tensor or the right tensor.
    :type center_left: bool, optional
    :return: Two tensors after splitting
    :rtype: Tuple[Tensor, Tensor]
    """

class MPSCircuit(AbstractCircuit):
    """
    ``MPSCircuit`` class.
    Simple usage demo below.

    .. code-block:: python

        mps = tc.MPSCircuit(3)
        mps.H(1)
        mps.CNOT(0, 1)
        mps.rx(2, theta=tc.num_to_tensor(1.))
        mps.expectation((tc.gates.z(), 2))

    """
    is_mps: bool
    circuit_param: Incomplete
    split: Incomplete
    def __init__(self, nqubits, center_position: Incomplete | None = None, tensors: Sequence[Tensor] | None = None, wavefunction: QuVector | Tensor | None = None, split: dict[str, Any] | None = None) -> None:
        """
        MPSCircuit object based on state simulator.

        :param nqubits: The number of qubits in the circuit.
        :type nqubits: int
        :param center_position: The center position of MPS, default to 0
        :type center_position: int, optional
        :param tensors: If not None, the initial state of the circuit is taken as ``tensors``
            instead of :math:`\\vert 0\\rangle^n` qubits, defaults to None.
            When ``tensors`` are specified, if ``center_position`` is None, then the tensors are canonicalized,
            otherwise it is assumed the tensors are already canonicalized at the ``center_position``
        :type tensors: Sequence[Tensor], optional
        :param wavefunction: If not None, it is transformed to the MPS form according to the split rules
        :type wavefunction: Tensor
        :param split: Split rules
        :type split: Any
        """
    def get_bond_dimensions(self) -> Tensor:
        """
        Get the MPS bond dimensions

        :return: MPS tensors
        :rtype: Tensor
        """
    def get_tensors(self) -> list[Tensor]:
        """
        Get the MPS tensors

        :return: MPS tensors
        :rtype: List[Tensor]
        """
    def get_center_position(self) -> int | None:
        """
        Get the center position of the MPS

        :return: center position
        :rtype: Optional[int]
        """
    def set_split_rules(self, split: dict[str, Any]) -> None:
        """
        Set truncation split when double qubit gates are applied.
        If nothing is specified, no truncation will take place and the bond dimension will keep growing.
        For more details, refer to `split_tensor`.

        :param split: Truncation split
        :type split: Any
        """
    def position(self, site) -> None:
        """
        Wrapper of tn.FiniteMPS.position.
        Set orthogonality center.

        :param site: The orthogonality center
        :type site: int
        """
    def apply_single_gate(self, gate: Gate, index: int) -> None:
        """
        Apply a single qubit gate on MPS; no truncation is needed.

        :param gate: gate to be applied
        :type gate: Gate
        :param index: Qubit index of the gate
        :type index: int
        """
    def apply_adjacent_double_gate(self, gate: Gate, index1: int, index2: int, center_position: int | None = None, split: dict[str, Any] | None = None) -> None:
        """
        Apply a double qubit gate on adjacent qubits of Matrix Product States (MPS).

        :param gate: The Gate to be applied
        :type gate: Gate
        :param index1: The first qubit index of the gate
        :type index1: int
        :param index2: The second qubit index of the gate
        :type index2: int
        :param center_position: Center position of MPS, default is None
        :type center_position: Optional[int]
        """
    def consecutive_swap(self, index_from: int, index_to: int, split: dict[str, Any] | None = None) -> None: ...
    def apply_double_gate(self, gate: Gate, index1: int, index2: int, split: dict[str, Any] | None = None) -> None:
        """
        Apply a double qubit gate on MPS.

        :param gate: The Gate to be applied
        :type gate: Gate
        :param index1: The first qubit index of the gate
        :type index1: int
        :param index2: The second qubit index of the gate
        :type index2: int
        """
    @classmethod
    def gate_to_MPO(cls, gate: Gate | Tensor, *index: int) -> tuple[Sequence[Tensor], int]:
        """
        Convert gate to MPO form with identities at empty sites
        """
    @classmethod
    def MPO_to_gate(cls, tensors: Sequence[Tensor]) -> Gate:
        """
        Convert MPO to gate
        """
    @classmethod
    def reduce_tensor_dimension(cls, tensor_left: Tensor, tensor_right: Tensor, center_left: bool = True, split: dict[str, Any] | None = None) -> tuple[Tensor, Tensor]:
        """
        Reduce the bond dimension between two general tensors by SVD
        """
    def reduce_dimension(self, index_left, center_left: bool = True, split: dict[str, Any] | None = None) -> None:
        """
        Reduce the bond dimension between two adjacent sites by SVD
        """
    def apply_MPO(self, tensors: Sequence[Tensor], index_left, center_left: bool = True, split: dict[str, Any] | None = None) -> None:
        """
        Apply a MPO to the MPS
        """
    def apply_nqubit_gate(self, gate: Gate, *index: int, split: dict[str, Any] | None = None) -> None:
        """
        Apply a n-qubit gate by transforming the gate to MPO
        """
    def apply_general_gate(self, gate: Gate | QuOperator, *index: int, name: str | None = None, split: dict[str, Any] | None = None, mpo: bool = False, ir_dict: dict[str, Any] | None = None) -> None:
        '''
        Apply a general qubit gate on MPS.

        :param gate: The Gate to be applied
        :type gate: Gate
        :raises ValueError: "MPS does not support application of gate on > 2 qubits."
        :param index: Qubit indices of the gate
        :type index: int
        '''
    apply = apply_general_gate
    def mid_measurement(self, index: int, keep: int = 0) -> None:
        """
        Middle measurement in the z-basis on the circuit, note the wavefunction output is not normalized
        with ``mid_measurement`` involved, one should normalized the state manually if needed.

        :param index: The index of qubit that the Z direction postselection applied on
        :type index: int
        :param keep: 0 for spin up, 1 for spin down, defaults to 0
        :type keep: int, optional
        """
    def is_valid(self) -> bool:
        """
        Check whether the circuit is legal.

        :return: Whether the circuit is legal.
        :rtype: bool
        """
    @classmethod
    def wavefunction_to_tensors(cls, wavefunction: Tensor, dim_phys: int = 2, norm: bool = True, split: dict[str, Any] | None = None) -> list[Tensor]:
        """
        Construct the MPS tensors from a given wavefunction.

        :param wavefunction: The given wavefunction (any shape is OK)
        :type wavefunction: Tensor
        :param split: Truncation split
        :type split: Dict
        :param dim_phys: Physical dimension, 2 for MPS and 4 for MPO
        :type dim_phys: int
        :param norm: Whether to normalize the wavefunction
        :type norm: bool
        :return: The tensors
        :rtype: List[Tensor]
        """
    def wavefunction(self, form: str = 'default') -> Tensor:
        """
        Compute the output wavefunction from the circuit.

        :param form: the str indicating the form of the output wavefunction
        :type form: str, optional
        :return: Tensor with shape [1, -1]
        :rtype: Tensor
           a  b           ab
           |  |           ||
        i--A--B--j  -> i--XX--j
        """
    state = wavefunction
    def copy_without_tensor(self) -> MPSCircuit:
        """
        Copy the current MPS without the tensors.

        :return: The constructed MPS
        :rtype: MPSCircuit
        """
    def copy(self) -> MPSCircuit:
        """
        Copy the current MPS.

        :return: The constructed MPS
        :rtype: MPSCircuit
        """
    def conj(self) -> MPSCircuit:
        """
        Compute the conjugate of the current MPS.

        :return: The constructed MPS
        :rtype: MPSCircuit
        """
    def get_norm(self) -> Tensor:
        """
        Get the normalized Center Position.

        :return: Normalized Center Position.
        :rtype: Tensor
        """
    def normalize(self) -> None:
        """
        Normalize MPS Circuit according to the center position.
        """
    def amplitude(self, l: str) -> Tensor: ...
    def proj_with_mps(self, other: MPSCircuit, conj: bool = True) -> Tensor:
        """
        Compute the projection between `other` as bra and `self` as ket.

        :param other: ket of the other MPS, which will be converted to bra automatically
        :type other: MPSCircuit
        :return: The projection in form of tensor
        :rtype: Tensor
        """
    def slice(self, begin, end) -> MPSCircuit:
        """
        Get a slice of the MPS (only for internal use)
        """
    def expectation_multi_pauli(self, *ops: tuple[tn.Node, list[int]], reuse: bool = True, enable_lightcone: bool = False, noise_conf: Any | None = None, nmc: int = 1000, status: Tensor | None = None, **kws: Any) -> Tensor: ...
    def expectation(self, *ops: tuple[Gate, list[int]], reuse: bool = True, other: MPSCircuit | None = None, conj: bool = True, normalize: bool = False, split: dict[str, Any] | None = None, **kws: Any) -> Tensor:
        """
        Compute the expectation of corresponding operators in the form of tensor.

        :param ops: Operator and its position on the circuit,
            eg. ``(gates.Z(), [1]), (gates.X(), [2])`` is for operator :math:`Z_1X_2`
        :type ops: Tuple[tn.Node, List[int]]
        :param reuse: If True, then the wavefunction tensor is cached for further expectation evaluation,
            defaults to be true.
        :type reuse: bool, optional
        :param other: If not None, will be used as bra
        :type other: MPSCircuit, optional
        :param conj: Whether to conjugate the bra state
        :type conj: bool, defaults to be True
        :param normalize: Whether to normalize the MPS
        :type normalize: bool, defaults to be True
        :param split: Truncation split
        :type split: Any
        :return: The expectation of corresponding operators
        :rtype: Tensor
        """
    def get_quvector(self) -> QuVector:
        """
        Get the representation of the output state in the form of ``QuVector``
            has to be full contracted in MPS

        :return: ``QuVector`` representation of the output state from the circuit
        :rtype: QuVector
        """
    def measure(self, *index: int, with_prob: bool = False, status: Tensor | None = None) -> tuple[Tensor, Tensor]:
        """
        Take measurement to the given quantum lines.

        :param index: Measure on which quantum line.
        :type index: int
        :param with_prob: If true, theoretical probability is also returned.
        :type with_prob: bool, optional
        :param status: external randomness, with shape [index], defaults to None
        :type status: Optional[Tensor]
        :return: The sample output and probability (optional) of the quantum line.
        :rtype: Tuple[Tensor, Tensor]
        """
