from _typeshed import Incomplete
from pyvqnet.backends import global_backend as global_backend
from pyvqnet.backends_mock import TorchMock as TorchMock
from pyvqnet.nn.parameter import Parameter as Parameter
from pyvqnet.nn.torch import TorchModule as Module, TorchSequential as Sequential
from pyvqnet.nn.torch.activation import ReLU as ReLU
from pyvqnet.tensor import QTensor as QTensor, as_qtensor as as_qtensor, tensor as tensor
from typing import Callable

Tensor = QTensor

class Flatten(Module):
    __constants__: Incomplete
    start_dim: int
    end_dim: int
    def __init__(self, start_dim: int = 1, end_dim: int = -1) -> None: ...
    def forward(self, input): ...
    def extra_repr(self) -> str: ...

class PatchMerging(Module):
    dim: Incomplete
    reduction: Incomplete
    norm: Incomplete
    def __init__(self, dim: int, norm_layer: Callable[..., Module] = ...) -> None: ...
    def forward(self, x: Tensor): ...

def normalize(q, dim: int = -1): ...
def pad(x, pad, value: int = 0): ...
def linear(x, w, b): ...
def softmax(x, axis): ...
def shifted_window_attention(input: Tensor, qkv_weight: Tensor, proj_weight: Tensor, relative_position_bias: Tensor, window_size: list[int], num_heads: int, shift_size: list[int], attention_dropout: float = 0.0, dropout: float = 0.0, qkv_bias: Tensor | None = None, proj_bias: Tensor | None = None, logit_scale: Tensor | None = None, training: bool = True) -> Tensor: ...

class MLP(Sequential):
    """This block implements the multi-layer perceptron (MLP) module.

    Args:
        in_channels (int): Number of channels of the input
        hidden_channels (List[int]): List of the hidden channel dimensions
        norm_layer (Callable[..., torch.Module], optional): Norm layer that will be stacked on top of the linear layer. If ``None`` this layer won't be used. Default: ``None``
        activation_layer (Callable[..., torch.Module], optional): Activation function which will be stacked on top of the normalization layer (if not None), otherwise on top of the linear layer. If ``None`` this layer won't be used. Default: ``torch.ReLU``
        inplace (bool, optional): Parameter for the activation layer, which can optionally do the operation in-place.
            Default is ``None``, which uses the respective default values of the ``activation_layer`` and Dropout layer.
        bias (bool): Whether to use bias in the linear layer. Default ``True``
        dropout (float): The probability for the dropout layer. Default: 0.0
    """
    def __init__(self, in_channels: int, hidden_channels: list[int], norm_layer: Callable[..., Module] | None = None, activation_layer: Callable[..., Module] | None = ..., inplace: bool | None = None, bias: bool = True, dropout: float = 0.0) -> None: ...

class Permute(Module):
    """This module returns a view of the tensor input with its dimensions permuted.

    Args:
        dims (List[int]): The desired ordering of dimensions
    """
    dims: Incomplete
    def __init__(self, dims: list[int]) -> None: ...
    def forward(self, x: Tensor) -> Tensor: ...

class ShiftedWindowAttention(Module):
    window_size: Incomplete
    shift_size: Incomplete
    num_heads: Incomplete
    attention_dropout: Incomplete
    dropout: Incomplete
    qkv: Incomplete
    proj: Incomplete
    def __init__(self, dim: int, window_size: list[int], shift_size: list[int], num_heads: int, qkv_bias: bool = True, proj_bias: bool = True, attention_dropout: float = 0.0, dropout: float = 0.0) -> None: ...
    relative_position_bias_table: Incomplete
    def define_relative_position_bias_table(self) -> None: ...
    def define_relative_position_index(self) -> None: ...
    def get_relative_position_bias(self): ...
    def forward(self, x: Tensor) -> Tensor:
        """
        Args:
            x (Tensor): Tensor with layout of [B, H, W, C]
        Returns:
            Tensor with same layout as input, i.e. [B, H, W, C]
        """

def stochastic_depth(input: Tensor, p: float, mode: str, training: bool = True) -> Tensor:
    '''
    Implements the Stochastic Depth from `"Deep Networks with Stochastic Depth"
    <https://arxiv.org/abs/1603.09382>`_ used for randomly dropping residual
    branches of residual architectures.

    Args:
        input (Tensor[N, ...]): The input tensor or arbitrary dimensions with the first one
                    being its batch i.e. a batch with ``N`` rows.
        p (float): probability of the input to be zeroed.
        mode (str): ``"batch"`` or ``"row"``.
                    ``"batch"`` randomly zeroes the entire input, ``"row"`` zeroes
                    randomly selected rows from the batch.
        training: apply stochastic depth if is ``True``. Default: ``True``

    Returns:
        Tensor[N, ...]: The randomly zeroed tensor.
    '''

class StochasticDepth(Module):
    """
    See :func:`stochastic_depth`.
    """
    p: Incomplete
    mode: Incomplete
    def __init__(self, p: float, mode: str) -> None: ...
    def forward(self, input: Tensor) -> Tensor: ...

class SwinTransformerBlock(Module):
    """
    Swin Transformer Block.
    Args:
        dim (int): Number of input channels.
        num_heads (int): Number of attention heads.
        window_size (List[int]): Window size.
        shift_size (List[int]): Shift size for shifted window attention.
        mlp_ratio (float): Ratio of mlp hidden dim to embedding dim. Default: 4.0.
        dropout (float): Dropout rate. Default: 0.0.
        attention_dropout (float): Attention dropout rate. Default: 0.0.
        stochastic_depth_prob: (float): Stochastic depth rate. Default: 0.0.
        norm_layer (Module): Normalization layer.  Default: nn.LayerNorm.
        attn_layer (Module): Attention layer. Default: ShiftedWindowAttention
    """
    norm1: Incomplete
    attn: Incomplete
    stochastic_depth: Incomplete
    norm2: Incomplete
    mlp: Incomplete
    def __init__(self, dim: int, num_heads: int, window_size: list[int], shift_size: list[int], mlp_ratio: float = 4.0, dropout: float = 0.0, attention_dropout: float = 0.0, stochastic_depth_prob: float = 0.0, norm_layer: Callable[..., Module] = ..., attn_layer: Callable[..., Module] = ...) -> None: ...
    def forward(self, x: Tensor): ...

class SwinTransformer(Module):
    '''
    Implements Swin Transformer from the `"Swin Transformer: Hierarchical Vision Transformer using
    Shifted Windows" <https://arxiv.org/abs/2103.14030>`_ paper.
    Args:
        patch_size (List[int]): Patch size.
        embed_dim (int): Patch embedding dimension.
        depths (List(int)): Depth of each Swin Transformer layer.
        num_heads (List(int)): Number of attention heads in different layers.
        window_size (List[int]): Window size.
        mlp_ratio (float): Ratio of mlp hidden dim to embedding dim. Default: 4.0.
        dropout (float): Dropout rate. Default: 0.0.
        attention_dropout (float): Attention dropout rate. Default: 0.0.
        stochastic_depth_prob (float): Stochastic depth rate. Default: 0.1.
        num_classes (int): Number of classes for classification head. Default: 1000.
        block (Module, optional): SwinTransformer Block. Default: None.
        norm_layer (Module, optional): Normalization layer. Default: None.
        downsample_layer (Module): Downsample layer (patch merging). Default: PatchMerging.
    '''
    num_classes: Incomplete
    features: Incomplete
    norm: Incomplete
    permute: Incomplete
    avgpool: Incomplete
    flatten: Incomplete
    head: Incomplete
    def __init__(self, patch_size: list[int], embed_dim: int, depths: list[int], num_heads: list[int], window_size: list[int], mlp_ratio: float = 4.0, dropout: float = 0.0, attention_dropout: float = 0.0, stochastic_depth_prob: float = 0.1, num_classes: int = 1000, norm_layer: Callable[..., Module] | None = None, block: Callable[..., Module] | None = None, downsample_layer: Callable[..., Module] = ..., feat_dim: int = 16) -> None: ...
    def forward(self, x): ...

def swin_b(weights=None, **kwargs): ...
