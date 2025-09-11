from .native import VQNet_Native_Impl_Backend as VQNet_Native_Impl_Backend
from .torch import TorchNativeBackend as TorchNativeBackend
from _typeshed import Incomplete

global_backend_name: str
global_backend: Incomplete
valid_backend: Incomplete
default_qtensor_class_tuple: Incomplete
default_torch_class_tuple: Incomplete
package_name: str

def set_backend(backend_name: str):
    '''

    Set the backend used for current calculation and data storage. The default is "pyvqnet" and can be set to "torch".
    After using `pyvqnet.backends.set_backend("torch")`, the interface remains unchanged, but the `data` member variables of VQNet\'s `QTensor` all use `torch.Tensor` to store data,
    and use torch for calculation.
    After using `pyvqnet.backends.set_backend("pyvqnet")`, the `data` member variables of VQNet `QTensor` all use `pyvqnet._core.Tensor` to store data and use the pyvqnet c++ library for calculation.
    After using `pyvqnet.backends.set_backend("torch-native")`, the input can be torch.Tensor or QTensor, the output will be torch.tensor, the `data` member variables of VQNet\'s `QTensor` all use `torch.Tensor` to store data,
    and use torch for calculation.
    .. note::

        This function modifies the current calculation backend.
        `QTensor` obtained under different backends cannot be calculated in one phase.
        
    
    :param backend_name: backend name.

    Example::

        import pyvqnet
        pyvqnet.backends.set_backend("torch")
    '''
def check_data_type(t): ...
def get_backend(t=None):
    '''
    If t is None, get the current computation backend. 
    If t is a QTensor, return the computation backend used when the QTensor was created according to its `data` attribute.
    
    If "torch" is the used backend, it returns pyvqnet torch api backend.
    If "pyvqnet" is the used backend, it simplely returns "pyvqnet."

    :param t: current tensor, default: "None".
    :return: backend. Returns `pyvqnet` by default.

    Example::

        import pyvqnet
        pyvqnet.backends.set_backend("torch")
        pyvqnet.backends.get_backend()

    '''
def get_backend_name(): ...
def check_uniform_type(elements) -> None: ...
def check_not_default_backend(t=None): ...
