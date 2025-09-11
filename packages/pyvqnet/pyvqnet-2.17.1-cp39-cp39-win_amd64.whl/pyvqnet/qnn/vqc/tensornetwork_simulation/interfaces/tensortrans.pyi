from ..backends import get_backend as get_backend
from ..cons import backend as backend, dtypestr as dtypestr
from ..gates import Gate as Gate
from ..quantum import QuOperator as QuOperator
from _typeshed import Incomplete
from typing import Any, Callable, Sequence

Tensor = Any
Array = Any
module2backend: Incomplete

def which_backend(a: Tensor, return_backend: bool = True) -> Any:
    """
    Given a tensor ``a``, return the corresponding backend

    :param a: the tensor
    :type a: Tensor
    :param return_backend: if true, return backend object, if false, return backend str,
        defaults to True
    :type return_backend: bool, optional
    :return: the backend object or backend str
    :rtype: Any
    """
def tensor_to_numpy(t: Tensor) -> Array: ...
def tensor_to_backend_jittable(t: Tensor) -> Tensor: ...
def numpy_to_tensor(t: Array, backend: Any) -> Tensor: ...
def tensor_to_dtype(t: Tensor) -> str: ...
def tensor_to_dlpack(t: Tensor) -> Any: ...
def general_args_to_numpy(args: Any) -> Any:
    """
    Given a pytree, get the corresponding numpy array pytree

    :param args: pytree
    :type args: Any
    :return: the same format pytree with all tensor replaced by numpy array
    :rtype: Any
    """
def numpy_args_to_backend(args: Any, dtype: Any = None, target_backend: Any = None) -> Any:
    """
    Given a pytree of numpy arrays, get the corresponding tensor pytree

    :param args: pytree of numpy arrays
    :type args: Any
    :param dtype: str of str of the same pytree shape as args, defaults to None
    :type dtype: Any, optional
    :param target_backend: str or backend object, defaults to None,
        indicating the current default backend
    :type target_backend: Any, optional
    :return: the same format pytree with all numpy array replaced by the tensors
        in the target backend
    :rtype: Any
    """
def general_args_to_backend(args: Any, dtype: Any = None, target_backend: Any = None, enable_dlpack: bool = True) -> Any: ...
def gate_to_matrix(t: Gate, is_reshapem: bool = True) -> Tensor: ...
def qop_to_matrix(t: QuOperator, is_reshapem: bool = True) -> Tensor: ...
def args_to_tensor(f: Callable[..., Any], argnums: int | Sequence[int] = 0, tensor_as_matrix: bool = False, gate_to_tensor: bool = False, gate_as_matrix: bool = True, qop_to_tensor: bool = False, qop_as_matrix: bool = True, cast_dtype: bool = True) -> Callable[..., Any]:
    '''
    Function decorator that automatically convert inputs to tensors on current backend

    :Example:

    .. code-block:: python

        tc.set_backend("jax")

        @partial(
        tc.interfaces.args_to_tensor,
        argnums=[0, 1, 2],
        gate_to_tensor=True,
        qop_to_tensor=True,
        )
        def f(a, b, c, d):
            return a, b, c, d

        f(
        [tc.Gate(np.ones([2, 2])), tc.Gate(np.ones([2, 2, 2, 2]))],
        tc.QuOperator.from_tensor(np.ones([2, 2, 2, 2, 2, 2])),
        np.ones([2, 2, 2, 2]),
        tf.zeros([1, 2]),
        )

        # ([DeviceArray([[1.+0.j, 1.+0.j],
        #        [1.+0.j, 1.+0.j]], dtype=complex64),
        # DeviceArray([[1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j],
        #             [1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j],
        #             [1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j],
        #             [1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j]], dtype=complex64)],
        # DeviceArray([[1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j,
        #             1.+0.j],
        #             [1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j,
        #             1.+0.j],
        #             [1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j,
        #             1.+0.j],
        #             [1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j,
        #             1.+0.j],
        #             [1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j,
        #             1.+0.j],
        #             [1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j,
        #             1.+0.j],
        #             [1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j,
        #             1.+0.j],
        #             [1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j,
        #             1.+0.j]], dtype=complex64),
        # DeviceArray([[[[1.+0.j, 1.+0.j],
        #                 [1.+0.j, 1.+0.j]],

        #             [[1.+0.j, 1.+0.j],
        #                 [1.+0.j, 1.+0.j]]],


        #             [[[1.+0.j, 1.+0.j],
        #                 [1.+0.j, 1.+0.j]],

        #             [[1.+0.j, 1.+0.j],
        #                 [1.+0.j, 1.+0.j]]]], dtype=complex64),
        # <tf.Tensor: shape=(1, 2), dtype=float32, numpy=array([[0., 0.]], dtype=float32)>)



    :param f: the wrapped function whose arguments in ``argnums``
        position are expected to be tensor format
    :type f: Callable[..., Any]
    :param argnums: position of args under the auto conversion, defaults to 0
    :type argnums: Union[int, Sequence[int]], optional
    :param tensor_as_matrix: try reshape all input tensor as matrix
        with shape rank 2, defaults to False
    :type tensor_as_matrix: bool, optional
    :param gate_to_tensor: convert ``Gate`` to tensor, defaults to False
    :type gate_to_tensor: bool, optional
    :param gate_as_matrix: reshape tensor from ``Gate`` input as matrix, defaults to True
    :type gate_as_matrix: bool, optional
    :param qop_to_tensor: convert ``QuOperator`` to tensor, defaults to False
    :type qop_to_tensor: bool, optional
    :param qop_as_matrix: reshape tensor from ``QuOperator`` input as matrix, defaults to True
    :type qop_as_matrix: bool, optional
    :param cast_dtype: whether cast to backend dtype, defaults to True
    :type cast_dtype: bool, optional
    :return: The wrapped function
    :rtype: Callable[..., Any]
    '''
