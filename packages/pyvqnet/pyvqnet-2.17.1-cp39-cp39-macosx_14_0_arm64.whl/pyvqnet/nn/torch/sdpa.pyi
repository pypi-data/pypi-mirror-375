from ...tensor import to_tensor as to_tensor
from ...transformer import SDPA as NSDPA
from .module import TorchModule as TorchModule
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock

def scaled_dot_product_attention(query, key, value, attn_mask: Incomplete | None = None, dropout_p: float = 0.0, is_causal: bool = False, scale: Incomplete | None = None): ...

class SDPA(TorchModule, NSDPA):
    """
    sdpa (scaled dot product attention) layer .

    This Module use torch.nn.functional.scaled_dot_product_attention.

    :param attn_mask: Attention mask; Default: None.shape must be broadcastable to the shape of attention weights.
    :param dropout_p:  Dropout probability; Default: 0,if greater than 0.0, dropout is applied.
    :param scale:  Scaling factor applied prior to softmax, Default: None.
    :param is_causal: default:False,If set to true, the attention masking is a lower triangular matrix when the mask is a square matrix. 
        An error is thrown if both attn_mask and is_causal are set.

    """
    def __init__(self, attn_mask: Incomplete | None = None, dropout_p: float = 0.0, scale: Incomplete | None = None, is_causal: bool = False) -> None: ...
    attn_mask: Incomplete
    def forward(self, query, key, value): ...
