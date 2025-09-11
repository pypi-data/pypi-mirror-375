from ...tensor import to_tensor as to_tensor
from ..interpolate import Interpolate as NInterpolate
from .module import TorchModule as TorchModule
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock

class Interpolate(TorchModule, NInterpolate):
    '''The interface is consistent with PyTorch.    
    
    The documentation is referenced from: https://pytorch.org/docs/1.10/_modules/torch/nn/functional.html#interpolate.

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.


    Down/up samples the input to either the given :attr:`size` or the given
    :attr:`scale_factor`.

    The algorithm used for interpolation is determined by :attr:`mode`.Currently only supports data with a 4-D input.

    The input dimensions are interpreted in the form: `mini-batch x channels x height x width`.
    The modes available for resizing are: `nearest`, `bilinear`, `bicubic`.

    :param size: output spatial size.
    :param scale_factor: multiplier for spatial size. Has to match input size if it is a tuple.
    :param mode: algorithm used for upsampling: ``\'nearest\'`` | ``\'bilinear\'`` | ``\'bicubic\'``.
    :param align_corners: Geometrically, we consider the pixels of the
            input and output as squares rather than points.
            If set to ``True``, the input and output tensors are aligned by the
            center points of their corner pixels, preserving the values at the corner pixels.
            If set to ``False``, the input and output tensors are aligned by the corner
            points of their corner pixels, and the interpolation uses edge value padding
            for out-of-boundary values, making this operation *independent* of input size
            when :attr:`scale_factor` is kept the same. This only has an effect when :attr:`mode`
            is ``\'bilinear\'``.
            Default: ``False``
    :param recompute_scale_factor: recompute the scale_factor for use in the
            interpolation calculation.  When `scale_factor` is passed as a parameter, it is used
            to compute the `output_size`.
    :param name: name of module,default:"".
    
    .. note::
        With ``mode=\'bicubic\'``, it\'s possible to cause overshoot, in other words it can produce
        negative values or values greater than 255 for images.
        Explicitly call ``result.clamp(min=0, max=255)`` if you want to reduce the overshoot
        when displaying the image.

    .. warning::
        With ``align_corners = True``, the linearly interpolating modes
        (`linear`, `bilinear`, and `trilinear`) don\'t proportionally align the
        output and input pixels, and thus the output values can depend on the
        input size. This was the default behavior for these modes up to version
        0.3.1. Since then, the default behavior is ``align_corners = False``.
        See :class:`~torch.nn.Upsample` for concrete examples on how this
        affects the outputs.

    .. warning::
        When scale_factor is specified, if recompute_scale_factor=True,
        scale_factor is used to compute the output_size which will then
        be used to infer new scales for the interpolation.
    '''
    def __init__(self, size: int | tuple[int, ...] | None = None, scale_factor: float | tuple[float, ...] | None = None, mode: str = 'nearest', align_corners: bool | None = None, recompute_scale_factor: bool | None = None, name: str = '') -> None: ...
    align_corners: Incomplete
    def forward(self, x): ...
