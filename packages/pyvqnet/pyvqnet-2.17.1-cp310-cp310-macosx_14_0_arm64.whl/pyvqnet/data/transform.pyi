from _typeshed import Incomplete
from pyvqnet.dtype import get_default_dtype as get_default_dtype
from pyvqnet.tensor import QTensor as QTensor

class TransformCompose:
    """
    compose multible transform function.

    :param transforms: list of callable transform functions.

    """
    transforms: Incomplete
    def __init__(self, transforms) -> None: ...
    def __call__(self, img): ...

class TransformResize:
    """
    resize image like [c,h,w]

    :param size: target size,int or tuple of int.
    """
    size: Incomplete
    def __init__(self, size: int | tuple[int, int]) -> None: ...
    def __call__(self, img): ...

class TransformCenterCrop:
    """
    center crop image like [c,h,w]

    :param size: target size,int or tuple of int.
    """
    size: Incomplete
    def __init__(self, size: int | tuple[int, int]) -> None: ...
    def __call__(self, img): ...

class TransformToTensor:
    """
    convert image to QTensor class.

    :param size: target size,int or tuple of int.
    """
    def __call__(self, pic): ...

class TransformNormalize:
    """
    Normalize image with mean and standard variance.

    :param mean: list of mean value.
    :param std: list of standard variance.
    """
    mean: Incomplete
    std: Incomplete
    def __init__(self, mean, std) -> None: ...
    def __call__(self, tensor): ...
