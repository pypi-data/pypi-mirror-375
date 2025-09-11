from ...tensor import to_tensor as to_tensor
from .module import TorchModule as TorchModule
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock

class Pixel_Shuffle(TorchModule):
    """
    Pixel_Shuffle module use torch backend

    :param upscale_factors: upscale factors.
    :param name: name
    :return: a Pixel_Shuffle module
    """
    upscale_factors: Incomplete
    def __init__(self, upscale_factors: int, name: str = '') -> None: ...
    def forward(self, x): ...

class Pixel_Unshuffle(TorchModule):
    """
    Pixel_Unshuffle module use torch backend

    :param downscale_factors: downscale factors.
    :param name: name
    :return: a Pixel_Unshuffle module
    """
    downscale_factors: Incomplete
    def __init__(self, downscale_factors: int, name: str = '') -> None: ...
    def forward(self, x): ...
