import abc
from _typeshed import Incomplete
from abc import abstractmethod
from pyvqnet.nn.module import Module as Module
from pyvqnet.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, tensor as tensor

class Activation(Module, metaclass=abc.ABCMeta):
    """
        Base class of activation. Specific activation functions inherit this class.
    """
    @abstractmethod
    def __init__(self, name: str = ''): ...
    def forward(self, x) -> QTensor: ...
    def __call__(self, x) -> QTensor: ...

class Gelu(Activation):
    """Applies the Gaussian Error Linear Units function:

    .. math:: \\text{GELU}(x) = x * \\Phi(x)

    When the approximate argument is 'tanh', Gelu is estimated with:

    .. math:: \\text{GELU}(x) = 0.5 * x * (1 + \\text{Tanh}(\\sqrt{2 / \\pi} * (x + 0.044715 * x^3)))

    :param approximate (str, optional): the gelu approximation algorithm to use:
            ``'none'`` | ``'tanh'``. Default: ``'tanh'``

    Examples::

        from pyvqnet.tensor import randu, ones_like
        from pyvqnet.nn import Gelu
        qa = randu([5,4])
        qb = Gelu()(qa)
        
    """
    approximate: Incomplete
    def __init__(self, approximate: str = 'tanh', name: str = '') -> None: ...
GeLU = Gelu

class SiLU(Activation):
    """

    Applies the Sigmoid Linear Unit (SiLU) function, element-wise.
        The SiLU function is also known as the swish function.

        .. math::
            \\text{silu}(x) = x * \\sigma(x), \\text{where } \\sigma(x) \\text{ is the logistic sigmoid.}
    """
    def __init__(self, name: str = '') -> None: ...
    def forward(self, x): ...

class Sigmoid(Activation):
    '''\\\n        Apply a sigmoid activation function to the given input.

        .. math::
            \\text{Sigmoid}(x) = \\frac{1}{1 + \\exp(-x)}

    

        :param name: name of module,default:"".
        :return: sigmoid Activation layer

        Examples::

            from pyvqnet.nn import Sigmoid
            from pyvqnet.tensor import QTensor
            layer = Sigmoid()
            y = layer(QTensor([1.0, 2.0, 3.0, 4.0]))
            print(y)

    '''
    def __init__(self, name: str = '') -> None: ...

class Softplus(Activation):
    '''\\\n        Apply the softplus activation function to the given input.

        .. math::
            \\text{Softplus}(x) = \\log(1 + \\exp(x))


        :param name: name of module,default:"".

        :return: softplus Activation layer

        Examples::

            from pyvqnet.nn import Softplus
            from pyvqnet.tensor import QTensor
            layer = Softplus()
            y = layer(QTensor([1.0, 2.0, 3.0, 4.0]))
            print(y)

    '''
    def __init__(self, name: str = '') -> None: ...

class Softsign(Activation):
    '''\\\n        Apply the softsign activation function to the given input.

        .. math::
            \\text{SoftSign}(x) = \\frac{x}{ 1 + |x|}

        :param name: name of module,default:"".

        :return: softsign Activation layer

        Examples::

            from pyvqnet.nn import Softsign
            from pyvqnet.tensor import QTensor
            layer = Softsign()
            y = layer(QTensor([1.0, 2.0, 3.0, 4.0]))
            print(y)


    '''
    def __init__(self, name: str = '') -> None: ...

class Softmax(Activation):
    '''\\\n    Apply a softmax activation function to the given input.

    .. math::
        \\text{Softmax}(x_{i}) = \\frac{\\exp(x_i)}{\\sum_j \\exp(x_j)}


    :param axis: dimension on which to operate (-1 for last axis)
    :param name: name of module,default:"".

    :return: softmax Activation layer

    Examples::

        from pyvqnet.nn import Softmax
        from pyvqnet.tensor import QTensor
        layer = Softmax()
        y = layer(QTensor([1.0, 2.0, 3.0, 4.0]))
        print(y)

    '''
    def __init__(self, axis: int = -1, dtype: int | None = None, name: str = '') -> None: ...

class HardSigmoid(Activation):
    '''\\\n    Apply a hard sigmoid activation function to the given input.

    .. math::
        \\text{Hardsigmoid}(x) = \\begin{cases}
            0 & \\text{ if } x \\le -3, \\\\\n            1 & \\text{ if } x \\ge +3, \\\\\n            x / 6 + 1 / 2 & \\text{otherwise}
        \\end{cases}

    :param name: name of module,default:"".

    :return: hard sigmoid Activation layer

    Examples::

        from pyvqnet.nn import HardSigmoid
        from pyvqnet.tensor import QTensor
        layer = HardSigmoid()
        y = layer(QTensor([1.0, 2.0, 3.0, 4.0]))
        print(y)

    '''
    def __init__(self, name: str = '') -> None: ...

class ReLu(Activation):
    '''\\\n    Apply a rectified linear unit activation function to the given input.

    .. math::
        \\text{ReLu}(x) = \\begin{cases}
        x, & \\text{ if } x > 0\\\\\n        0, & \\text{ if } x \\leq 0
        \\end{cases}


    :param name: name of module,default:"".
    
    :return: ReLu Activation layer

    Examples::

        from pyvqnet.nn import ReLu
        from pyvqnet.tensor import QTensor
        layer = ReLu()
        y = layer(QTensor([-1, 2.0, -3, 4.0]))
        print(y)

    '''
    def __init__(self, name: str = '') -> None: ...
ReLU = ReLu

class LeakyReLu(Activation):
    '''\\\n    Apply the leaky version of a rectified linear unit activation
    function to the given input.

    .. math::
        \\text{LeakyRelu}(x) =
        \\begin{cases}
        x, & \\text{ if } x \\geq 0 \\\\\n        \\alpha * x, & \\text{ otherwise }
        \\end{cases}

    :param alpha: LeakyRelu coefficient, default: 0.01
    :param name: name of module,default:"".

    :return: leaky ReLu Activation layer

    Examples::

        from pyvqnet.nn import LeakyReLu
        from pyvqnet.tensor import QTensor
        layer = LeakyReLu()
        y = layer(QTensor([-1, 2.0, -3, 4.0]))
        print(y)


    '''
    def __init__(self, alpha: float = 0.01, name: str = '') -> None: ...

class ELU(Activation):
    '''\\\n    Apply the exponential linear unit activation function to the given input.

    .. math::
        \\text{ELU}(x) = \\begin{cases}
        x, & \\text{ if } x > 0\\\\\n        \\alpha * (\\exp(x) - 1), & \\text{ if } x \\leq 0
        \\end{cases}

    :param alpha: Elu coefficient, default: 1.0
    :param name: name of module,default:"".

    :return: Elu Activation layer

    Examples::

        from pyvqnet.nn import ELU
        from pyvqnet.tensor import QTensor
        layer = ELU()
        y = layer(QTensor([-1, 2.0, -3, 4.0]))
        print(y)

    '''
    def __init__(self, alpha: float = 1.0, name: str = '') -> None: ...

class Tanh(Activation):
    '''\\\n    Apply the hyperbolic tangent activation function to the given input.

    .. math::
        \\text{Tanh}(x) = \\frac{\\exp(x) - \\exp(-x)} {\\exp(x) + \\exp(-x)}



    :param name: name of module,default:"".

    :return: hyperbolic tangent Activation layer

    Examples::

        from pyvqnet.nn import Tanh
        from pyvqnet.tensor import QTensor
        layer = Tanh()
        y = layer(QTensor([-1, 2.0, -3, 4.0]))
        print(y)


    '''
    def __init__(self, name: str = '') -> None: ...
