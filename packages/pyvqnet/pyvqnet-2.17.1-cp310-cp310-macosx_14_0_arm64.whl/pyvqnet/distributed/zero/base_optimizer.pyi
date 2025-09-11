from _typeshed import Incomplete
from pyvqnet import tensor as tensor
from pyvqnet.distributed import get_rank as get_rank, get_world_size as get_world_size

class DeepSpeedOptimizer: ...

class DummyOptim:
    """
    Dummy optimizer presents model parameters as a param group, this is
    primarily used to allow ZeRO-3 without an optimizer
    """
    param_groups: Incomplete
    def __init__(self, params) -> None: ...

class ZeROOptimizer(DeepSpeedOptimizer): ...
