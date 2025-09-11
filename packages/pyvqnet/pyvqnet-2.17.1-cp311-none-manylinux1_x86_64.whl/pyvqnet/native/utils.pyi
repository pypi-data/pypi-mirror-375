from ..dtype import kcomplex128 as kcomplex128, kcomplex32 as kcomplex32, kcomplex64 as kcomplex64, kfloat16 as kfloat16, kfloat32 as kfloat32, kfloat64 as kfloat64, vqnet_complex_dtypes as vqnet_complex_dtypes
from collections import defaultdict as defaultdict

slice_none_Placeholder: int

def has_duplicates(lst): ...
def maybe_wrap_dim(dim: list[int] | tuple[int, ...] | int, dim_post_expr, wrap_scalar: bool = True):
    """
    check dim valid
    """
def maybe_wrap_dim_unsqueeze(dim, dim_post_expr, wrap_scalar: bool = True):
    """    check dim valid
    """
