import pyvqnet.nn as nn
import pyvqnet.tensor as tensor
from .utils import permute_12_reshape_b_n_embed_dims as permute_12_reshape_b_n_embed_dims, qkv_split as qkv_split, scaled_dot_product_attention_pyimpl as scaled_dot_product_attention_pyimpl
from _typeshed import Incomplete
from pyvqnet import DEV_CPU as DEV_CPU, kbool as kbool
from pyvqnet.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor
from pyvqnet.utils import to_2tuple as to_2tuple
from pyvqnet.utils.initializer import he_uniform as he_uniform
from typing import Callable

arch_zoo: Incomplete

class AdaptivePadding(nn.Module):
    '''Applies padding adaptively to the input.

    This module can make input get fully covered by filter
    you specified. It support two modes "same" and "corner". The
    "same" mode is same with "SAME" padding mode in TensorFlow, pad
    zero around input. The "corner"  mode would pad zero
    to bottom right.

    :param kernel_size (int | tuple): Size of the kernel. Default: 1.
    :param stride (int | tuple): Stride of the filter. Default: 1.
    :param dilation (int | tuple): Spacing between kernel elements.
        Default: 1.
    :param padding (str): Support "same" and "corner", "corner" mode
        would pad zero to bottom right, and "same" mode would
        pad zero around input. Default: "corner".

    '''
    padding: Incomplete
    kernel_size: Incomplete
    stride: Incomplete
    dilation: Incomplete
    def __init__(self, kernel_size: int = 1, stride: int = 1, dilation: int = 1, padding: str = 'corner') -> None: ...
    def get_pad_shape(self, input_shape):
        """Calculate the padding size of input.

        :param input_shape: arrange as (H, W).

        return:
            Tuple[int]: The padding size along the
            original H and W directions
        """
    def forward(self, x: tensor.QTensor):
        """Add padding to `x`

        :param x: Input tensor has shape (B, C, H, W).

        return:
            QTensor: The tensor with adaptive padding
        """

class PatchEmbed(nn.Module):
    embed_dims: Incomplete
    adaptive_padding: Incomplete
    projection: Incomplete
    norm: Incomplete
    init_input_size: Incomplete
    init_out_size: Incomplete
    def __init__(self, in_channels: int = 3, embed_dims: int = 768, conv_type: str = 'Conv2d', kernel_size: int = 16, stride: int = 16, padding: str = 'corner', dilation: int = 1, bias: bool = True, norm_cfg: Incomplete | None = None, input_size: Incomplete | None = None) -> None: ...
    def forward(self, x):
        """
        :param x (QTensor): Has shape (B, C, H, W). In most case, C is 3.

        return:
            tuple: Contains merged results and its spatial shape.

            - x (QTensor): Has shape (B, out_h * out_w, embed_dims)
            - out_size (tuple[int]): Spatial shape of x, arrange as
            (out_h, out_w).
        """

def resize_pos_embed(pos_embed, src_shape, dst_shape, mode: str = 'bicubic', num_extra_tokens: int = 1): ...
scaled_dot_product_attention = scaled_dot_product_attention_pyimpl

class LayerScale(nn.Module):
    """LayerScale layer.

    :param dim (int): Dimension of input features.
        layer_scale_init_value (float or tensor.QTensor): Init value of layer
            scale. Defaults to 1e-5.
    """
    weight: Incomplete
    def __init__(self, dim: int, layer_scale_init_value: float | tensor.QTensor = 1e-05) -> None: ...
    def forward(self, x): ...

def build_dropout_layer(dict): ...
def build_act_layer(dict): ...
def build_norm_layer(dict, embed_dims: Incomplete | None = None): ...

class MultiheadAttention(nn.Module):
    """Multi-head Attention Module.

    This module implements multi-head attention that supports different input
    dims and embed dims. And it also supports a shortcut from ``value``, which
    is useful if input dims is not the same with embed dims.

    :param embed_dims (int): The embedding dimension.
    :param num_heads (int): Parallel attention heads.
    :param input_dims (int, optional): The input dimension, and if None, use embed_dims. Defaults to None.
    :param attn_drop (float): Dropout rate of the dropout layer after the attention calculation of query and key. Defaults to 0.
    :param proj_drop (float): Dropout rate of the dropout layer after the output projection. Defaults to 0.
    :param dropout_layer (dict): The dropout config before adding the shortcut. Defaults to dict(type='Dropout', drop_prob=0.).
    :param qkv_bias (bool): If True, add a learnable bias to q, k, v. Defaults to True.
    :param qk_scale (float, optional): Override default qk scale of head_dim ** -0.5 if set. Defaults to None.
    :param proj_bias (bool): If True, add a learnable bias to output projection. Defaults to True.
    :param v_shortcut (bool): Add a shortcut from value to output. It's usually used if input_dims is different from embed_dims. Defaults to False.
    :param use_layer_scale (bool): Whether to use layer scale. Defaults to False.
    :param layer_scale_init_value (float or tensor.QTensor): Init value of layer scale. Defaults to 0.

    """
    input_dims: Incomplete
    embed_dims: Incomplete
    num_heads: Incomplete
    v_shortcut: Incomplete
    head_dims: Incomplete
    scaled_dot_product_attention: Incomplete
    qkv: Incomplete
    attn_drop: Incomplete
    proj: Incomplete
    proj_drop: Incomplete
    out_drop: Incomplete
    gamma1: Incomplete
    def __init__(self, embed_dims, num_heads, input_dims: Incomplete | None = None, attn_drop: float = 0.0, proj_drop: float = 0.0, dropout_layer=..., qkv_bias: bool = True, qk_scale: Incomplete | None = None, proj_bias: bool = True, v_shortcut: bool = False, use_layer_scale: bool = False, layer_scale_init_value: float = 0.0) -> None: ...
    def forward(self, x): ...

class MultiheadAttentionSampling(nn.Module):
    """Multi-head Attention Module.

    This module implements multi-head attention that supports different input
    dims and embed dims. And it also supports a shortcut from ``value``, which
    is useful if input dims is not the same with embed dims.

    :param embed_dims (int): The embedding dimension.
    :param num_heads (int): Parallel attention heads.
    :param input_dims (int, optional): The input dimension, and if None, use embed_dims. Defaults to None.
    :param attn_drop (float): Dropout rate of the dropout layer after the attention calculation of query and key. Defaults to 0.
    :param proj_drop (float): Dropout rate of the dropout layer after the output projection. Defaults to 0.
    :param sampling_error (float): quantum state estimation error threshold, default to 0.
    :param dropout_layer (dict): The dropout config before adding the shortcut. Defaults to dict(type='Dropout', drop_prob=0.).
    :param qkv_bias (bool): If True, add a learnable bias to q, k, v. Defaults to True.
    :param qk_scale (float, optional): Override default qk scale of head_dim ** -0.5 if set. Defaults to None.
    :param proj_bias (bool): If True, add a learnable bias to output projection. Defaults to True.
    :param v_shortcut (bool): Add a shortcut from value to output. It's usually used if input_dims is different from embed_dims. Defaults to False.
    :param use_layer_scale (bool): Whether to use layer scale. Defaults to False.
    :param layer_scale_init_value (float or tensor.QTensor): Init value of layer scale. Defaults to 0.
    :param init_cfg (dict, optional): The Config for initialization. Defaults to None.

    """
    input_dims: Incomplete
    embed_dims: Incomplete
    num_heads: Incomplete
    v_shortcut: Incomplete
    head_dims: Incomplete
    scaled_dot_product_attention: Incomplete
    qkv: Incomplete
    attn_drop: Incomplete
    proj: Incomplete
    proj_drop: Incomplete
    out_drop: Incomplete
    gamma1: Incomplete
    def __init__(self, embed_dims, num_heads, input_dims: Incomplete | None = None, attn_drop: float = 0.0, proj_drop: float = 0.0, sampling_error: float = 0.0, dropout_layer=..., qkv_bias: bool = True, qk_scale: Incomplete | None = None, proj_bias: bool = True, v_shortcut: bool = False, use_layer_scale: bool = False, layer_scale_init_value: float = 0.0, init_cfg: Incomplete | None = None) -> None: ...
    def forward(self, x): ...

class LinearFunctionSamplingAutoGrad(nn.Module):
    sampling_error: Incomplete
    backend: Incomplete
    use_bias: Incomplete
    bias: Incomplete
    weights: Incomplete
    def __init__(self, input_channels: int, output_channels: int, weight_initializer: Callable | None = None, bias_initializer: Callable | None = None, use_bias: bool = True, sampling_error: float = 0.005, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x) -> QTensor: ...

class FFN(nn.Module):
    """Implements feed-forward networks (FFNs) with identity connection.

    :param embed_dims (int): The feature dimension. Same as MultiheadAttention. Defaults: 256.
    :param feedforward_channels (int): The hidden dimension of FFNs. Defaults: 1024.
    :param num_fcs (int, optional): The number of fully-connected layers in FFNs. Default: 2.
    :param act_cfg (dict, optional): The activation config for FFNs. Default: dict(type='ReLU')
    :param ffn_drop (float, optional): Probability of an element to be zeroed in FFN. Default 0.0.
    :param add_identity (bool, optional): Whether to add the identity connection. Default: True.
    :param dropout_layer (dict): The dropout_layer used when adding the shortcut.
    :param layer_scale_init_value (float): Initial value of scale factor in LayerScale. Default: 1.0
    """
    embed_dims: Incomplete
    feedforward_channels: Incomplete
    num_fcs: Incomplete
    act_layer: Incomplete
    layers: Incomplete
    dropout_layer: Incomplete
    add_identity: Incomplete
    gamma2: Incomplete
    def __init__(self, embed_dims: int = 256, feedforward_channels: int = 1024, num_fcs: int = 2, act_cfg=..., ffn_drop: float = 0.0, dropout_layer: Incomplete | None = None, add_identity: bool = True, layer_scale_init_value: float = 0.0) -> None: ...
    def forward(self, x, identity: Incomplete | None = None):
        """Forward function for `FFN`.

        The function would add x to the output tensor if residue is None.
        """

class TransformerEncoderLayer(nn.Module):
    """Implements one encoder layer in Vision Transformer.

    Args:
        embed_dims (int): The feature dimension
        num_heads (int): Parallel attention heads
        feedforward_channels (int): The hidden dimension for FFNs
        layer_scale_init_value (float or tensor.QTensor): Init value of layer
            scale. Defaults to 0.
        drop_rate (float): Probability of an element to be zeroed
            after the feed forward layer. Defaults to 0.
        attn_drop_rate (float): The drop out rate for attention output weights.
            Defaults to 0.
        drop_path_rate (float): Stochastic depth rate. Defaults to 0.
        num_fcs (int): The number of fully-connected layers for FFNs.
            Defaults to 2.
        qkv_bias (bool): enable bias for qkv if True. Defaults to True.
        ffn_type (str): Select the type of ffn layers. Defaults to 'origin'.
        act_cfg (dict): The activation config for FFNs.
            Defaults to ``dict(type='GELU')``.
        norm_cfg (dict): Config dict for normalization layer.
            Defaults to ``dict(type='LN')``.
        init_cfg (dict, optional): Initialization config dict.
            Defaults to None.
    """
    embed_dims: Incomplete
    ln1: Incomplete
    sampling: Incomplete
    attn: Incomplete
    ln2: Incomplete
    ffn: Incomplete
    def __init__(self, embed_dims, num_heads, feedforward_channels, layer_scale_init_value: float = 0.0, drop_rate: float = 0.0, attn_drop_rate: float = 0.0, drop_path_rate: float = 0.0, sampling_error: float = 0.0, num_fcs: int = 2, qkv_bias: bool = True, ffn_type: str = 'origin', act_cfg=..., norm_cfg=..., init_cfg: Incomplete | None = None) -> None: ...
    def forward(self, x: tensor.QTensor): ...

class SamplingBlockAutoGrad(nn.Module):
    sampling_error: Incomplete
    def __init__(self, sampling_error, name: str = '') -> None: ...
    def forward(self, x: tensor.QTensor): ...

class VisionTransformerSampling(nn.Module):
    '''
    Vision Transformer use quantum state estimation Sampling

    :param arch (dict): Vision Transformer architecture.If use dict, it should have below keys:
    - embed_dims (int): The dimensions of embedding.
    - num_layers (int): The number of transformer encoder layers.
    - num_heads (int): The number of heads in attention modules.
    - feedforward_channels (int): The hidden dimensions in feedforward modules.
    Defaults to \'base\'.
    :param img_size (int | tuple): The expected input image shape. Because we support dynamic input shape, just set the argument to the most common input image shape. Defaults to 224.
    :param patch_size (int | tuple): The patch size in patch embedding. Defaults to 16.
    :param in_channels (int): The num of input channels. Defaults to 3.
    :param out_indices (Sequence | int): Output from which stages. Defaults to -1, means the last stage.
    :param drop_rate (float): Probability of an element to be zeroed. Defaults to 0.
    :param drop_path_rate (float): stochastic depth rate. Defaults to 0.
    :param qkv_bias (bool): Whether to add bias for qkv in attention modules. Defaults to True.
    :param norm_cfg (dict): Config dict for normalization layer. Defaults to dict(type=\'LN\').
    :param final_norm (bool): Whether to add a additional layer to normalize final feature map. Defaults to True.
    :param out_type (str): The type of output features. Please choose from
    - "cls_token": The class token tensor with shape (B, C).
    Defaults to "cls_token".
    :param with_cls_token (bool): Whether concatenating class token into image tokens as transformer input. Defaults to True.
    :param frozen_stages (int): Stages to be frozen (stop grad and set eval mode). -1 means not freezing any parameters. Defaults to -1.
    :param interpolate_mode (str): Select the interpolate mode for position embeding vector resize. Defaults to "bicubic".
    :param layer_scale_init_value (float or tensor.QTensor): Init value of layer scale. Defaults to 0.
    :param patch_cfg (dict): Configs of patch embeding. Defaults to an empty dict.
    :param layer_cfgs (Sequence | dict): Configs of each transformer layer in encoder. Defaults to an empty dict.
        '''
    num_extra_tokens: int
    arch_settings: Incomplete
    embed_dims: Incomplete
    num_layers: Incomplete
    img_size: Incomplete
    sampling_error: Incomplete
    patch_embed: Incomplete
    patch_resolution: Incomplete
    interpolate_mode: Incomplete
    out_type: Incomplete
    with_cls_token: Incomplete
    cls_token: Incomplete
    pos_embed: Incomplete
    PESampling: Incomplete
    drop_after_pos: Incomplete
    out_indices: Incomplete
    layers: Incomplete
    frozen_stages: Incomplete
    pre_norm: Incomplete
    final_norm: Incomplete
    ln1: Incomplete
    def __init__(self, arch: str = 'base', img_size: int = 224, patch_size: int = 16, in_channels: int = 3, out_indices: int = -1, drop_rate: float = 0.0, drop_path_rate: float = 0.0, sampling_error: float = 0.0, qkv_bias: bool = True, norm_cfg=..., final_norm: bool = True, out_type: str = 'cls_token', with_cls_token: bool = True, frozen_stages: int = -1, interpolate_mode: str = 'bicubic', layer_scale_init_value: float = 0.0, patch_cfg=..., layer_cfgs=..., pre_norm: bool = False, name: str = '') -> None: ...
    def forward(self, x, *args, **kwargs): ...

def binomial_prob_sample(sampling_times: int, probs: tensor.QTensor): ...

class PESamplingAutoGrad(nn.Module):
    sampling_error: Incomplete
    def __init__(self, sampling_error: float = 0.005, name: str = '') -> None: ...
    def forward(self, x: tensor.QTensor, pos_para: tensor.QTensor):
        """
        dummy impl for pe sample
        """

class VisionTransformerClsHeadSampling(nn.Module):
    in_channels: Incomplete
    num_classes: Incomplete
    hidden_dim: Incomplete
    act_cfg: Incomplete
    sampling: Incomplete
    def __init__(self, num_classes: int, in_channels: int, sampling_error: float, hidden_dim: int | None = None, act_cfg: dict = ..., init_cfg: dict = ..., **kwargs) -> None: ...
    def pre_logits(self, feats: tuple[list[tensor.QTensor]]) -> tensor.QTensor:
        """The process before the final classification head.

        The input ``feats`` is a tuple of list of tensor, and each tensor is
        the feature of a backbone stage. In ``VisionTransformerClsHead``, we
        obtain the feature of the last stage and forward in hidden layer if
        exists.
        """
    def forward(self, feats: tuple[list[tensor.QTensor]]) -> tensor.QTensor:
        """The forward process."""

class e2e_qvit_cls(nn.Module):
    """
    end to end quantum vision transformer with classification task impl.

    :param img_size: image size.
    :param sampling_error: quantum state estimation sampling error.
    :param num_classes: number of classes for classification task.
    :param drop_rate: drop_rate for all dropout layer.
    :param loss_func: loss function.
    """
    backbone: Incomplete
    head: Incomplete
    loss_func: Incomplete
    def __init__(self, img_size, sampling_error, num_classes, in_channels, drop_rate, loss_func) -> None: ...
    def predict(self, x): ...
    def forward(self, x, gt_label):
        """
        input ground true label and input to calculate loss.

        :param x: input.
        :param gt_label: ground true label.

        :return:
            loss QTensor.
        """
    def loss(self, pred, label): ...
