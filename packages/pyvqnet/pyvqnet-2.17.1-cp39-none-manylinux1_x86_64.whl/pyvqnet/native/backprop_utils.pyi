import types
from .._core import Tensor as CoreTensor
from _typeshed import Incomplete

global_cache_map: Incomplete
use_qtensor_graphnode: bool

def set_use_qtensor_graphnode(flag) -> None: ...
def get_use_qtensor_graphnode(): ...
def erase_global_cache_map() -> None: ...
def get_global_cache_map(id): ...
def del_kv_in_global_cache_map(key) -> None: ...
def set_global_cache_map(id, fake) -> None: ...

class DummyTensor:
    id: Incomplete
    nodes: Incomplete
    device: Incomplete
    requires_grad: Incomplete
    shape: Incomplete
    stride: Incomplete
    dtype: Incomplete
    grad: Incomplete
    data: Incomplete
    output_idx: Incomplete
    def __init__(self, input_id, t) -> None: ...
    def hook_function(self): ...
    def get_output_idx(self): ...
    def set_output_idx(self, idx) -> None: ...

def create_fake_tensor(input_id, if_weights, t): ...

class keep_activation_in_graph:
    prev: bool
    def __init__(self) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: types.TracebackType | None) -> None: ...

class AutoGradNode:
    """
    A dummy autograd node for internal gradients calculation.
    It simply mocks QTensor without real data reference to save some storage.
    For internal activation may not need real data for backward.
    """
    id: Incomplete
    if_not_dummy: Incomplete
    tensor: Incomplete
    name: Incomplete
    df: Incomplete
    device: Incomplete
    output_nr: int
    outputs_grads: Incomplete
    expect_nr: Incomplete
    ready_grad_nr: int
    def __init__(self, tensor, df, expect_nr: int = 1, name: str = '') -> None: ...
    def reset_after_calc_grad(self) -> None: ...
    def add_output_grad(self, out_idx, grad) -> None: ...
    def get_ready_grad_nr(self): ...
    def get_outgrad(self): ...
    def add_output_nr(self) -> None: ...

def backprop(g, end_node, save_grad: bool = False, save_intern_act: bool = True): ...
def backprop_impl(out_grad, end_node, save_grad: bool, save_intern_act: bool):
    """
    real backpropgation impl
    """
def calc_op_mult_output_input_grad(node, i, outgrads, parent) -> CoreTensor:
    """
    calculate grad based on df.
    """
def calc_op_input_grad(node, i, outgrad, parent) -> CoreTensor:
    """
    calculate grad based on df.
    """
def free_backprop_grad(g, end_node) -> None: ...
def post_accum_grad_for_dp(end_node) -> None:
    """
    #all grad are done calculation, do all_reduce for data paralled(dp)
    """
