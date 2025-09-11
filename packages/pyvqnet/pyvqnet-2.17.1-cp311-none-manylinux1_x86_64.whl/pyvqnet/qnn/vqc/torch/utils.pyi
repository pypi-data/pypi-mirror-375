from ....dtype import get_readable_dtype_str as get_readable_dtype_str, kcomplex128 as kcomplex128, kcomplex32 as kcomplex32, kcomplex64 as kcomplex64
from ....torch import get_vqnet_dtype as get_vqnet_dtype
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock

valid_complex_dtype: Incomplete
valid_float_dtype: Incomplete

def complex_dtype_to_float_dtype(dtype): ...
def float_dtype_to_complex_dtype(dtype): ...
