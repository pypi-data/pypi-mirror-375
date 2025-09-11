from ...tensor import to_tensor as to_tensor
from ..dropout import DropPath as NDropPath, Dropout as NDropout
from .module import TorchModule as TorchModule
from pyvqnet.backends_mock import TorchMock as TorchMock

class DropPath(TorchModule, NDropPath):
    """
    DropPath module use torch backend

    :param dropout_rate: drop ratio ,default:0.5.
    :param name: name
    :return: a DropPath module
    """
    def __init__(self, dropout_rate: float = 0.5, name: str = '') -> None: ...
    def forward(self, x): ...

class Dropout(TorchModule, NDropout):
    """
    Dropout module use torch backend

    :param dropout_rate: drop ratio ,default:0.5.
    :param name: name
    :return: a Dropout module
    """
    def __init__(self, dropout_rate: float = 0.5, name: str = '') -> None: ...
    def forward(self, x): ...
