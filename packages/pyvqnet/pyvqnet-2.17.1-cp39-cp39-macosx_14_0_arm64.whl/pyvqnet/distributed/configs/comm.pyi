from .. import tensor as tensor
from ...device import DEV_GPU_MAX as DEV_GPU_MAX, if_nccl_compiled as if_nccl_compiled
from ...dtype import kfloat32 as kfloat32, kfloat64 as kfloat64
from ...logger import logger as logger
from ...tensor import empty as empty
from _typeshed import Incomplete
from pyvqnet.distributed.ControlComm import CommController as CommController

pp_Comm_OP: Incomplete

def get_global_CommController_for_deepspeed(): ...

class ProcessGroup:
    """
    a wrapper of distributed prcoess group.

    :param ranks: list of global ranking.

    """
    ranks: Incomplete
    size: Incomplete
    def __init__(self, ranks=[]) -> None: ...
    def get_rank(self, rank): ...
    def get_ranks(self): ...
    def get_size(self): ...

supported_types: Incomplete

def new_group(ranks=[]):
    """
    create new ProcessGroup

    :param rank: target ranks list to create new group.
    :return:
        new ProcessGroup
    """
def device_count():
    """
    return gpu device counts.

    """
def get_world_size(group: Incomplete | None = None): ...
def get_rank(group: Incomplete | None = None):
    """
    get global rank or rank in group.

    :param group: process group, default:None,use global.
    return:
        global rank or rank in group.

    """
def get_local_rank():
    """

    get local_rank in a node, which is used to index GPU device.

    return:
        local_rank.

    """
def get_global_rank(): ...
def is_initialized(): ...
def set_device(device_id) -> None: ...
def barrier() -> None: ...
def broadcast(t, root, group: ProcessGroup = None): ...
def send(t, root) -> None: ...
def recv(t, root) -> None: ...
def all_reduce(t, group: ProcessGroup = None, op: str = 'sum'): ...
def reduce(t, rank, group: ProcessGroup): ...
def all_gather_into_tensor(group_flat, t, group: ProcessGroup): ...

class ReduceOp:
    """
    ReduceOp using for nccl.
    """
    SUM: str
    PRODUCT: str
    MIN: str
    MAX: str
