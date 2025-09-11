import tensornetwork as tn
from . import channels as channels, gates as gates
from .basecircuit import BaseCircuit as BaseCircuit
from .channels import kraus_to_super_gate as kraus_to_super_gate
from .circuit import Circuit as Circuit
from .cons import backend as backend, contractor as contractor, dtypestr as dtypestr
from .quantum import QuOperator as QuOperator
from _typeshed import Incomplete
from typing import Any, Callable, Sequence

Gate = gates.Gate
Tensor = Any

class DMCircuit(BaseCircuit):
    is_dm: bool
    inputs: Incomplete
    dminputs: Incomplete
    mps_inputs: Incomplete
    mpo_dminputs: Incomplete
    split: Incomplete
    circuit_param: Incomplete
    def __init__(self, nqubits: int, empty: bool = False, inputs: Tensor | None = None, mps_inputs: QuOperator | None = None, dminputs: Tensor | None = None, mpo_dminputs: QuOperator | None = None, split: dict[str, Any] | None = None) -> None:
        """
        The density matrix simulator based on tensornetwork engine.

        :param nqubits: Number of qubits
        :type nqubits: int
        :param empty: if True, nothing initialized, only for internal use, defaults to False
        :type empty: bool, optional
        :param inputs: the state input for the circuit, defaults to None
        :type inputs: Optional[Tensor], optional
        :param mps_inputs: QuVector for a MPS like initial pure state.
        :type mps_inputs: Optional[QuOperator]
        :param dminputs: the density matrix input for the circuit, defaults to None
        :type dminputs: Optional[Tensor], optional
        :param mpo_dminputs: QuOperator for a MPO like initial density matrix.
        :type mpo_dminputs: Optional[QuOperator]
        :param split: dict if two qubit gate is ready for split, including parameters for at least one of
            ``max_singular_values`` and ``max_truncation_err``.
        :type split: Optional[Dict[str, Any]]
        """
    @staticmethod
    def check_kraus(kraus: Sequence[Gate]) -> bool: ...
    def apply_general_kraus(self, kraus: Sequence[Gate], index: Sequence[tuple[int, ...]], **kws: Any) -> None: ...
    general_kraus = apply_general_kraus
    @staticmethod
    def apply_general_kraus_delayed(krausf: Callable[..., Sequence[Gate]]) -> Callable[..., None]: ...
    def densitymatrix(self, check: bool = False, reuse: bool = True) -> Tensor:
        """
        Return the output density matrix of the circuit.

        :param check: check whether the final return is a legal density matrix, defaults to False
        :type check: bool, optional
        :param reuse: whether to reuse previous results, defaults to True
        :type reuse: bool, optional
        :return: The output densitymatrix in 2D shape tensor form
        :rtype: Tensor
        """
    state = densitymatrix
    def wavefunction(self) -> Tensor:
        """
        get the wavefunction of outputs,
        raise error if the final state is not purified
        [Experimental: the phase factor is not fixed for different backend]

        :return: wavefunction vector
        :rtype: Tensor
        """
    get_dm_as_quvector: Incomplete
    def get_dm_as_quoperator(self) -> QuOperator:
        """
        Get the representation of the output state in the form of ``QuOperator``
        while maintaining the circuit uncomputed

        :return: ``QuOperator`` representation of the output state from the circuit
        :rtype: QuOperator
        """
    def expectation(self, *ops: tuple[tn.Node, list[int]], reuse: bool = True, noise_conf: Any | None = None, status: Tensor | None = None, **kws: Any) -> tn.Node.tensor:
        """
        Compute the expectation of corresponding operators.

        :param ops: Operator and its position on the circuit,
            eg. ``(tc.gates.z(), [1, ]), (tc.gates.x(), [2, ])`` is for operator :math:`Z_1X_2`.
        :type ops: Tuple[tn.Node, List[int]]
        :param reuse: whether contract the density matrix in advance, defaults to True
        :type reuse: bool
        :param noise_conf: Noise Configuration, defaults to None
        :type noise_conf: Optional[NoiseConf], optional
        :param status: external randomness given by tensor uniformly from [0, 1], defaults to None,
            used for noisfy circuit sampling
        :type status: Optional[Tensor], optional
        :return: Tensor with one element
        :rtype: Tensor
        """
    @staticmethod
    def check_density_matrix(dm: Tensor) -> None: ...
    def to_circuit(self, circuit_params: dict[str, Any] | None = None) -> Circuit:
        """
        convert into state simulator
        (current implementation ignores all noise channels)

        :param circuit_params: kws to initialize circuit object,
            defaults to None
        :type circuit_params: Optional[Dict[str, Any]], optional
        :return: Circuit with no noise
        :rtype: Circuit
        """

class DMCircuit2(DMCircuit):
    def apply_general_kraus(self, kraus: Sequence[Gate], *index: int, **kws: Any) -> None: ...
    general_kraus = apply_general_kraus
    @staticmethod
    def apply_general_kraus_delayed(krausf: Callable[..., Sequence[Gate]]) -> Callable[..., None]: ...
