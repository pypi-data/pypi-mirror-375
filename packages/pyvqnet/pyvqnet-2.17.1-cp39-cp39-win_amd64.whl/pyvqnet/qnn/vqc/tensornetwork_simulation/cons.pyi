from .backends import get_backend as get_backend
from .backends.numpy_backend import NumpyBackend as NumpyBackend
from _typeshed import Incomplete
from contextlib import contextmanager
from typing import Any, Callable, Iterator

logger: Incomplete
package_name: str
thismodule: Incomplete
dtypestr: str
rdtypestr: str
npdtype: Incomplete
backend: NumpyBackend
contractor: Incomplete

def move_tensor_to_same_device(tensor1, tensor2): ...
def move_tensor_to_same_complex_dtype(tensor1, tensor2): ...
def set_tensornetwork_backend(backend: str | None = None, set_global: bool = True) -> Any:
    '''To set the runtime backend of tensorcircuit.

    Note: ``tc.set_backend`` and ``tc.cons.set_tensornetwork_backend`` are the same.

    :Example:

    >>> tc.set_backend("numpy")
    numpy_backend
    >>> tc.gates.num_to_tensor(0.1)
    array(0.1+0.j, dtype=complex64)
    >>>
    >>> tc.set_backend("tensorflow")
    tensorflow_backend
    >>> tc.gates.num_to_tensor(0.1)
    <tf.Tensor: shape=(), dtype=complex64, numpy=(0.1+0j)>
    >>>
    >>> tc.set_backend("pytorch")
    pytorch_backend
    >>> tc.gates.num_to_tensor(0.1)
    tensor(0.1000+0.j)
    >>>
    >>> tc.set_backend("jax")
    jax_backend
    >>> tc.gates.num_to_tensor(0.1)
    DeviceArray(0.1+0.j, dtype=complex64)

    :param backend: "numpy", "tensorflow", "jax", "pytorch". defaults to None,
        which gives the same behavior as ``tensornetwork.backend_contextmanager.get_default_backend()``.
    :type backend: Optional[str], optional
    :param set_global: Whether the object should be set as global.
    :type set_global: bool
    :return: The `tc.backend` object that with all registered universal functions.
    :rtype: backend object
    '''
set_backend = set_tensornetwork_backend

def set_function_backend(backend: str | None = None) -> Callable[..., Any]:
    '''
    Function decorator to set function-level runtime backend

    :param backend: "numpy", "tensorflow", "jax", "pytorch", defaults to None
    :type backend: Optional[str], optional
    :return: Decorated function
    :rtype: Callable[..., Any]
    '''
@contextmanager
def runtime_backend(backend: str | None = None) -> Iterator[Any]:
    '''
    Context manager to set with-level runtime backend

    :param backend: "numpy", "tensorflow", "jax", "pytorch", defaults to None
    :type backend: Optional[str], optional
    :yield: the backend object
    :rtype: Iterator[Any]
    '''
def set_dtype(dtype: str | None = None, set_global: bool = True) -> tuple[str, str]:
    '''
    Set the global runtime numerical dtype of tensors.

    :param dtype: "complex64"/"float32" or "complex128"/"float64",
        defaults to None, which is equivalent to "complex64".
    :type dtype: Optional[str], optional
    :return: complex dtype str and the corresponding real dtype str
    :rtype: Tuple[str, str]
    '''

get_dtype: Incomplete

def set_function_dtype(dtype: str | None = None) -> Callable[..., Any]:
    '''
    Function decorator to set function-level numerical dtype

    :param dtype: "complex64" or "complex128", defaults to None
    :type dtype: Optional[str], optional
    :return: The decorated function
    :rtype: Callable[..., Any]
    '''
@contextmanager
def runtime_dtype(dtype: str | None = None) -> Iterator[tuple[str, str]]:
    '''
    Context manager to set with-level runtime dtype

    :param dtype: "complex64" or "complex128", defaults to None ("complex64")
    :type dtype: Optional[str], optional
    :yield: complex dtype str and real dtype str
    :rtype: Iterator[Tuple[str, str]]
    '''
def experimental_contractor(nodes: list[Any], output_edge_order: list[Any] | None = None, ignore_edge_order: bool = False, local_steps: int = 2) -> Any: ...
def plain_contractor(nodes: list[Any], output_edge_order: list[Any] | None = None, ignore_edge_order: bool = False) -> Any:
    """
    The naive state-vector simulator contraction path.

    :param nodes: The list of ``tn.Node``.
    :type nodes: List[Any]
    :param output_edge_order: The list of dangling node edges, defaults to be None.
    :type output_edge_order: Optional[List[Any]], optional
    :return: The ``tn.Node`` after contraction
    :rtype: tn.Node
    """
def nodes_to_adj(ns: list[Any]) -> Any: ...

has_ps: bool

def d2s(n: int, dl: list[Any]) -> list[Any]: ...
def tn_greedy_contractor(nodes: list[Any], output_edge_order: list[Any] | None = None, ignore_edge_order: bool = False, max_branch: int = 1) -> Any: ...
def custom(nodes: list[Any], optimizer: Any, memory_limit: int | None = None, output_edge_order: list[Any] | None = None, ignore_edge_order: bool = False, **kws: Any) -> Any: ...
def custom_stateful(nodes: list[Any], optimizer: Any, memory_limit: int | None = None, opt_conf: dict[str, Any] | None = None, output_edge_order: list[Any] | None = None, ignore_edge_order: bool = False, **kws: Any) -> Any: ...
def contraction_info_decorator(algorithm: Callable[..., Any]) -> Callable[..., Any]: ...
def set_contractor(method: str | None = None, optimizer: Any | None = None, memory_limit: int | None = None, opt_conf: dict[str, Any] | None = None, set_global: bool = True, contraction_info: bool = False, debug_level: int = 0, **kws: Any) -> Callable[..., Any]:
    '''
    To set runtime contractor of the tensornetwork for a better contraction path.
    For more information on the usage of contractor, please refer to independent tutorial.

    :param method: "auto", "greedy", "branch", "plain", "tng", "custom", "custom_stateful". defaults to None ("auto")
    :type method: Optional[str], optional
    :param optimizer: Valid for "custom" or "custom_stateful" as method, defaults to None
    :type optimizer: Optional[Any], optional
    :param memory_limit: It is not very useful, as ``memory_limit`` leads to ``branch`` contraction
        instead of ``greedy`` which is rather slow, defaults to None
    :type memory_limit: Optional[int], optional
    :raises Exception: Tensornetwork version is too low to support some of the contractors.
    :raises ValueError: Unknown method options.
    :return: The new tensornetwork with its contractor set.
    :rtype: tn.Node
    '''

get_contractor: Incomplete

def set_function_contractor(*confargs: Any, **confkws: Any) -> Callable[..., Any]:
    """
    Function decorate to change function-level contractor

    :return: _description_
    :rtype: Callable[..., Any]
    """
@contextmanager
def runtime_contractor(*confargs: Any, **confkws: Any) -> Iterator[Any]:
    """
    Context manager to change with-levek contractor

    :yield: _description_
    :rtype: Iterator[Any]
    """
def split_rules(max_singular_values: int | None = None, max_truncation_err: float | None = None, relative: bool = False) -> Any:
    """
    Obtain the direcionary of truncation rules

    :param max_singular_values: The maximum number of singular values to keep.
    :type max_singular_values: int, optional
    :param max_truncation_err: The maximum allowed truncation error.
    :type max_truncation_err: float, optional
    :param relative: Multiply `max_truncation_err` with the largest singular value.
    :type relative: bool, optional
    """
