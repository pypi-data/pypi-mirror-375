from .numpy_backend import NumpyBackend as NumpyBackend
from .pytorch_backend import PyTorchBackend as PyTorchBackend
from _typeshed import Incomplete
from typing import Any

tnbackend: Incomplete
bk = Any

def get_backend(backend: str | bk) -> bk:
    '''
    Get the `tc.backend` object.

    :param backend: "numpy", "tensorflow", "jax", "pytorch"
    :type backend: Union[Text, tnbackend]
    :raises ValueError: Backend doesn\'t exist for `backend` argument.
    :return: The `tc.backend` object that with all registered universal functions.
    :rtype: backend object
    '''
