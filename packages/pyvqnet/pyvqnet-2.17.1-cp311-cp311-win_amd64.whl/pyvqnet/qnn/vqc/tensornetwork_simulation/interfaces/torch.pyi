from ..cons import backend as backend
from ..utils import is_sequence as is_sequence
from .tensortrans import general_args_to_backend as general_args_to_backend
from typing import Any, Callable

Tensor = Any

def torch_interface(fun: Callable[..., Any], jit: bool = False, enable_dlpack: bool = False) -> Callable[..., Any]:
    '''
    Wrap a quantum function on different ML backend with a pytorch interface.

    :Example:

    .. code-block:: python

        import torch

        tc.set_backend("tensorflow")


        def f(params):
            c = tc.Circuit(1)
            c.rx(0, theta=params[0])
            c.ry(0, theta=params[1])
            return c.expectation([tc.gates.z(), [0]])


        f_torch = tc.interfaces.torch_interface(f, jit=True)

        a = torch.ones([2], requires_grad=True)
        b = f_torch(a)
        c = b ** 2
        c.backward()

        print(a.grad)

    :param fun: The quantum function with tensor in and tensor out
    :type fun: Callable[..., Any]
    :param jit: whether to jit ``fun``, defaults to False
    :type jit: bool, optional
    :param enable_dlpack: whether transform tensor backend via dlpack, defaults to False
    :type enable_dlpack: bool, optional
    :return: The same quantum function but now with torch tensor in and torch tensor out
        while AD is also supported
    :rtype: Callable[..., Any]
    '''
pytorch_interface = torch_interface
