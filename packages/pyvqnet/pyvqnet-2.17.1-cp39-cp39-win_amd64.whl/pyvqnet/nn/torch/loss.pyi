from ...backends import global_backend as global_backend
from ...tensor import QTensor as QTensor, argmax as argmax, to_tensor as to_tensor
from .module import TorchModule as TorchModule
from pyvqnet.backends_mock import TorchMock as TorchMock

class MeanSquaredError(TorchModule):
    '''
    Creates a criterion that measures the mean squared error (squared L2 norm) between
    each element in the input :math:`x` and target :math:`y`.

    The unreduced loss can be described as:

    .. math::
        \\ell(x, y) = L = \\{l_1,\\dots,l_N\\}^\\top, \\quad
        l_n = \\left( x_n - y_n \\right)^2,

    where :math:`N` is the batch size. , then:

    .. math::
        \\ell(x, y) =
            \\operatorname{mean}(L)


    :math:`x` and :math:`y` are tensors of arbitrary shapes with a total
    of :math:`n` elements each.

    The mean operation still operates over all the elements, and divides by :math:`n`.

    :param target: :math:`(N, )`, same shape as the output
    :param output: :math:`(N, )`
    :param name: name of module,default:"".

    :return: a MeanSquaredError class
    '''
    loss_type: str
    def __init__(self, name: str = '') -> None: ...
    def forward(self, target, output): ...
TorchMeanSquaredError = MeanSquaredError

class CategoricalCrossEntropy(TorchModule):
    '''
    This criterion combines LogSoftmax and NLLLoss in one single class.

    The loss can be described as:

    .. math::
        \\text{loss}(x, class) = -\\log\\left(\\frac{\\exp(x[class])}{\\sum_j \\exp(x[j])}\\right)
                       = -x[class] + \\log\\left(\\sum_j \\exp(x[j])\\right)

    :param target: :math:`(N, *)`, same shape as the output
    :param output: :math:`(N, *)` where :math:`*` means, any number of additional
          dimensions
    :param name: name of module,default:"".

    :return: a CategoricalCrossEntropy class

 

    '''
    loss_type: str
    def __init__(self, name: str = '') -> None: ...
    def forward(self, target, output): ...
TorchCategoricalCrossEntropy = CategoricalCrossEntropy

class SoftmaxCrossEntropy(TorchModule):
    '''
    This criterion combines LogSoftmax and NLLLoss in one single class with more numeral stablity.

    The loss can be described as:

    .. math::
        \\text{loss}(x, class) = -\\log\\left(\\frac{\\exp(x[class])}{\\sum_j \\exp(x[j])}\\right)
                       = -x[class] + \\log\\left(\\sum_j \\exp(x[j])\\right)

    :param target: :math:`(N, *)`, same shape as the output
    :param output: :math:`(N, *)` where :math:`*` means, any number of additional
          dimensions
    :param name: name of module,default:"".

    :return: a SoftmaxCrossEntropy class

 

    '''
    loss_type: str
    def __init__(self, name: str = '') -> None: ...
    def forward(self, target, output): ...
TorchSoftmaxCrossEntropy = SoftmaxCrossEntropy

class BinaryCrossEntropy(TorchModule):
    '''
    measures the Binary Cross Entropy between the target and the output:

    The unreduced loss can be described as:

    .. math::
        \\ell(x, y) = L = \\{l_1,\\dots,l_N\\}^\\top, \\quad
        l_n = - w_n \\left[ y_n \\cdot \\log x_n + (1 - y_n) \\cdot \\log (1 - x_n) \\right],

    where :math:`N` is the batch size.

    .. math::
        \\ell(x, y) = \\operatorname{mean}(L)

    :param target: :math:`(N, *)`, same shape as the input
    :param output: :math:`(N, *)` where :math:`*` means, any number of additional
          dimensions
    :param name: name of module,default:"".

    :return: a BinaryCrossEntropy class
    '''
    loss_type: str
    def __init__(self, name: str = '') -> None: ...
    def forward(self, target, output): ...
TorchBinaryCrossEntropy = BinaryCrossEntropy

class NLL_Loss(TorchModule):
    '''The average negative log likelihood loss. It is useful to train a classification
        problem with `C` classes.

        If provided, the optional argument :attr:`weight` should be a 1D Tensor assigning
        weight to each of the classes. This is particularly useful when you have an
        unbalanced training set.

        The `output` given through a forward call is expected to contain
        log-probabilities of each class. `output` has to be a Tensor of size either
        :math:`(minibatch, C)` or :math:`(minibatch, C, d_1, d_2, ..., d_K)`
        with :math:`K \\geq 1` for the `K`-dimensional case.
        The `target` that this loss expects should be a class index in the range :math:`[0, C-1]`
            where `C = number of classes`

    .. math::

        \\ell(output, target) = L = \\{l_1,\\dots,l_N\\}^\\top, \\quad
        l_n = -  
            \\sum_{n=1}^N \\frac{1}{N}output_{n,target_n}, \\quad

    :param target: :math:`(N, *)`, same shape as the output
    :param output: :math:`(N, *)` where :math:`*` means, any number of additional
          dimensions
    :param name: name of module,default:"".

    :return: a NLL_Loss class
    '''
    loss_type: str
    def __init__(self, name: str = '') -> None: ...
    def forward(self, target, output): ...
TorchNLL_Loss = NLL_Loss

class CrossEntropyLoss(TorchModule):
    '''This criterion combines LogSoftmax and NLLLoss in one single class.

    The `output` is expected to contain raw, unnormalized scores for each class.
        `output` has to be a Tensor of size :math:`(C)` for unbatched input,
        :math:`(minibatch, C)` or :math:`(minibatch, C, d_1, d_2, ..., d_K)` with :math:`K \\geq 1` for the
        `K`-dimensional case.
    The loss can be described as:

    .. math::
        \\text{loss}(x, class) = -\\log\\left(\\frac{\\exp(x[class])}{\\sum_j \\exp(x[j])}\\right)
                       = -x[class] + \\log\\left(\\sum_j \\exp(x[j])\\right)

    :param target: :math:`(N, *)`, same shape as the output
    :param output: :math:`(N, *)` where :math:`*` means, any number of additional
          dimensions
    :param name: name of module,default:"".
    '''
    loss_type: str
    def __init__(self, name: str = '') -> None: ...
    def forward(self, target, output): ...
TorchCrossEntropyLoss = CrossEntropyLoss
