from ... import nn as nn
from ..._core import vqnet as vqnet
from ...dtype import kbool as kbool
from ...tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, arange as arange, permute as permute, reshape as reshape, tensor as tensor
from _typeshed import Incomplete

def permute_12_reshape_b_n_embed_dims(input, B, N, embed_dims): ...
def get_1d_sincos_temp_embed(embed_dim, length): ...
def get_2d_sincos_pos_embed(embed_dim, grid_size, cls_token: bool = False, extra_tokens: int = 0):
    """
    grid_size: int of the grid height and width
    return:
    pos_embed: [grid_size*grid_size, embed_dim] or [1+grid_size*grid_size, embed_dim] (w/ or w/o cls_token)
    """
def get_2d_sincos_pos_embed_from_grid(embed_dim, grid): ...
def get_1d_sincos_pos_embed_from_grid(embed_dim, pos):
    """
    embed_dim: output dimension for each position
    pos: a list of positions to be encoded: size (M,)
    out: (M, D)
    """
def qkv_split(qkv, B, N, num_heads, head_dims): ...
def scaled_dot_product_attention_pyimpl(query, key, value, attn_mask: Incomplete | None = None, dropout_p: float = 0.0, scale: Incomplete | None = None, is_causal: bool = False): ...
