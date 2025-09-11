from ..backends import check_not_default_backend as check_not_default_backend, get_backend as get_backend, global_backend as global_backend
from ..tensor import mul as mul, randu as randu, to_tensor as to_tensor, where as where, zeros as zeros

def adaptive_avg_pool2d(x, size): ...
def linear(x, w, b):
    """
    x@w.transpose()+b
    """
def softmax(x, axis): ...
def dropout(x, p: float = 0.5, training: bool = True): ...
def functional_conv2d(x, weight, bias, stride=(1, 1), padding=(0, 0), dilation=(1, 1), groups: int = 1):
    """
    Applies a 2D convolution over an input image composed of several input planes.

    :param x: 4d input tensor.
    :param weight: 4d kernel tensor.
    :param weight: 4d kernel tensor.
    
    :param stride: `tuple` - Stride, defaults to (1, 1)
    :param padding: Padding, controls the amount of padding of the input. It can be either a string {‘valid’, ‘same’} or a tuple of ints giving the amount of implicit padding applied on the input,defaults to (0,0)
    :param dilation_rate: `tuple` - Spacing between kernel elements. Default: (1,1)
    :param group: `int` - Number of group. Default: 1

    :return: output QTensor

    Examples::

        from pyvqnet.nn.functional import functional_conv2d
        from pyvqnet.tensor import arange,ones
        from pyvqnet import kfloat32
        from pyvqnet.nn import Module,Parameter


        class TM(Module):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.w = ones([5,4,2,2])
                self.w.requires_grad = True
                self.b = ones([5,])
                self.b.requires_grad = True

            def forward(self,x):
                weight, bias,   = self.w, self.b 
                return functional_conv2d(x, weight, bias )


        x = arange(0,7*4*12*12,dtype=kfloat32).reshape([7,4,12,12])
        l = TM()
        y = l(x)

        y.backward( )
    """
