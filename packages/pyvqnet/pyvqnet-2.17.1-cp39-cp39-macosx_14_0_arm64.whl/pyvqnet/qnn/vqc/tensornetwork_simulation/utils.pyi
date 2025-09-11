from _typeshed import Incomplete
from typing import Any, Callable, Sequence

def return_partial(f: Callable[..., Any], return_argnums: int | Sequence[int] = 0) -> Callable[..., Any]:
    """
    Return a callable function for output ith parts of the original output along the first axis.
    Original output supports List and Tensor.

    :Example:

    >>> from tensorcircuit.utils import return_partial
    >>> testin = np.array([[1,2],[3,4],[5,6],[7,8]])
    >>> # Method 1:
    >>> return_partial(lambda x: x, [1, 3])(testin)
    (array([3, 4]), array([7, 8]))
    >>> # Method 2:
    >>> from functools import partial
    >>> @partial(return_partial, return_argnums=(0,2))
    ... def f(inp):
    ...     return inp
    ...
    >>> f(testin)
    (array([1, 2]), array([5, 6]))

    :param f: The function to be applied this method
    :type f: Callable[..., Any]
    :param return_partial: The ith parts of original output along the first axis (axis=0 or dim=0)
    :type return_partial: Union[int, Sequence[int]]
    :return: The modified callable function
    :rtype: Callable[..., Any]
    """
def append(f: Callable[..., Any], *op: Callable[..., Any]) -> Any:
    """
    Functional programming paradigm to build function pipeline

    :Example:

    >>> f = tc.utils.append(lambda x: x**2, lambda x: x+1, tc.backend.mean)
    >>> f(tc.backend.ones(2))
    (2+0j)

    :param f: The function which are attached with other functions
    :type f: Callable[..., Any]
    :param op: Function to be attached
    :type op: Callable[..., Any]
    :return: The final results after function pipeline
    :rtype: Any
    """
def is_m1mac() -> bool:
    """
    check whether the running platform is MAC with M1 chip

    :return: True for MAC M1 platform
    :rtype: bool
    """
def is_sequence(x: Any) -> bool: ...
def is_number(x: Any) -> bool: ...
def arg_alias(f: Callable[..., Any], alias_dict: dict[str, str | Sequence[str]], fix_doc: bool = True) -> Callable[..., Any]:
    """
    function argument alias decorator with new docstring

    :param f: _description_
    :type f: Callable[..., Any]
    :param alias_dict: _description_
    :type alias_dict: Dict[str, Union[str, Sequence[str]]]
    :param fix_doc: whether to add doc for these new alias arguments, defaults True
    :type fix_doc: bool
    :return: the decorated function
    :rtype: Callable[..., Any]
    """
def benchmark(f: Any, *args: Any, tries: int = 5, verbose: bool = True) -> tuple[Any, float, float]:
    """
    benchmark jittable function with staging time and running time

    :param f: _description_
    :type f: Any
    :param tries: _description_, defaults to 5
    :type tries: int, optional
    :param verbose: _description_, defaults to True
    :type verbose: bool, optional
    :return: _description_
    :rtype: Tuple[Any, float, float]
    """
def run_prob_list(cir, act_wires_idx):
    """
    get analytic probability of specific qubits
    """
def get_expectation(cir, paulistr):
    """
    Expectation value of the supplied Hamiltonian observables

    :param cir: tensornetwork_simulation.Circuit
    :param paulistr: Hamiltonian pauli string, such as {'Z0 Z1':1}
    """
def get_expectation_real(cir, paulistr):
    """
    Expectation value of the supplied Hamiltonian observables of real

    :param cir: tensornetwork_simulation.Circuit
    :param paulistr: Hamiltonian pauli string, such as {'Z0 Z1':1}
    """
def get_sample(cir, wires, shots): ...
def analytic_probability(state, num_wires, wires: Incomplete | None = None): ...
def unique_wires(whole_wires, act_on_wires): ...
def generate_basis_states(num_wires, dtype=...): ...
def marginal_prob(prob, num_wires, wires): ...
