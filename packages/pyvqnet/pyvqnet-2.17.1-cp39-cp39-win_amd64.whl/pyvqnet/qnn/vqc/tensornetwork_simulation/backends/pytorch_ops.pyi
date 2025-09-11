import torch
from typing import Any

Array = Any
qr_epsilon: float

def torchqr_grad(a: Array, q: Array, r: Array, dq: Array, dr: Array) -> Array:
    """Get the gradient for Qr."""

class torchqr(torch.autograd.Function):
    """
    Customized backward of qr for better numerical stability
    """
    @staticmethod
    def forward(a: Array) -> Any: ...
    @staticmethod
    def setup_context(ctx, inputs, output) -> None: ...
    @staticmethod
    def backward(ctx, dq: Array, dr: Array) -> Any: ...
    @staticmethod
    def vmap(info, in_dims, a): ...
