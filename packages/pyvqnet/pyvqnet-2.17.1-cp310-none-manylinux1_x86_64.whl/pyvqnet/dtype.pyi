from _typeshed import Incomplete
from functools import lru_cache

kbool: int
kuint8: int
kint8: int
kint16: int
kint32: int
kint64: int
kfloat32: int
kfloat64: int
kcomplex64: int
kcomplex128: int
kcomplex32: int
kfloat16: int
HC_DTYPE = kcomplex32
HF_DTYPE = kfloat16
F_DTYPE = kfloat32
F_DTYPE = kfloat32
D_DTYPE = kfloat64
C_DTYPE = kcomplex64
Z_DTYPE = kcomplex128

@lru_cache
def may_be_hc_dtype(dtype): ...
@lru_cache
def may_be_c_dtype(dtype): ...
@lru_cache
def may_be_z_dtype(dtype): ...
@lru_cache
def may_be_f_dtype(dtype): ...
@lru_cache
def may_be_d_dtype(dtype): ...
@lru_cache
def may_be_hf_dtype(dtype): ...

vqnet_complex_dtypes: Incomplete
vqnet_float_dtypes: Incomplete
vqnet_complex_float_dtypes: Incomplete

@lru_cache
def complex_dtype_to_float_dtype(dtype): ...
@lru_cache
def float_dtype_to_complex_dtype(dtype): ...
@lru_cache
def get_readable_dtype_str(dtype_int):
    """
    get data type string for data type
    """
def dtype_map_from_numpy(dtype_np): ...

dtype_map: Incomplete
vqnet_2_np_dtype = dtype_map

class Defualt_QTensor_Dtype:
    default_dtype: Incomplete
    def __init__(self) -> None: ...
    def set_default_dtype(self, d) -> None: ...
    def get_default_dtype(self): ...

qtensor_default: Incomplete

def set_default_dtype(d) -> None: ...
def get_default_dtype(): ...
@lru_cache
def valid_param_dtype(dtype): ...
