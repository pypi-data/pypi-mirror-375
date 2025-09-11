from ..device import DEV_CPU as DEV_CPU, DEV_GPU_0 as DEV_GPU_0
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock

torch_bool: Incomplete
torch_uint8: Incomplete
torch_int8: Incomplete
torch_int16: Incomplete
torch_int32: Incomplete
torch_int64: Incomplete
torch_float32: Incomplete
torch_float64: Incomplete
torch_complex64: Incomplete
torch_complex128: Incomplete
torch_complex32: Incomplete
torch_float16: Incomplete

def set_random_seed(seed) -> None: ...
def get_random_seed(): ...

dtype_map_torch_dict: Incomplete

def dtype_map_torch(vqnet_dtype):
    """
    convert vqnet dtype to torch
    """
def device_map_torch(vqnet_device):
    """
    convert vqnet device to torch
    """
def set_grad_enabled(flag) -> None: ...
def get_grad_enabled(): ...
def requires_grad_getter(self): ...
def requires_grad_setter(self, value) -> None: ...
def get_vqnet_device(torch_device): ...

get_vqnet_dtype_dict: Incomplete

def get_vqnet_dtype(dtype): ...
