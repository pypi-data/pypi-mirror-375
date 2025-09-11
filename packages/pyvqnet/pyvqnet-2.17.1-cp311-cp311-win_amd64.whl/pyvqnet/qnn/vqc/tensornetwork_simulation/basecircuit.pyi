import tensornetwork as tn
from . import gates as gates
from .abstractcircuit import AbstractCircuit as AbstractCircuit
from .cons import backend as backend, contractor as contractor, dtypestr as dtypestr, npdtype as npdtype, rdtypestr as rdtypestr
from .quantum import QuOperator as QuOperator, QuVector as QuVector, correlation_from_counts as correlation_from_counts, correlation_from_samples as correlation_from_samples, measurement_counts as measurement_counts, sample2all as sample2all, sample_bin2int as sample_bin2int, sample_int2bin as sample_int2bin
from .utils import arg_alias as arg_alias
from _typeshed import Incomplete
from typing import Any, Sequence

Gate = gates.Gate
Tensor = Any

class BaseCircuit(AbstractCircuit):
    is_dm: bool
    split: dict[str, Any] | None
    is_mps: bool
    @staticmethod
    def all_zero_nodes(n: int, d: int = 2, prefix: str = 'qb-') -> list[tn.Node]: ...
    @staticmethod
    def front_from_nodes(nodes: list[tn.Node]) -> list[tn.Edge]: ...
    @staticmethod
    def coloring_nodes(nodes: Sequence[tn.Node], is_dagger: bool = False, flag: str = 'inputs') -> None: ...
    @staticmethod
    def coloring_copied_nodes(nodes: Sequence[tn.Node], nodes0: Sequence[tn.Node], is_dagger: bool = True, flag: str = 'inputs') -> None: ...
    @staticmethod
    def copy(nodes: Sequence[tn.Node], dangling: Sequence[tn.Edge] | None = None, conj: bool | None = False) -> tuple[list[tn.Node], list[tn.Edge]]:
        """
        copy all nodes and dangling edges correspondingly

        :return:
        """
    state_tensor: Incomplete
    def apply_general_gate(self, gate: Gate | QuOperator, *index: int, name: str | None = None, split: dict[str, Any] | None = None, mpo: bool = False, ir_dict: dict[str, Any] | None = None) -> None: ...
    apply = apply_general_gate
    def expectation_before(self, *ops: tuple[tn.Node, list[int]], reuse: bool = True, **kws: Any) -> list[tn.Node]:
        """
        Get the tensor network in the form of a list of nodes
        for the expectation calculation before the real contraction

        :param reuse: _description_, defaults to True
        :type reuse: bool, optional
        :raises ValueError: _description_
        :return: _description_
        :rtype: List[tn.Node]
        """
    def to_qir(self) -> list[dict[str, Any]]:
        """
        Return the quantum intermediate representation of the circuit.

        :Example:

        .. code-block:: python

            >>> c = tc.Circuit(2)
            >>> c.CNOT(0, 1)
            >>> c.to_qir()
            [{'gatef': cnot, 'gate': Gate(
                name: 'cnot',
                tensor:
                    array([[[[1.+0.j, 0.+0.j],
                            [0.+0.j, 0.+0.j]],

                            [[0.+0.j, 1.+0.j],
                            [0.+0.j, 0.+0.j]]],


                        [[[0.+0.j, 0.+0.j],
                            [0.+0.j, 1.+0.j]],

                            [[0.+0.j, 0.+0.j],
                            [1.+0.j, 0.+0.j]]]], dtype=complex64),
                edges: [
                    Edge(Dangling Edge)[0],
                    Edge(Dangling Edge)[1],
                    Edge('cnot'[2] -> 'qb-1'[0] ),
                    Edge('cnot'[3] -> 'qb-2'[0] )
                ]), 'index': (0, 1), 'name': 'cnot', 'split': None, 'mpo': False}]

        :return: The quantum intermediate representation of the circuit.
        :rtype: List[Dict[str, Any]]
        """
    def perfect_sampling(self, status: Tensor | None = None) -> tuple[str, float]:
        """
        Sampling bistrings from the circuit output based on quantum amplitudes.
        Reference: arXiv:1201.3974.

        :param status: external randomness, with shape [nqubits], defaults to None
        :type status: Optional[Tensor]
        :return: Sampled bit string and the corresponding theoretical probability.
        :rtype: Tuple[str, float]
        """
    def measure_jit(self, *index: int, with_prob: bool = False, status: Tensor | None = None):
        """
        Take measurement to the given quantum lines.
        This method is jittable is and about 100 times faster than unjit version!

        :param index: Measure on which quantum line.
        :type index: int
        :param with_prob: If true, theoretical probability is also returned.
        :type with_prob: bool, optional
        :param status: external randomness, with shape [index], defaults to None
        :type status: Optional[Tensor]
        :return: The sample output and probability (optional) of the quantum line.
        :rtype: Tuple[Tensor, Tensor]
        """
    measure = measure_jit
    def amplitude(self, l: str | Tensor) -> Tensor:
        '''
        Returns the amplitude of the circuit given the bitstring l.
        For state simulator, it computes :math:`\\langle l\\vert \\psi\\rangle`,
        for density matrix simulator, it computes :math:`Tr(\\rho \\vert l\\rangle \\langle 1\\vert)`
        Note how these two are different up to a square operation.

        :Example:

        >>> c = tc.Circuit(2)
        >>> c.X(0)
        >>> c.amplitude("10")
        array(1.+0.j, dtype=complex64)
        >>> c.CNOT(0, 1)
        >>> c.amplitude("11")
        array(1.+0.j, dtype=complex64)

        :param l: The bitstring of 0 and 1s.
        :type l: Union[str, Tensor]
        :return: The amplitude of the circuit.
        :rtype: tn.Node.tensor
        '''
    def probability(self) -> Tensor:
        """
        get the 2^n length probability vector over computational basis

        :return: probability vector
        :rtype: Tensor
        """
    def sample(self, batch: int | None = None, allow_state: bool = False, readout_error: Sequence[Any] | None = None, format: str | None = None, random_generator: Any | None = None, status: Tensor | None = None) -> Any:
        """
        batched sampling from state or circuit tensor network directly

        :param batch: number of samples, defaults to None
        :type batch: Optional[int], optional
        :param allow_state: if true, we sample from the final state
            if memory allows, True is preferred, defaults to False
        :type allow_state: bool, optional
        :param readout_error: readout_error, defaults to None
        :type readout_error: Optional[Sequence[Any]]. Tensor, List, Tuple
        :param format: sample format, defaults to None as backward compatibility
            check the doc in :py:meth:`tensorcircuit.quantum.measurement_results`
        :type format: Optional[str]
        :param random_generator: random generator,  defaults to None
        :type random_generator: Optional[Any], optional
        :param status: external randomness given by tensor uniformly from [0, 1],
            if set, can overwrite random_generator
        :type status: Optional[Tensor]
        :return: List (if batch) of tuple (binary configuration tensor and corresponding probability)
            if the format is None, and consistent with format when given
        :rtype: Any
        """
    def sample_expectation_ps(self, x: Sequence[int] | None = None, y: Sequence[int] | None = None, z: Sequence[int] | None = None, shots: int | None = None, random_generator: Any | None = None, status: Tensor | None = None, readout_error: Sequence[Any] | None = None, noise_conf: Any | None = None, nmc: int = 1000, statusc: Tensor | None = None, **kws: Any) -> Tensor:
        '''
        Compute the expectation with given Pauli string with measurement shots numbers

        :Example:

        >>> c = tc.Circuit(2)
        >>> c.H(0)
        >>> c.rx(1, theta=np.pi/2)
        >>> c.sample_expectation_ps(x=[0], y=[1])
        -0.99999976
        >>> readout_error = []
        >>> readout_error.append([0.9,0.75])
        >>> readout_error.append([0.4,0.7])
        >>> c.sample_expectation_ps(x=[0], y=[1],readout_error = readout_error)

        >>> c = tc.Circuit(2)
        >>> c.cnot(0, 1)
        >>> c.rx(0, theta=0.4)
        >>> c.rx(1, theta=0.8)
        >>> c.h(0)
        >>> c.h(1)
        >>> error1 = tc.channels.generaldepolarizingchannel(0.1, 1)
        >>> error2 = tc.channels.generaldepolarizingchannel(0.06, 2)
        >>> readout_error = [[0.9, 0.75],[0.4, 0.7]]
        >>> noise_conf = NoiseConf()
        >>> noise_conf.add_noise("rx", error1)
        >>> noise_conf.add_noise("cnot", [error2], [[0, 1]])
        >>> noise_conf.add_noise("readout", readout_error)
        >>> c.sample_expectation_ps(x=[0], noise_conf=noise_conf, nmc=10000)
        0.44766843

        :param x: index for Pauli X, defaults to None
        :type x: Optional[Sequence[int]], optional
        :param y: index for Pauli Y, defaults to None
        :type y: Optional[Sequence[int]], optional
        :param z: index for Pauli Z, defaults to None
        :type z: Optional[Sequence[int]], optional
        :param shots: number of measurement shots, defaults to None, indicating analytical result
        :type shots: Optional[int], optional
        :param random_generator: random_generator, defaults to None
        :type random_generator: Optional[Any]
        :param status: external randomness given by tensor uniformly from [0, 1],
            if set, can overwrite random_generator
        :type status: Optional[Tensor]
        :param readout_error: readout_error, defaults to None. Overrided if noise_conf is provided.
        :type readout_error: Optional[Sequence[Any]]. Tensor, List, Tuple
        :param noise_conf: Noise Configuration, defaults to None
        :type noise_conf: Optional[NoiseConf], optional
        :param nmc: repetition time for Monte Carlo sampling for noisfy calculation, defaults to 1000
        :type nmc: int, optional
        :param statusc: external randomness given by tensor uniformly from [0, 1], defaults to None,
            used for noisfy circuit sampling
        :type statusc: Optional[Tensor], optional
        :return: [description]
        :rtype: Tensor
        '''
    sexpps = sample_expectation_ps
    def readouterror_bs(self, readout_error: Sequence[Any] | None = None, p: Any | None = None) -> Tensor:
        """Apply readout error to original probabilities of bit string and return the noisy probabilities.

        :Example:

        >>> readout_error = []
        >>> readout_error.append([0.9,0.75])  # readout error for qubit 0, [p0|0,p1|1]
        >>> readout_error.append([0.4,0.7])   # readout error for qubit 1, [p0|0,p1|1]


        :param readout_error: list of readout error for each qubits.
        :type readout_error: Optional[Sequence[Any]]. Tensor, List, Tuple
        :param p: probabilities of bit string
        :type p: Optional[Any]
        :rtype: Tensor
        """
    def replace_inputs(self, inputs: Tensor) -> None:
        """
        Replace the input state with the circuit structure unchanged.

        :param inputs: Input wavefunction.
        :type inputs: Tensor
        """
    def cond_measurement(self, index: int, status: float | None = None) -> Tensor:
        """
        Measurement on z basis at ``index`` qubit based on quantum amplitude
        (not post-selection). The highlight is that this method can return the
        measured result as a int Tensor and thus maintained a jittable pipeline.

        :Example:

        >>> c = tc.Circuit(2)
        >>> c.H(0)
        >>> r = c.cond_measurement(0)
        >>> c.conditional_gate(r, [tc.gates.i(), tc.gates.x()], 1)
        >>> c.expectation([tc.gates.z(), [0]]), c.expectation([tc.gates.z(), [1]])
        # two possible outputs: (1, 1) or (-1, -1)

        .. note::

            In terms of ``DMCircuit``, this method returns nothing and the density
            matrix after this method is kept in mixed state without knowing the
            measuremet resuslts



        :param index: the qubit for the z-basis measurement
        :type index: int
        :return: 0 or 1 for z measurement on up and down freedom
        :rtype: Tensor
        """
    cond_measure = cond_measurement
    def get_quvector(self) -> QuVector:
        """
        Get the representation of the output state in the form of ``QuVector``
        while maintaining the circuit uncomputed

        :return: ``QuVector`` representation of the output state from the circuit
        :rtype: QuVector
        """
    quvector = get_quvector
