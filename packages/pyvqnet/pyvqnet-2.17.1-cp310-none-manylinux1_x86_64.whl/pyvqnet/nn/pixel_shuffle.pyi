from _typeshed import Incomplete
from pyvqnet.nn import Module as Module
from pyvqnet.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, tensor as tensor

class Pixel_Shuffle(Module):
    '''
    Rearranges elements in a tensor of shape :math:`(*, C \\times r^2, H, W)`
    to a tensor of shape :math:`(*, C, H \\times r, W \\times r)`, where r is an upscale factors.

    :param upscale_factors: factor to increase spatial resolution by
    :param name: name,default is "".
    :return: 
        Pixel_Shuffle Module

    :Example::

        from pyvqnet.nn import Pixel_Shuffle
        from pyvqnet.tensor import tensor
        ps = Pixel_Shuffle(3)
        inx = tensor.ones([5,2,3,18,4,4])
        inx.requires_grad=  True
        y = ps(inx)

    '''
    upscale_factors: Incomplete
    def __init__(self, upscale_factors: int, name: str = '') -> None: ...
    def forward(self, x) -> QTensor: ...

class Pixel_Unshuffle(Module):
    '''
    Reverses the Pixel_Shuffle operation by rearranging elements
        in a tensor of shape :math:`(*, C, H \\times r, W \\times r)` to a tensor of shape
        :math:`(*, C \\times r^2, H, W)`, where r is a downscale factor.

    :param downscale_factors: factor to decrease spatial resolution by.
    :param name: name,default is "".
    
    :return: 
        Pixel_Unshuffle Module

    :Example::

        from pyvqnet.nn import Pixel_Unshuffle
        from pyvqnet.tensor import tensor
        ps = Pixel_Unshuffle(3)
        inx = tensor.ones([5,2,3,2,12,12])
        inx.requires_grad= True
        y = ps(inx)
    '''
    downscale_factors: Incomplete
    def __init__(self, downscale_factors: int, name: str = '') -> None: ...
    def forward(self, x) -> QTensor: ...
