from ....device import DEV_CPU as DEV_CPU, DEV_GPU_0 as DEV_GPU_0
from ....nn.torch import TorchModule as TorchModule
from .qop import QMachine as QMachine
from _typeshed import Incomplete
from collections import OrderedDict as OrderedDict, defaultdict as defaultdict, deque as deque
from pyvqnet.backends_mock import TorchMock as TorchMock

class TorchDataParalledVQCLayer(TorchModule):
    Comm_OP: Incomplete
    ddp: Incomplete
    def __init__(self, Comm_OP, vqc_module, name: str = '') -> None: ...
    def forward(self, x): ...
