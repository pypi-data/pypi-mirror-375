import tensornetwork as tn
from . import gates as gates
from .cons import backend as backend, dtypestr as dtypestr
from .quantum import QuOperator as QuOperator
from _typeshed import Incomplete
from typing import Any, Callable, Sequence

logger: Incomplete
Gate = gates.Gate
Tensor = Any
sgates: Incomplete
vgates: Incomplete
mpogates: Incomplete
gate_aliases: Incomplete

class AbstractCircuit:
    inputs: Tensor
    circuit_param: dict[str, Any]
    is_mps: bool
    sgates = sgates
    vgates = vgates
    mpogates = mpogates
    gate_aliases = gate_aliases
    def apply_general_gate(self, gate: Gate | QuOperator, *index: int, name: str | None = None, split: dict[str, Any] | None = None, mpo: bool = False, ir_dict: dict[str, Any] | None = None) -> None:
        """
        An implementation of this method should also append gate directionary to self._qir
        """
    @staticmethod
    def apply_general_variable_gate_delayed(gatef: Callable[..., Gate], name: str | None = None, mpo: bool = False) -> Callable[..., None]: ...
    @staticmethod
    def apply_general_gate_delayed(gatef: Callable[[], Gate], name: str | None = None, mpo: bool = False) -> Callable[..., None]: ...
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
    @classmethod
    def from_qir(cls, qir: list[dict[str, Any]], circuit_params: dict[str, Any] | None = None) -> AbstractCircuit:
        '''
        Restore the circuit from the quantum intermediate representation.

        :Example:

        >>> c = tc.Circuit(3)
        >>> c.H(0)
        >>> c.rx(1, theta=tc.array_to_tensor(0.7))
        >>> c.exp1(0, 1, unitary=tc.gates._zz_matrix, theta=tc.array_to_tensor(-0.2), split=split)
        >>> len(c)
        7
        >>> c.expectation((tc.gates.z(), [1]))
        array(0.764842+0.j, dtype=complex64)
        >>> qirs = c.to_qir()
        >>>
        >>> c = tc.Circuit.from_qir(qirs, circuit_params={"nqubits": 3})
        >>> len(c._nodes)
        7
        >>> c.expectation((tc.gates.z(), [1]))
        array(0.764842+0.j, dtype=complex64)

        :param qir: The quantum intermediate representation of a circuit.
        :type qir: List[Dict[str, Any]]
        :param circuit_params: Extra circuit parameters.
        :type circuit_params: Optional[Dict[str, Any]]
        :return: The circuit have same gates in the qir.
        :rtype: Circuit
        '''
    def inverse(self, circuit_params: dict[str, Any] | None = None) -> AbstractCircuit:
        """
        inverse the circuit, return a new inversed circuit

        :EXAMPLE:

        >>> c = tc.Circuit(2)
        >>> c.H(0)
        >>> c.rzz(1, 2, theta=0.8)
        >>> c1 = c.inverse()

        :param circuit_params: keywords dict for initialization the new circuit, defaults to None
        :type circuit_params: Optional[Dict[str, Any]], optional
        :return: the inversed circuit
        :rtype: Circuit
        """
    def append_from_qir(self, qir: list[dict[str, Any]]) -> None:
        """
        Apply the ciurict in form of quantum intermediate representation after the current cirucit.

        :Example:

        >>> c = tc.Circuit(3)
        >>> c.H(0)
        >>> c.to_qir()
        [{'gatef': h, 'gate': Gate(...), 'index': (0,), 'name': 'h', 'split': None, 'mpo': False}]
        >>> c2 = tc.Circuit(3)
        >>> c2.CNOT(0, 1)
        >>> c2.to_qir()
        [{'gatef': cnot, 'gate': Gate(...), 'index': (0, 1), 'name': 'cnot', 'split': None, 'mpo': False}]
        >>> c.append_from_qir(c2.to_qir())
        >>> c.to_qir()
        [{'gatef': h, 'gate': Gate(...), 'index': (0,), 'name': 'h', 'split': None, 'mpo': False},
         {'gatef': cnot, 'gate': Gate(...), 'index': (0, 1), 'name': 'cnot', 'split': None, 'mpo': False}]

        :param qir: The quantum intermediate representation.
        :type qir: List[Dict[str, Any]]
        """
    def initial_mapping(self, logical_physical_mapping: dict[int, int], n: int | None = None, circuit_params: dict[str, Any] | None = None) -> AbstractCircuit:
        """
        generate a new circuit with the qubit mapping given by ``logical_physical_mapping``

        :param logical_physical_mapping: how to map logical qubits to the physical qubits on the new circuit
        :type logical_physical_mapping: Dict[int, int]
        :param n: number of qubit of the new circuit, can be different from the original one, defaults to None
        :type n: Optional[int], optional
        :param circuit_params: _description_, defaults to None
        :type circuit_params: Optional[Dict[str, Any]], optional
        :return: _description_
        :rtype: AbstractCircuit
        """
    def get_positional_logical_mapping(self) -> dict[int, int]:
        """
        Get positional logical mapping dict based on measure instruction.
        This function is useful when we only measure part of the qubits in the circuit,
        to process the count result from partial measurement, we must be aware of the mapping,
        i.e. for each position in the count bitstring, what is the corresponding qubits (logical)
        defined on the circuit

        :return: ``positional_logical_mapping``
        :rtype: Dict[int, int]
        """
    @staticmethod
    def standardize_gate(name: str) -> str:
        """
        standardize the gate name to tc common gate sets

        :param name: non-standard gate name
        :type name: str
        :return: the standard gate name
        :rtype: str
        """
    def gate_count(self, gate_list: Sequence[str] | None = None) -> int:
        '''
        count the gate number of the circuit

        :Example:

        >>> c = tc.Circuit(3)
        >>> c.h(0)
        >>> c.multicontrol(0, 1, 2, ctrl=[0, 1], unitary=tc.gates._x_matrix)
        >>> c.toffolli(1, 2, 0)
        >>> c.gate_count()
        3
        >>> c.gate_count(["multicontrol", "toffoli"])
        2

        :param gate_list: gate name list to be counted, defaults to None (counting all gates)
        :type gate_list: Optional[Sequence[str]], optional
        :return: the total number of all gates or gates in the ``gate_list``
        :rtype: int
        '''
    def gate_summary(self) -> dict[str, int]:
        """
        return the summary dictionary on gate type - gate count pair

        :return: the gate count dict by gate type
        :rtype: Dict[str, int]
        """
    def measure_instruction(self, index: int) -> None:
        """
        add a measurement instruction flag, no effect on numerical simulation

        :param index: the corresponding qubit
        :type index: int
        """
    def reset_instruction(self, index: int) -> None:
        """
        add a reset instruction flag, no effect on numerical simulation

        :param index: the corresponding qubit
        :type index: int
        """
    def barrier_instruction(self, *index: list[int]) -> None:
        """
        add a barrier instruction flag, no effect on numerical simulation

        :param index: the corresponding qubits
        :type index: List[int]
        """
    def select_gate(self, which: Tensor, kraus: Sequence[Gate], *index: int) -> None:
        """
        Apply ``which``-th gate from ``kraus`` list, i.e. apply kraus[which]

        :param which: Tensor of shape [] and dtype int
        :type which: Tensor
        :param kraus: A list of gate in the form of ``tc.gate`` or Tensor
        :type kraus: Sequence[Gate]
        :param index: the qubit lines the gate applied on
        :type index: int
        """
    conditional_gate = select_gate
    def cond_measurement(self, index: int) -> Tensor:
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
    def prepend(self, c: AbstractCircuit) -> AbstractCircuit:
        """
        prepend circuit ``c`` before

        :param c: The other circuit to be prepended
        :type c: BaseCircuit
        :return: The composed circuit
        :rtype: BaseCircuit
        """
    def insert(self, c): ...
    def append(self, c: AbstractCircuit, indices: list[int] | None = None) -> AbstractCircuit:
        """
        append circuit ``c`` before

        :example:

        >>> c1 = tc.Circuit(2)
        >>> c1.H(0)
        >>> c1.H(1)
        >>> c2 = tc.Circuit(2)
        >>> c2.cnot(0, 1)
        >>> c1.append(c2)
        <tensorcircuit.circuit.Circuit object at 0x7f8402968970>
        >>> c1.draw()
            ┌───┐
        q_0:┤ H ├──■──
            ├───┤┌─┴─┐
        q_1:┤ H ├┤ X ├
            └───┘└───┘

        :param c: The other circuit to be appended
        :type c: BaseCircuit
        :param indices: the qubit indices to which ``c`` is appended on.
            Defaults to None, which means plain concatenation.
        :type indices: Optional[List[int]], optional
        :return: The composed circuit
        :rtype: BaseCircuit
        """
    def expectation(self, *ops: tuple[tn.Node, list[int]], reuse: bool = True, noise_conf: Any | None = None, nmc: int = 1000, status: Tensor | None = None, **kws: Any) -> Tensor: ...
    def expectation_ps(self, x: Sequence[int] | None = None, y: Sequence[int] | None = None, z: Sequence[int] | None = None, reuse: bool = True, noise_conf: Any | None = None, nmc: int = 1000, status: Tensor | None = None, **kws: Any) -> Tensor:
        '''
        Shortcut for Pauli string expectation.
        x, y, z list are for X, Y, Z positions

        :Example:

        >>> c = tc.Circuit(2)
        >>> c.X(0)
        >>> c.H(1)
        >>> c.expectation_ps(x=[1], z=[0])
        array(-0.99999994+0.j, dtype=complex64)

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
        >>> c.expectation_ps(x=[0], noise_conf=noise_conf, nmc=10000)
        (0.46274087-3.764033e-09j)

        :param x: sites to apply X gate, defaults to None
        :type x: Optional[Sequence[int]], optional
        :param y: sites to apply Y gate, defaults to None
        :type y: Optional[Sequence[int]], optional
        :param z: sites to apply Z gate, defaults to None
        :type z: Optional[Sequence[int]], optional
        :param reuse: whether to cache and reuse the wavefunction, defaults to True
        :type reuse: bool, optional
        :param noise_conf: Noise Configuration, defaults to None
        :type noise_conf: Optional[NoiseConf], optional
        :param nmc: repetition time for Monte Carlo sampling for noisfy calculation, defaults to 1000
        :type nmc: int, optional
        :param status: external randomness given by tensor uniformly from [0, 1], defaults to None,
            used for noisfy circuit sampling
        :type status: Optional[Tensor], optional
        :return: Expectation value
        :rtype: Tensor
        '''
