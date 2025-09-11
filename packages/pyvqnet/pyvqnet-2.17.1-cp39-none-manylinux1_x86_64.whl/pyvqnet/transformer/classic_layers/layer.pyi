import pyvqnet.nn as nn
from .format import Format as Format, nchw_to as nchw_to
from _typeshed import Incomplete
from pyvqnet.utils import to_2tuple as to_2tuple
from typing import Callable

class PatchEmbed(nn.Module):
    """ 2D Image to Patch Embedding
    """
    output_fmt: Format
    patch_size: Incomplete
    img_size: Incomplete
    grid_size: Incomplete
    num_patches: Incomplete
    flatten: bool
    strict_img_size: Incomplete
    dynamic_img_pad: Incomplete
    proj: Incomplete
    norm: Incomplete
    def __init__(self, img_size: int | None = 224, patch_size: int = 16, in_chans: int = 3, embed_dim: int = 768, norm_layer: Callable | None = None, flatten: bool = True, output_fmt: str | None = None, bias: bool = True, strict_img_size: bool = True, dynamic_img_pad: bool = False) -> None: ...
    def forward(self, x): ...
