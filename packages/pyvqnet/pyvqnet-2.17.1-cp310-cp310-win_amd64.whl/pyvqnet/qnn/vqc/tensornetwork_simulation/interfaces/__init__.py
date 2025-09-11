"""
Interfaces bridging different backends
"""

from . import tensortrans
from .tensortrans import (
    which_backend,
    numpy_args_to_backend,
    general_args_to_numpy,
    general_args_to_backend,
    args_to_tensor,
)
from .torch import torch_interface, pytorch_interface