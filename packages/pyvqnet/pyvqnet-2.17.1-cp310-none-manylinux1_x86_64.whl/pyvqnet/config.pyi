from .backends import global_backend as global_backend
from functools import lru_cache as _lru_cache

if_show_bp_info: bool
is_dist_init: bool

def get_is_dist_init():
    """
    global flag if vqnet distributed is initialed.

    """
def set_is_dist_init(flag) -> None:
    """
    set global flag if vqnet distributed is initialed.
    
    """
def get_if_grad_enabled():
    """
    get if_grad_enabled based on backend
    """
def set_if_grad_enabled(flag) -> None:
    """
    set value of if_grad_enabled
    """
def get_if_show_bp_info():
    """
    get flag of if_show_bp_info
    """
def set_if_show_bp_info(flag) -> None:
    """
    set flag of if_show_bp_info
    """
def init_if_show_bp() -> None:
    """
    init flag of if_show_bp_info to False
    """
@_lru_cache
def is_opt_einsum_available() -> bool:
    """Return a bool indicating if opt_einsum is currently available."""
