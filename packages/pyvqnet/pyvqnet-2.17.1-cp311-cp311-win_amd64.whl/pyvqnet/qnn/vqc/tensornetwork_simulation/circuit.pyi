import tensornetwork as tn
from . import channels as channels, gates as gates
from .basecircuit import BaseCircuit as BaseCircuit
from .cons import backend as backend, contractor as contractor, dtypestr as dtypestr, npdtype as npdtype
from .quantum import QuOperator as QuOperator, identity as identity
from _typeshed import Incomplete
from typing import Any, Callable, Sequence

Gate = gates.Gate
Tensor = Any

class Circuit(BaseCircuit):
    """
    ``Circuit`` class.
    Simple usage demo below.

    .. code-block:: python

        c = tc.Circuit(3)
        c.H(1)
        c.CNOT(0, 1)
        c.RX(2, theta=tc.num_to_tensor(1.))
        c.expectation([tc.gates.z(), (2, )]) # 0.54

    """
    is_dm: bool
    inputs: Incomplete
    mps_inputs: Incomplete
    split: Incomplete
    circuit_param: Incomplete
    def __init__(self, nqubits: int, inputs: Tensor | None = None, mps_inputs: QuOperator | None = None, split: dict[str, Any] | None = None) -> None:
        """
        Circuit object based on state simulator.

        :param nqubits: The number of qubits in the circuit.
        :type nqubits: int
        :param inputs: If not None, the initial state of the circuit is taken as ``inputs``
            instead of :math:`\\vert 0\\rangle^n` qubits, defaults to None.
        :type inputs: Optional[Tensor], optional
        :param mps_inputs: QuVector for a MPS like initial wavefunction.
        :type mps_inputs: Optional[QuOperator]
        :param split: dict if two qubit gate is ready for split, including parameters for at least one of
            ``max_singular_values`` and ``max_truncation_err``.
        :type split: Optional[Dict[str, Any]]
        """
    def replace_mps_inputs(self, mps_inputs: QuOperator) -> None:
        """
        Replace the input state in MPS representation while keep the circuit structure unchanged.

        :Example:
        >>> c = tc.Circuit(2)
        >>> c.X(0)
        >>>
        >>> c2 = tc.Circuit(2, mps_inputs=c.quvector())
        >>> c2.X(0)
        >>> c2.wavefunction()
        array([1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j], dtype=complex64)
        >>>
        >>> c3 = tc.Circuit(2)
        >>> c3.X(0)
        >>> c3.replace_mps_inputs(c.quvector())
        >>> c3.wavefunction()
        array([1.+0.j, 0.+0.j, 0.+0.j, 0.+0.j], dtype=complex64)

        :param mps_inputs: (Nodes, dangling Edges) for a MPS like initial wavefunction.
        :type mps_inputs: Tuple[Sequence[Gate], Sequence[Edge]]
        """
    def mid_measurement(self, index: int, keep: int = 0) -> Tensor:
        """
        Middle measurement in z-basis on the circuit, note the wavefunction output is not normalized
        with ``mid_measurement`` involved, one should normalize the state manually if needed.
        This is a post-selection method as keep is provided as a prior.

        :param index: The index of qubit that the Z direction postselection applied on.
        :type index: int
        :param keep: 0 for spin up, 1 for spin down, defaults to be 0.
        :type keep: int, optional
        """
    mid_measure = mid_measurement
    post_select = mid_measurement
    post_selection = mid_measurement
    def depolarizing2(self, index: int, *, px: float, py: float, pz: float, status: float | None = None) -> float: ...
    def depolarizing_reference(self, index: int, *, px: float, py: float, pz: float, status: float | None = None) -> Tensor:
        """
        Apply depolarizing channel in a Monte Carlo way,
        i.e. for each call of this method, one of gates from
        X, Y, Z, I are applied on the circuit based on the probability
        indicated by ``px``, ``py``, ``pz``.

        :param index: The qubit that depolarizing channel is on
        :type index: int
        :param px: probability for X noise
        :type px: float
        :param py: probability for Y noise
        :type py: float
        :param pz: probability for Z noise
        :type pz: float
        :param status: random seed uniformly from 0 to 1, defaults to None (generated implicitly)
        :type status: Optional[float], optional
        :return: int Tensor, the element lookup: [0: x, 1: y, 2: z, 3: I]
        :rtype: Tensor
        """
    def unitary_kraus2(self, kraus: Sequence[Gate], *index: int, prob: Sequence[float] | None = None, status: float | None = None, name: str | None = None) -> Tensor: ...
    def unitary_kraus(self, kraus: Sequence[Gate], *index: int, prob: Sequence[float] | None = None, status: float | None = None, name: str | None = None) -> Tensor:
        """
        Apply unitary gates in ``kraus`` randomly based on corresponding ``prob``.
        If ``prob`` is ``None``, this is reduced to kraus channel language.

        :param kraus: List of ``tc.gates.Gate`` or just Tensors
        :type kraus: Sequence[Gate]
        :param prob: prob list with the same size as ``kraus``, defaults to None
        :type prob: Optional[Sequence[float]], optional
        :param status: random seed between 0 to 1, defaults to None
        :type status: Optional[float], optional
        :return: shape [] int dtype tensor indicates which kraus gate is actually applied
        :rtype: Tensor
        """
    def general_kraus(self, kraus: Sequence[Gate], *index: int, status: float | None = None, name: str | None = None) -> Tensor:
        """
        Monte Carlo trajectory simulation of general Kraus channel whose Kraus operators cannot be
        amplified to unitary operators. For unitary operators composed Kraus channel, :py:meth:`unitary_kraus`
        is much faster.

        This function is jittable in theory. But only jax+GPU combination is recommended for jit
        since the graph building time is too long for other backend options; though the running
        time of the function is very fast for every case.

        :param kraus: A list of ``tn.Node`` for Kraus operators.
        :type kraus: Sequence[Gate]
        :param index: The qubits index that Kraus channel is applied on.
        :type index: int
        :param status: Random tensor uniformly between 0 or 1, defaults to be None,
            when the random number will be generated automatically
        :type status: Optional[float], optional
        """
    apply_general_kraus = general_kraus
    @staticmethod
    def apply_general_kraus_delayed(krausf: Callable[..., Sequence[Gate]], is_unitary: bool = False) -> Callable[..., None]: ...
    def is_valid(self) -> bool:
        """
        [WIP], check whether the circuit is legal.

        :return: The bool indicating whether the circuit is legal
        :rtype: bool
        """
    def wavefunction(self, form: str = 'default') -> tn.Node.tensor:
        '''
        Compute the output wavefunction from the circuit.

        :param form: The str indicating the form of the output wavefunction.
            "default": [-1], "ket": [-1, 1], "bra": [1, -1]
        :type form: str, optional
        :return: Tensor with the corresponding shape.
        :rtype: Tensor
        '''
    state = wavefunction
    def get_quoperator(self) -> QuOperator:
        """
        Get the ``QuOperator`` MPO like representation of the circuit unitary without contraction.

        :return: ``QuOperator`` object for the circuit unitary (open indices for the input state)
        :rtype: QuOperator
        """
    quoperator = get_quoperator
    get_circuit_as_quoperator = get_quoperator
    get_state_as_quvector: Incomplete
    def matrix(self) -> Tensor:
        """
        Get the unitary matrix for the circuit irrespective with the circuit input state.

        :return: The circuit unitary matrix
        :rtype: Tensor
        """
    def measure_reference(self, *index: int, with_prob: bool = False) -> tuple[str, float]:
        """
        Take measurement on the given quantum lines by ``index``.

        :Example:

        >>> c = tc.Circuit(3)
        >>> c.H(0)
        >>> c.h(1)
        >>> c.toffoli(0, 1, 2)
        >>> c.measure(2)
        ('1', -1.0)
        >>> # Another possible output: ('0', -1.0)
        >>> c.measure(2, with_prob=True)
        ('1', (0.25000011920928955+0j))
        >>> # Another possible output: ('0', (0.7499998807907104+0j))

        :param index: Measure on which quantum line.
        :param with_prob: If true, theoretical probability is also returned.
        :return: The sample output and probability (optional) of the quantum line.
        :rtype: Tuple[str, float]
        """
    def expectation_multi_pauli(self, *ops: tuple[tn.Node, list[int]], reuse: bool = True, enable_lightcone: bool = False, noise_conf: Any | None = None, nmc: int = 1000, status: Tensor | None = None, **kws: Any) -> Tensor: ...
    def expectation(self, *ops: tuple[tn.Node, list[int]], reuse: bool = True, enable_lightcone: bool = False, noise_conf: Any | None = None, nmc: int = 1000, status: Tensor | None = None, **kws: Any) -> Tensor:
        '''
        Compute the expectation of corresponding operators.

        :Example:

        >>> c = tc.Circuit(2)
        >>> c.H(0)
        >>> c.expectation((tc.gates.z(), [0]))
        array(0.+0.j, dtype=complex64)

        >>> c = tc.Circuit(2)
        >>> c.cnot(0, 1)
        >>> c.rx(0, theta=0.4)
        >>> c.rx(1, theta=0.8)
        >>> c.h(0)
        >>> c.h(1)
        >>> error1 = tc.channels.generaldepolarizingchannel(0.1, 1)
        >>> error2 = tc.channels.generaldepolarizingchannel(0.06, 2)
        >>> noise_conf = NoiseConf()
        >>> noise_conf.add_noise("rx", error1)
        >>> noise_conf.add_noise("cnot", [error2], [[0, 1]])
        >>> c.expectation((tc.gates.x(), [0]), noise_conf=noise_conf, nmc=10000)
        (0.46274087-3.764033e-09j)

        :param ops: Operator and its position on the circuit,
            eg. ``(tc.gates.z(), [1, ]), (tc.gates.x(), [2, ])`` is for operator :math:`Z_1X_2`.
        :type ops: Tuple[tn.Node, List[int]]
        :param reuse: If True, then the wavefunction tensor is cached for further expectation evaluation,
            defaults to be true.
        :type reuse: bool, optional
        :param enable_lightcone: whether enable light cone simplification, defaults to False
        :type enable_lightcone: bool, optional
        :param noise_conf: Noise Configuration, defaults to None
        :type noise_conf: Optional[NoiseConf], optional
        :param nmc: repetition time for Monte Carlo sampling for noisfy calculation, defaults to 1000
        :type nmc: int, optional
        :param status: external randomness given by tensor uniformly from [0, 1], defaults to None,
            used for noisfy circuit sampling
        :type status: Optional[Tensor], optional
        :raises ValueError: "Cannot measure two operators in one index"
        :return: Tensor with one element
        :rtype: Tensor
        '''

def expectation(*ops: tuple[tn.Node, list[int]], ket: Tensor, bra: Tensor | None = None, conj: bool = True, normalization: bool = False) -> Tensor:
    '''
    Compute :math:`\\langle bra\\vert ops \\vert ket\\rangle`.

    Example 1 (:math:`bra` is same as :math:`ket`)

    >>> c = tc.Circuit(3)
    >>> c.H(0)
    >>> c.ry(1, theta=tc.num_to_tensor(0.8 + 0.7j))
    >>> c.cnot(1, 2)
    >>> state = c.wavefunction() # the state of this circuit
    >>> x1z2 = [(tc.gates.x(), [0]), (tc.gates.z(), [1])] # input qubits
    >>>
    >>> # Expection of this circuit / <state|*x1z2|state>
    >>> c.expectation(*x1z2)
    array(0.69670665+0.j, dtype=complex64)
    >>> tc.expectation(*x1z2, ket=state)
    (0.6967066526412964+0j)
    >>>
    >>> # Normalize(expection of Circuit) / Normalize(<state|*x1z2|state>)
    >>> c.expectation(*x1z2) / tc.backend.norm(state) ** 2
    (0.5550700389340034+0j)
    >>> tc.expectation(*x1z2, ket=state, normalization=True)
    (0.55507004+0j)

    Example 2 (:math:`bra` is different from :math:`ket`)

    >>> c = tc.Circuit(2)
    >>> c.X(1)
    >>> s1 = c.state()
    >>> c2 = tc.Circuit(2)
    >>> c2.X(0)
    >>> s2 = c2.state()
    >>> c3 = tc.Circuit(2)
    >>> c3.H(1)
    >>> s3 = c3.state()
    >>> x1x2 = [(tc.gates.x(), [0]), (tc.gates.x(), [1])]
    >>>
    >>> tc.expectation(*x1x2, ket=s1, bra=s2)
    (1+0j)
    >>> tc.expectation(*x1x2, ket=s3, bra=s2)
    (0.7071067690849304+0j) # 1/sqrt(2)

    :param ket: :math:`ket`. The state in tensor or ``QuVector`` format
    :type ket: Tensor
    :param bra: :math:`bra`, defaults to None, which is the same as ``ket``.
    :type bra: Optional[Tensor], optional
    :param conj: :math:`bra` changes to the adjoint matrix of :math:`bra`, defaults to True.
    :type conj: bool, optional
    :param normalization: Normalize the :math:`ket` and :math:`bra`, defaults to False.
    :type normalization: bool, optional
    :raises ValueError: "Cannot measure two operators in one index"
    :return: The result of :math:`\\langle bra\\vert ops \\vert ket\\rangle`.
    :rtype: Tensor
    '''
