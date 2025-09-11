from . import cons as cons, gates as gates, interfaces as interfaces
from .cons import backend as backend, dtypestr as dtypestr
from .gates import array_to_tensor as array_to_tensor
from _typeshed import Incomplete
from typing import Any, Sequence

thismodule: Incomplete
Gate = gates.Gate
Tensor = Any
Matrix = Any

class KrausList(list):
    name: Incomplete
    is_unitary: Incomplete
    def __init__(self, iterable, name, is_unitary) -> None: ...

def depolarizingchannel(px: float, py: float, pz: float) -> Sequence[Gate]:
    """
    Return a Depolarizing Channel

    .. math::
        \\sqrt{1-p_x-p_y-p_z}
        \\begin{bmatrix}
            1 & 0\\\\\n            0 & 1\\\\\n        \\end{bmatrix}\\qquad
        \\sqrt{p_x}
        \\begin{bmatrix}
            0 & 1\\\\\n            1 & 0\\\\\n        \\end{bmatrix}\\qquad
        \\sqrt{p_y}
        \\begin{bmatrix}
            0 & -1j\\\\\n            1j & 0\\\\\n        \\end{bmatrix}\\qquad
        \\sqrt{p_z}
        \\begin{bmatrix}
            1 & 0\\\\\n            0 & -1\\\\\n        \\end{bmatrix}

    :Example:

    >>> cs = depolarizingchannel(0.1, 0.15, 0.2)
    >>> tc.channels.single_qubit_kraus_identity_check(cs)

    :param px: :math:`p_x`
    :type px: float
    :param py: :math:`p_y`
    :type py: float
    :param pz: :math:`p_z`
    :type pz: float
    :return: Sequences of Gates
    :rtype: Sequence[Gate]
    """
def generaldepolarizingchannel(p: float | Sequence[Any], num_qubits: int = 1) -> Sequence[Gate]:
    """
    Return a Depolarizing Channel for 1 qubit or 2 qubits

    :Example:

    >>> cs = tc.channels.generaldepolarizingchannel([0.1,0.1,0.1],1)
    >>> tc.channels.kraus_identity_check(cs)
    >>> cs = tc.channels.generaldepolarizingchannel(0.02,2)
    >>> tc.channels.kraus_identity_check(cs)


    :param p: parameter for each Pauli channel
    :type p: Union[float, Sequence]
    :param num_qubits: number of qubits, 1 and 2 are avaliable, defaults 1
    :type num_qubits: int, optional
    :return: Sequences of Gates
    :rtype: Sequence[Gate]
    """
def amplitudedampingchannel(gamma: float, p: float) -> Sequence[Gate]:
    """
    Return an amplitude damping channel.
    Notice: Amplitude damping corrspondings to p = 1.

    .. math::
        \\sqrt{p}
        \\begin{bmatrix}
            1 & 0\\\\\n            0 & \\sqrt{1-\\gamma}\\\\\n        \\end{bmatrix}\\qquad
        \\sqrt{p}
        \\begin{bmatrix}
            0 & \\sqrt{\\gamma}\\\\\n            0 & 0\\\\\n        \\end{bmatrix}\\qquad
        \\sqrt{1-p}
        \\begin{bmatrix}
            \\sqrt{1-\\gamma} & 0\\\\\n            0 & 1\\\\\n        \\end{bmatrix}\\qquad
        \\sqrt{1-p}
        \\begin{bmatrix}
            0 & 0\\\\\n            \\sqrt{\\gamma} & 0\\\\\n        \\end{bmatrix}

    :Example:

    >>> cs = amplitudedampingchannel(0.25, 0.3)
    >>> tc.channels.single_qubit_kraus_identity_check(cs)

    :param gamma: the damping parameter of amplitude (:math:`\\gamma`)
    :type gamma: float
    :param p: :math:`p`
    :type p: float
    :return: An amplitude damping channel with given :math:`\\gamma` and :math:`p`
    :rtype: Sequence[Gate]
    """
def resetchannel() -> Sequence[Gate]:
    """
    Reset channel

    .. math::
        \\begin{bmatrix}
            1 & 0\\\\\n            0 & 0\\\\\n        \\end{bmatrix}\\qquad
        \\begin{bmatrix}
            0 & 1\\\\\n            0 & 0\\\\\n        \\end{bmatrix}

    :Example:

    >>> cs = resetchannel()
    >>> tc.channels.single_qubit_kraus_identity_check(cs)

    :return: Reset channel
    :rtype: Sequence[Gate]
    """
def phasedampingchannel(gamma: float) -> Sequence[Gate]:
    """
    Return a phase damping channel with given :math:`\\gamma`

    .. math::
        \\begin{bmatrix}
            1 & 0\\\\\n            0 & \\sqrt{1-\\gamma}\\\\\n        \\end{bmatrix}\\qquad
        \\begin{bmatrix}
            0 & 0\\\\\n            0 & \\sqrt{\\gamma}\\\\\n        \\end{bmatrix}

    :Example:

    >>> cs = phasedampingchannel(0.6)
    >>> tc.channels.single_qubit_kraus_identity_check(cs)

    :param gamma: The damping parameter of phase (:math:`\\gamma`)
    :type gamma: float
    :return: A phase damping channel with given :math:`\\gamma`
    :rtype: Sequence[Gate]
    """
def thermalrelaxationchannel(t1: float, t2: float, time: float, method: str = 'ByChoi', excitedstatepopulation: float = 0.0) -> Sequence[Gate]:
    '''
    Return a thermal_relaxation_channel


    :Example:

    >>> cs = thermalrelaxationchannel(100,200,100,"AUTO",0.1)
    >>> tc.channels.single_qubit_kraus_identity_check(cs)

    :param t1: the T1 relaxation time.
    :type t1: float
    :param t2: the T2 dephasing time.
    :type t2: float
    :param time: gate time
    :type time: float
    :param method: method to express error (default: "ByChoi"). When :math:`T1>T2`, choose method "ByKraus"
        or "ByChoi" for jit. When :math:`T1<T2`,choose method "ByChoi" for jit. Users can also set method
        as "AUTO" and never mind the relative magnitude of :math:`T1,T2`, which is not jitable.
    :type time: str
    :param excitedstatepopulation: the population of  state :math:`|1\\rangle` at equilibrium (default: 0)
    :type excited_state_population: float, optional
    :return: A thermal_relaxation_channel
    :rtype: Sequence[Gate]
    '''

channels: Incomplete

def kraus_identity_check(kraus: Sequence[Gate]) -> None:
    """
    Check identity of Kraus operators.

    .. math::
        \\sum_{k}^{} K_k^{\\dagger} K_k = I


    :Examples:

    >>> cs = resetchannel()
    >>> tc.channels.kraus_identity_check(cs)

    :param kraus: List of Kraus operators.
    :type kraus: Sequence[Gate]
    """
single_qubit_kraus_identity_check = kraus_identity_check

def kraus_to_super_gate(kraus_list: Sequence[Gate]) -> Tensor:
    """
    Convert Kraus operators to one Tensor (as one Super Gate).

    .. math::
        \\sum_{k}^{} K_k \\otimes K_k^{*}

    :param kraus_list: A sequence of Gate
    :type kraus_list: Sequence[Gate]
    :return: The corresponding Tensor of the list of Kraus operators
    :rtype: Tensor
    """
def kraus_to_super(kraus_list: Sequence[Matrix]) -> Matrix:
    """
    Convert Kraus operator representation to Louivile-Superoperator representation.

    In the col-vec basis, the evolution of a state :math:`\\rho` in terms of tensor components
    of superoperator :math:`\\varepsilon` can be expressed as

    .. math::
        \\rho'_{mn} = \\sum_{\\mu \\nu}^{} \\varepsilon_{nm,\\nu \\mu} \\rho_{\\mu \\nu}

    The superoperator :math:`\\varepsilon` must make the dynamic map from :math:`\\rho` to :math:`\\rho'` to
    satisfy hermitian-perserving (HP), trace-preserving (TP), and completely positive (CP).

    We can construct the superoperator from Kraus operators by

    .. math::
        \\varepsilon = \\sum_{k} K_k^{*} \\otimes K_k


    :Examples:

    >>> kraus = resetchannel()
    >>> tc.channels.kraus_to_super(kraus)

    :param kraus_list: A sequence of Gate
    :type kraus_list: Sequence[Gate]
    :return: The corresponding Tensor of Superoperator
    :rtype: Matrix
    """
def super_to_choi(superop: Matrix) -> Matrix:
    """
    Convert Louivile-Superoperator representation to Choi representation.

    In the col-vec basis, the evolution of a state :math:`\\rho` in terms of Choi
    matrix :math:`\\Lambda` can be expressed as

    .. math::
        \\rho'_{mn} = \\sum_{\\mu,\\nu}^{} \\Lambda_{\\mu m,\\nu n} \\rho_{\\mu \\nu}

    The Choi matrix :math:`\\Lambda` must make the dynamic map from :math:`\\rho` to :math:`\\rho'` to
    satisfy hermitian-perserving (HP), trace-preserving (TP), and completely positive (CP).

    Interms of tensor components we have the relationship of Louivile-Superoperator representation
    and Choi representation

    .. math::
        \\Lambda_{mn,\\mu \\nu} = \\varepsilon_{\\nu n,\\mu m}


    :Examples:

    >>> kraus = resetchannel()
    >>> superop = tc.channels.kraus_to_super(kraus)
    >>> tc.channels.super_to_choi(superop)


    :param superop: Superoperator
    :type superop: Matrix
    :return: Choi matrix
    :rtype: Matrix
    """
def reshuffle(op: Matrix, order: Sequence[int]) -> Matrix:
    """
    Reshuffle the dimension index of a matrix.

    :param op: Input matrix
    :type op: Matrix
    :param order: required order
    :type order: Tuple
    :return: Reshuffled matrix
    :rtype: Matrix
    """
def choi_to_kraus(choi: Matrix, truncation_rules: dict[str, Any] | None = None) -> Matrix:
    '''
    Convert the Choi matrix representation to Kraus operator representation.

    This can be done by firstly geting eigen-decomposition of Choi-matrix

    .. math::
        \\Lambda = \\sum_k \\gamma_k  \\vert \\phi_k \\rangle \\langle \\phi_k \\vert

    Then define Kraus operators

    .. math::
        K_k = \\sqrt{\\gamma_k} V_k

    where :math:`\\gamma_k\\geq0` and :math:`\\phi_k` is the col-val vectorization of :math:`V_k` .


    :Examples:


    >>> kraus = tc.channels.phasedampingchannel(0.2)
    >>> superop = tc.channels.kraus_to_choi(kraus)
    >>> kraus_new = tc.channels.choi_to_kraus(superop, truncation_rules={"max_singular_values":3})


    :param choi: Choi matrix
    :type choi: Matrix
    :param truncation_rules: A dictionary to restrict the calculation of kraus matrices. The restriction
        can be the number of kraus terms, which is jitable. It can also be the truncattion error, which is not jitable.
    :type truncation_rules: Dictionary
    :return: A list of Kraus operators
    :rtype: Sequence[Matrix]
    '''
def kraus_to_choi(kraus_list: Sequence[Matrix]) -> Matrix:
    """
    Convert from Kraus representation to Choi representation.

    :param kraus_list: A list Kraus operators
    :type kraus_list: Sequence[Matrix]
    :return: Choi matrix
    :rtype: Matrix
    """
def choi_to_super(choi: Matrix) -> Matrix:
    """
    Convert from Choi representation to Superoperator representation.

    :param choi: Choi matrix
    :type choi: Matrix
    :return: Superoperator
    :rtype: Matrix
    """
def super_to_kraus(superop: Matrix) -> Matrix:
    """
    Convert from Superoperator representation to Kraus representation.

    :param superop: Superoperator
    :type superop: Matrix
    :return: A list of Kraus operator
    :rtype: Matrix
    """
def is_hermitian_matrix(mat: Matrix, rtol: float = 1e-08, atol: float = 1e-05):
    """
    Test if an array is a Hermitian matrix

    :param mat: Matrix
    :type mat: Matrix
    :param rtol: _description_, defaults to 1e-8
    :type rtol: float, optional
    :param atol: _description_, defaults to 1e-5
    :type atol: float, optional
    :return: _description_
    :rtype: _type_
    """
def krausgate_to_krausmatrix(kraus_list: Sequence[Gate]) -> Sequence[Matrix]:
    """
    Convert Kraus of Gate form to Matrix form.

    :param kraus_list: A list of Kraus
    :type kraus_list: Sequence[Gate]
    :return: A list of Kraus operators
    :rtype: Sequence[Matrix]
    """
def krausmatrix_to_krausgate(kraus_list: Sequence[Matrix]) -> Sequence[Gate]:
    """
    Convert Kraus of Matrix form to Gate form.

    :param kraus_list: A list of Kraus
    :type kraus_list: Sequence[Matrix]
    :return: A list of Kraus operators
    :rtype: Sequence[Gate]
    """
def evol_kraus(density_matrix: Matrix, kraus_list: Sequence[Matrix]) -> Matrix:
    """
    The dynamic evolution according to Kraus operators.

    .. math::
        \\rho' = \\sum_{k} K_k \\rho K_k^{\\dagger}

    :Examples:

    >>> density_matrix = np.array([[0.5,0.5],[0.5,0.5]])
    >>> kraus = tc.channels.phasedampingchannel(0.2)
    >>> evol_kraus(density_matrix,kraus)


    :param density_matrix: Initial density matrix
    :type density_matrix: Matrix
    :param kraus_list: A list of Kraus operator
    :type kraus_list: Sequence[Matrix]
    :return: Final density matrix
    :rtype: Matrix
    """
def evol_superop(density_matrix: Matrix, superop: Matrix) -> Matrix:
    """
    The dynamic evolution according to Superoperator.

    :Examples:

    >>> density_matrix = np.array([[0.5,0.5],[0.5,0.5]])
    >>> kraus = tc.channels.phasedampingchannel(0.2)
    >>> superop = kraus_to_super(kraus)
    >>> evol_superop(density_matrix,superop)


    :param density_matrix: Initial density matrix
    :type density_matrix: Matrix
    :param superop: Superoperator
    :type superop: Sequence[Matrix]
    :return: Final density matrix
    :rtype: Matrix
    """
def check_rep_transformation(kraus: Sequence[Gate], density_matrix: Matrix, verbose: bool = False):
    """
    Check the convertation between those representations.

    :param kraus: A sequence of Gate
    :type kraus: Sequence[Gate]
    :param density_matrix: Initial density matrix
    :type density_matrix: Matrix
    :param verbose: Whether print Kraus and new Kraus operators, defaults to False
    :type verbose: bool, optional
    """
def composedkraus(kraus1: KrausList, kraus2: KrausList) -> KrausList:
    """
    Compose the noise channels

    :param kraus1: One noise channel
    :type kraus1: KrausList
    :param kraus2: Another noise channel
    :type kraus2: KrausList
    :return: Composed nosie channel
    :rtype: KrausList
    """
