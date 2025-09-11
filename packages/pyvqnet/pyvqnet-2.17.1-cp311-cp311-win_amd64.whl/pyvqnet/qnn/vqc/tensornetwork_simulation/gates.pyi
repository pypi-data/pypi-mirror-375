import tensornetwork as tn
from .backends import get_backend as get_backend
from .cons import backend as backend, dtypestr as dtypestr, npdtype as npdtype
from .utils import arg_alias as arg_alias
from _typeshed import Incomplete
from typing import Any, Callable, Sequence

thismodule: Incomplete
Tensor = Any
Array = Any
Operator = Any
zero_state: Incomplete
one_state: Incomplete
plus_state: Incomplete
minus_state: Incomplete

def __rmul__(self, lvalue: float | complex) -> Gate: ...

class Gate(tn.Node):
    """
    Wrapper of tn.Node, quantum gate
    """
    def copy(self, conjugate: bool = False) -> Gate: ...

def num_to_tensor(*num: float | Tensor, dtype: str | None = None) -> Any:
    """
    Convert the inputs to Tensor with specified dtype.

    :Example:

    >>> from tensorcircuit.gates import num_to_tensor
    >>> # OR
    >>> from tensorcircuit.gates import array_to_tensor
    >>>
    >>> x, y, z = 0, 0.1, np.array([1])
    >>>
    >>> tc.set_backend('numpy')
    numpy_backend
    >>> num_to_tensor(x, y, z)
    [array(0.+0.j, dtype=complex64), array(0.1+0.j, dtype=complex64), array([1.+0.j], dtype=complex64)]
    >>>
    >>> tc.set_backend('tensorflow')
    tensorflow_backend
    >>> num_to_tensor(x, y, z)
    [<tf.Tensor: shape=(), dtype=complex64, numpy=0j>,
     <tf.Tensor: shape=(), dtype=complex64, numpy=(0.1+0j)>,
     <tf.Tensor: shape=(1,), dtype=complex64, numpy=array([1.+0.j], dtype=complex64)>]
    >>>
    >>> tc.set_backend('pytorch')
    pytorch_backend
    >>> num_to_tensor(x, y, z)
    [tensor(0.+0.j), tensor(0.1000+0.j), tensor([1.+0.j])]
    >>>
    >>> tc.set_backend('jax')
    jax_backend
    >>> num_to_tensor(x, y, z)
    [DeviceArray(0.+0.j, dtype=complex64),
     DeviceArray(0.1+0.j, dtype=complex64),
     DeviceArray([1.+0.j], dtype=complex64)]

    :param num: inputs
    :type num: Union[float, Tensor]
    :param dtype: dtype of the output Tensors
    :type dtype: str, optional
    :return: List of Tensors
    :rtype: List[Tensor]
    """
array_to_tensor = num_to_tensor

def gate_wrapper(m: Tensor, n: str | None = None) -> Gate: ...

class GateF:
    m: Incomplete
    n: Incomplete
    ctrl: Incomplete
    def __init__(self, m: Tensor, n: str | None = None, ctrl: list[int] | None = None) -> None: ...
    def __call__(self, *args: Any, **kws: Any) -> Gate: ...
    def adjoint(self) -> GateF: ...
    def ided(self, before: bool = True) -> GateF: ...
    def controlled(self) -> GateF: ...
    def ocontrolled(self) -> GateF: ...

class GateVF(GateF):
    f: Incomplete
    n: Incomplete
    ctrl: Incomplete
    def __init__(self, f: Callable[..., Gate], n: str | None = None, ctrl: list[int] | None = None) -> None: ...
    def __call__(self, *args: Any, **kws: Any) -> Gate: ...
    def adjoint(self) -> GateVF: ...

def meta_gate() -> None:
    """
    Inner helper function to generate gate functions, such as ``z()`` from ``_z_matrix``
    """
def matrix_for_gate(gate: Gate, tol: float = 1e-06) -> Tensor:
    """
    Convert Gate to numpy array.

    :Example:

    >>> gate = tc.gates.r_gate()
    >>> tc.gates.matrix_for_gate(gate)
        array([[1.+0.j, 0.+0.j],
            [0.+0.j, 1.+0.j]], dtype=complex64)

    :param gate: input Gate
    :type gate: Gate
    :return: Corresponding Tensor
    :rtype: Tensor
    """
def bmatrix(a: Array) -> str:
    '''
    Returns a :math:`\\LaTeX` bmatrix.

    :Example:

    >>> gate = tc.gates.r_gate()
    >>> array = tc.gates.matrix_for_gate(gate)
    >>> array
    array([[1.+0.j, 0.+0.j],
        [0.+0.j, 1.+0.j]], dtype=complex64)
    >>> print(tc.gates.bmatrix(array))
    \\begin{bmatrix}    1.+0.j & 0.+0.j\\\\    0.+0.j & 1.+0.j \\end{bmatrix}

    Formatted Display:

    .. math::
        \\begin{bmatrix}    1.+0.j & 0.+0.j\\\\    0.+0.j & 1.+0.j \\end{bmatrix}

    :param a: 2D numpy array
    :type a: np.array
    :raises ValueError: ValueError("bmatrix can at most display two dimensions")
    :return: :math:`\\LaTeX`-formatted string for bmatrix of the array a
    :rtype: str
    '''
def phase_gate(theta: int = 0) -> Gate:
    """
    The phase gate

    .. math::
        \\textrm{phase}(\\theta) =
        \\begin{pmatrix}
            1 & 0 \\\\\n            0 & e^{i\\theta} \\\\\n        \\end{pmatrix}

    :param theta: angle in radians, defaults to 0
    :type theta: float, optional
    :return: phase gate
    :rtype: Gate
    """
def get_u_parameter(m: Tensor) -> tuple[float, float, float]:
    """
    From the single qubit unitary to infer three angles of IBMUgate,

    :param m: numpy array, no backend agnostic version for now
    :type m: Tensor
    :return: theta, phi, lbd
    :rtype: Tuple[Tensor, Tensor, Tensor]
    """
def u_gate(theta: int = 0, phi: int = 0, lbd: int = 0) -> Gate:
    """
    IBMQ U gate following the converntion of OpenQASM3.0.
    See `OpenQASM doc <https://openqasm.com/language/gates.html#built-in-gates>`_

    .. math::

        \\begin{split}U(\\theta,\\phi,\\lambda) := \\left(\\begin{array}{cc}
        \\cos(\\theta/2) & -e^{i\\lambda}\\sin(\\theta/2) \\\\\n        e^{i\\phi}\\sin(\\theta/2) & e^{i(\\phi+\\lambda)}\\cos(\\theta/2) \\end{array}\\right).\\end{split}

    :param theta: _description_, defaults to 0
    :type theta: float, optional
    :param phi: _description_, defaults to 0
    :type phi: float, optional
    :param lbd: _description_, defaults to 0
    :type lbd: float, optional
    :return: _description_
    :rtype: Gate
    """
def rot_gate(theta: int = 0, phi: int = 0, lbd: int = 0) -> Gate: ...
def r_gate(theta: int = 0, alpha: int = 0, phi: int = 0) -> Gate:
    """
    General single qubit rotation gate

    .. math::
        R(\\theta, \\alpha, \\phi) = j \\cos(\\theta) I
        - j \\cos(\\phi) \\sin(\\alpha) \\sin(\\theta) X
        - j \\sin(\\phi) \\sin(\\alpha) \\sin(\\theta) Y
        - j \\sin(\\theta) \\cos(\\alpha) Z

    :param theta:  angle in radians
    :type theta: float, optional
    :param alpha: angle in radians
    :type alpha: float, optional
    :param phi: angle in radians
    :type phi: float, optional

    :return: R Gate
    :rtype: Gate
    """
def rx_gate(theta: int = 0) -> Gate:
    """
    Rotation gate along :math:`x` axis.

    .. math::
        RX(\\theta) = e^{-j\\frac{\\theta}{2}X}

    :param theta: angle in radians
    :type theta: float, optional
    :return: RX Gate
    :rtype: Gate
    """
def ry_gate(theta: int = 0) -> Gate:
    """
    Rotation gate along :math:`y` axis.

    .. math::
        RY(\\theta) = e^{-j\\frac{\\theta}{2}Y}

    :param theta: angle in radians
    :type theta: float, optional
    :return: RY Gate
    :rtype: Gate
    """
def rz_gate(theta: int = 0) -> Gate:
    """
    Rotation gate along :math:`z` axis.

    .. math::
        RZ(\\theta) = e^{-j\\frac{\\theta}{2}Z}

    :param theta: angle in radians
    :type theta: float, optional
    :return: RZ Gate
    :rtype: Gate
    """
def rgate_theoretical(theta: int = 0, alpha: float = 0, phi: float = 0) -> Gate:
    """
    Rotation gate implemented by matrix exponential. The output is the same as `rgate`.

    .. math::
        R(\\theta, \\alpha, \\phi) = e^{-j \\theta \\left[\\sin(\\alpha) \\cos(\\phi) X
                                                   + \\sin(\\alpha) \\sin(\\phi) Y
                                                   + \\cos(\\alpha) Z\\right]}

    :param theta: angle in radians
    :type theta: float, optional
    :param alpha: angle in radians
    :type alpha: float, optional
    :param phi: angle in radians
    :type phi: float, optional
    :return: Rotation Gate
    :rtype: Gate
    """
def random_single_qubit_gate() -> Gate:
    """
    Random single qubit gate described in https://arxiv.org/abs/2002.07730.

    :return: A random single-qubit gate
    :rtype: Gate
    """
def iswap_gate(theta: float = 1.0) -> Gate:
    """
    iSwap gate.

    .. math::
        \\textrm{iSwap}(\\theta) =
        \\begin{pmatrix}
            1 & 0 & 0 & 0\\\\\n            0 & \\cos(\\frac{\\pi}{2} \\theta ) & j \\sin(\\frac{\\pi}{2} \\theta ) & 0\\\\\n            0 & j \\sin(\\frac{\\pi}{2} \\theta ) & \\cos(\\frac{\\pi}{2} \\theta ) & 0\\\\\n            0 & 0 & 0 & 1\\\\\n        \\end{pmatrix}

    :param theta: angle in radians
    :type theta: float
    :return: iSwap Gate
    :rtype: Gate
    """
def cr_gate(theta: int = 0, alpha: float = 0, phi: float = 0) -> Gate:
    """
    Controlled rotation gate. When the control qubit is 1, `rgate` is applied to the target qubit.

    :param theta:  angle in radians
    :type theta: float, optional
    :param alpha: angle in radians
    :type alpha: float, optional
    :param phi: angle in radians
    :type phi: float, optional

    :return: CR Gate
    :rtype: Gate
    """
def any_gate(unitary: Tensor, name: str = 'any') -> Gate:
    """
    Note one should provide the gate with properly reshaped.

    :param unitary: corresponding gate
    :type unitary: Tensor
    :param name: The name of the gate.
    :type name: str
    :return: the resulted gate
    :rtype: Gate
    """
def exponential_gate(unitary: Tensor, theta: float, name: str = 'none') -> Gate:
    """
    Exponential gate.

    .. math::
        \\textrm{exp}(U) = e^{-j \\theta U}

    :param unitary: input unitary :math:`U`
    :type unitary: Tensor
    :param theta: angle in radians
    :type theta: float
    :param name: suffix of Gate name
    :return: Exponential Gate
    :rtype: Gate
    """
exp_gate = exponential_gate

def exponential_gate_unity(unitary: Tensor, theta, half: bool = False, name: str = 'none') -> Gate:
    """
    Faster exponential gate directly implemented based on RHS. Only works when :math:`U^2 = I` is an identity matrix.

    .. math::
        \\textrm{exp}(U) &= e^{-j \\theta U} \\\\\n                &= \\cos(\\theta) I - j \\sin(\\theta) U \\\\\n
    :param unitary: input unitary :math:`U`
    :type unitary: Tensor
    :param theta: angle in radians
    :type theta: float
    :param half: if True, the angel theta is mutiplied by 1/2,
        defaults to False
    :type half: bool
    :param name: suffix of Gate name
    :type name: str, optional
    :return: Exponential Gate
    :rtype: Gate
    """
exp1_gate = exponential_gate_unity
rzz_gate: Incomplete
rxx_gate: Incomplete
ryy_gate: Incomplete
rzx_gate: Incomplete
isingxx_gate = rxx_gate
isingyy_gate = ryy_gate
isingzz_gate = rzz_gate

def isingxy_gate(theta: int = 0) -> Gate: ...
def multirz_gate(theta: int = 0) -> Gate: ...
def singleexcitation_gate(theta: int = 0) -> Gate: ...
def crot_gate(theta: int = 0, phi: int = 0, lbd: int = 0) -> Gate: ...
def czz_gate(theta: int = 0, phi: int = 0, lbd: int = 0) -> Gate: ...
def multicontrol_gate(unitary: Tensor, ctrl: int | Sequence[int] = 1) -> Operator:
    """
    Multicontrol gate. If the control qubits equal to ``ctrl``, :math:`U` is applied to the target qubits.

    E.g., ``multicontrol_gate(tc.gates._zz_matrix, [1, 0, 1])`` returns a gate of 5 qubits,
        where the last 2 qubits are applied :math:`ZZ` gate,
        if the first 3 qubits are :math:`\\ket{101}`.

    :param unitary: input unitary :math:`U`
    :type unitary: Tensor
    :param ctrl: control bit sequence
    :type ctrl: Union[int, Sequence[int]]
    :return: Multicontrol Gate
    :rtype: Operator
    """
def mpo_gate(mpo: Operator, name: str = 'mpo') -> Operator: ...
def meta_vgate() -> None: ...
