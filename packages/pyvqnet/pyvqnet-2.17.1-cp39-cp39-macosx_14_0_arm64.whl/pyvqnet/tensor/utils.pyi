from ..backends import global_backend as global_backend
from ..config import get_if_grad_enabled as get_if_grad_enabled, set_if_grad_enabled as set_if_grad_enabled
from ..dtype import kcomplex128 as kcomplex128, kcomplex32 as kcomplex32, kcomplex64 as kcomplex64, kfloat16 as kfloat16, kfloat32 as kfloat32, kfloat64 as kfloat64, vqnet_complex_dtypes as vqnet_complex_dtypes
from collections import defaultdict as defaultdict

slice_none_Placeholder: int

def FLOAT_2_COMPLEX(param): ...

class no_grad:
    prev: bool
    def __init__(self) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: types.TracebackType | None) -> None: ...

def has_duplicates(lst): ...
def maybe_wrap_dim(dim: list[int] | tuple[int, ...] | int, dim_post_expr, wrap_scalar: bool = True):
    """
    check dim valid
    """
