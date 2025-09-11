from .qmachine import QMachine as QMachine
from .qmatrix import double_mat_dict as double_mat_dict, float_mat_dict as float_mat_dict, half_float_mat_dict as half_float_mat_dict
from _typeshed import Incomplete
from abc import ABCMeta
from pyvqnet.device import get_readable_device_str as get_readable_device_str
from pyvqnet.dtype import C_DTYPE as C_DTYPE, D_DTYPE as D_DTYPE, F_DTYPE as F_DTYPE, HC_DTYPE as HC_DTYPE, HF_DTYPE as HF_DTYPE, Z_DTYPE as Z_DTYPE, complex_dtype_to_float_dtype as complex_dtype_to_float_dtype, float_dtype_to_complex_dtype as float_dtype_to_complex_dtype, get_readable_dtype_str as get_readable_dtype_str, kcomplex128 as kcomplex128, kcomplex64 as kcomplex64, kfloat32 as kfloat32, kfloat64 as kfloat64, vqnet_complex_dtypes as vqnet_complex_dtypes, vqnet_float_dtypes as vqnet_float_dtypes
from pyvqnet.nn import Module as Module, Parameter as Parameter
from pyvqnet.tensor import QTensor as QTensor, tensor as tensor
from pyvqnet.tensor.utils import FLOAT_2_COMPLEX as FLOAT_2_COMPLEX
from pyvqnet.utils.initializer import quantum_uniform as quantum_uniform

class QModule(Module):
    compiled_op_historys: Incomplete
    def __init__(self, name: str = '') -> None: ...
    @property
    def use_merge_rotations(self): ...
    @use_merge_rotations.setter
    def use_merge_rotations(self, value) -> None:
        """Set the _use_merge_rotations of the module.

        Args:
            value (str): module name.

        """
    @property
    def use_single_qubit_ops_fuse(self): ...
    @use_single_qubit_ops_fuse.setter
    def use_single_qubit_ops_fuse(self, value) -> None:
        """Set the use_single_qubit_ops_fuse of the module.

        Args:
            value (str): module name.

        """
    @property
    def use_commute_controlled(self): ...
    @use_commute_controlled.setter
    def use_commute_controlled(self, value) -> None:
        """Set the _use_commute_controlled of the module.

        Args:
            value (str): module name.

        """
    def __call__(self, *args, **kwargs): ...

class Operator(QModule):
    """The class for quantum operators."""
    non_parameterized_ops: Incomplete
    parameterized_ops: Incomplete
    adjoint_basic_supported_ops: Incomplete
    adjoint_decompose_supported_ops: Incomplete
    dtype_mat_callable_dict: Incomplete
    @property
    def grad_method(self):
        """Gradient computation method.

        * ``'A'``: analytic differentiation using the parameter-shift method.

        """
    wires: Incomplete
    name: Incomplete
    hyper_parameters: Incomplete
    dtype: Incomplete
    use_dagger: Incomplete
    has_params: Incomplete
    trainable: Incomplete
    params: Incomplete
    def __init__(self, has_params: bool = False, trainable: bool = False, init_params=None, wires=None, dtype=..., use_dagger: bool = False, **kwargs) -> None:
        """__init__ function for Operator.

            :param has_params: Whether the operations has parameters.
                Defaults to False.
            :param trainable: Whether the parameters are trainable
                (if contains parameters) or just QTensor from input. Defaults to False.
            :param init_params: Initial parameters.Defaults to None.
            :param wires: Which qubit the operation is applied to. Defaults to None.
            :param dtype: data type for operator's matrix . Z_DTYPE or C_DTYPE
            :param use_dagger: if juse adjointed matrix for this operator.Deafults to False.
            :param kwargs: key arguments which will be saved in hyper_parameters.
        """
    @property
    def matrix(self):
        """The unitary matrix of the operator."""
    def compute_matrix(self):
        """
        alias for matrix
        """
    @property
    def eigvals(self):
        """The eigenvalues of the unitary matrix of the operator.

        Returns: Eigenvalues.

        """
    @property
    def basis(self) -> None:
        '''str or None: The basis of an operation, or for controlled gates, of the
        target operation. If not ``None``, should take a value of ``"X"``, ``"Y"``,
        or ``"Z"``.

        For example, ``X`` and ``CNOT`` have ``basis = "X"``, whereas
        ``ControlledPhaseShift`` and ``RZ`` have ``basis = "Z"``.
        '''
    @property
    def control_wires(self):
        """Control wires of the operator.

        For operations that are not controlled,
        this is an empty ``Wires`` object of length ``0``.

        Returns:
            Wires: The control wires of the operation.
        """
    def generator(self): ...
    def decompositions(self): ...
    def single_qubit_rot_angles(self) -> None:
        """The parameters required to implement a single-qubit gate as an
        equivalent ``Rot`` gate, up to a global phase.

        Returns:
            tuple[float, float, float]: A list of values :math:`[\\phi, \\theta, \\omega]`
            such that :math:`RZ(\\omega) RY(\\theta) RZ(\\phi)` is equivalent to the
            original operation.
        """
    def set_wires(self, wires) -> None:
        """Set which qubits the operator is applied to.

        Args:
            wires (Union[int, List[int]]): Qubits the operator is applied to.

        Returns: None.

        """
    def __call__(self, *args, **kwargs): ...
    def forward(self, params=None, q_machine: QMachine = None, wires=None):
        """Apply the operator to the quantum device states.
            
            :param params: Parameters of the operator or QTensor
            :param q_machine: Quantum Device that the
                operator is applied to.
            :param wires (Union[int, List[int]]): Qubits that the operator is
                applied to.

            return: None, the q_machine.states will be updated after this operation.
        """

class Observable(Operator, metaclass=ABCMeta):
    """Class for Observables.

    """
    def __init__(self, has_params: bool = False, trainable: bool = False, init_params=None, wires=None, dtype=..., use_dagger: bool = False, **kwargs) -> None:
        """Init function of the Observable class

        """
    def diagonalizing_gates(self) -> None:
        """The diagonalizing gates when perform measurements.

        Returns: None.

        """

class Encoder(Module):
    q_machine: Incomplete
    def __init__(self) -> None: ...
    def forward(self, x, q_machine) -> None: ...

class StateEncoder(Encoder, metaclass=ABCMeta):
    def __init__(self) -> None: ...
    def forward(self, x, q_machine) -> None: ...

class Operation(Operator, metaclass=ABCMeta):
    """_summary_"""
    def __init__(self, has_params: bool = False, trainable: bool = False, init_params=None, wires=None, dtype=..., use_dagger: bool = False, **kwargs) -> None: ...
    @property
    def eigvals(self):
        '''"The eigenvalues of the unitary matrix of the operator.

        Returns:
            QTensor: Eigenvalues.

        '''
    def init_params(self) -> None:
        """Initialize the parameters.

        Raises:
            NotImplementedError: The init param function is not implemented.
        """
    def build_params(self, trainable):
        """Build parameters.

        Args:
            trainable (bool): Whether the parameters are trainable.

        Returns:
            QTensor: Built parameters.
        """
    def reset_params(self, init_params=None) -> None:
        """Reset parameters with init_params value.

        If self.params is Parameter, it will copy value form init_params.
        If self.params is QTensor, it will set as refernece to init_params
        :param init_params or ndarray or float

        """

class DiagonalOperation(Operation, metaclass=ABCMeta):
    """Class for Diagonal Operation."""
    @property
    def eigvals(self):
        """The eigenvalues of the unitary matrix of the operator.

        Returns: Eigenvalues.

        """

def operation_derivative(op: Operation): ...
