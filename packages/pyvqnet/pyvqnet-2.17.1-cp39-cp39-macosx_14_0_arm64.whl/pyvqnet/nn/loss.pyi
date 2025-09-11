from _typeshed import Incomplete
from pyvqnet.nn import Module as Module
from pyvqnet.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, tensor as tensor

class Loss(Module):
    """
    Loss Class
    """
    ComputeLoss: Incomplete
    loss_type: Incomplete
    output: Incomplete
    target: Incomplete
    def __init__(self, name: str = '') -> None: ...
    def loss_forward(self, target, output) -> QTensor:
        """
        loss forward compute.

        :param target: ground truth data.
        :param output: output data.

        :return: loss data.
        """
    def __call__(self, target, output) -> QTensor:
        """
        loss forward compute.

        :param target: ground truth data.
        :param output: output data.

        :return: loss data.
        """
    def forward(self, target, output) -> QTensor:
        """
        loss forward compute.

        :param target: ground truth data.
        :param output: output data.

        :return: loss data.
        """

class MeanSquaredError(Loss):
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

    Example::

            target = QTensor([[0, 0, 1, 0, 0, 0, 0, 0, 0, 0]], requires_grad=True)
            output = QTensor([[0.1, 0.05, 0.7, 0, 0.05, 0.1, 0, 0, 0, 0]], requires_grad=True)

            loss_result = loss.MeanSquaredError()
            result = loss_result(target, output)
            result.backward()

    '''
    ComputeLoss: Incomplete
    loss_type: str
    def __init__(self, name: str = '') -> None: ...

class CategoricalCrossEntropy(Loss):
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

    Example::

        from pyvqnet.tensor import QTensor
        from pyvqnet import kfloat32,kint64
        from pyvqnet.nn import CategoricalCrossEntropy
        x = QTensor([[1, 2, 3, 4, 5],
        [1, 2, 3, 4, 5],
        [1, 2, 3, 4, 5]], requires_grad=True,dtype=kfloat32)
        y = QTensor([[0, 1, 0, 0, 0], [0, 1, 0, 0, 0], [1, 0, 0, 0, 0]], requires_grad=False,dtype=kint64)
        loss_result = CategoricalCrossEntropy()
        result = loss_result(y, x)
        print(result)

    '''
    ComputeLoss: Incomplete
    loss_type: str
    def __init__(self, name: str = '') -> None: ...

class SoftmaxCrossEntropy(Loss):
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

    Example::

        from pyvqnet.tensor import QTensor
        from pyvqnet import kfloat32, kint64
        from pyvqnet.nn import SoftmaxCrossEntropy
        x = QTensor([[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]],
                    requires_grad=True,
                    dtype=kfloat32)
        y = QTensor([[0, 1, 0, 0, 0], [0, 1, 0, 0, 0], [1, 0, 0, 0, 0]],
                    requires_grad=False,
                    dtype=kint64)
        loss_result = SoftmaxCrossEntropy()
        result = loss_result(y, x)
        result.backward()
        print(result)

    '''
    ComputeLoss: Incomplete
    loss_type: str
    def __init__(self, name: str = '') -> None: ...

class BinaryCrossEntropy(Loss):
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

    Example::

        from pyvqnet.tensor import QTensor
        from pyvqnet.nn import BinaryCrossEntropy
        x = QTensor([[0.3, 0.7, 0.2], [0.2, 0.3, 0.1]], requires_grad=True)
        y = QTensor([[0.0, 1.0, 0], [0.0, 0, 1]], requires_grad=False)

        loss_result = BinaryCrossEntropy()
        result = loss_result(y, x)
        result.backward()
        print(result)

    '''
    ComputeLoss: Incomplete
    loss_type: str
    def __init__(self, name: str = '') -> None: ...

class NLL_Loss(Loss):
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

    Example::

        from pyvqnet.tensor import QTensor
        from pyvqnet import kint64
        from pyvqnet.nn import NLL_Loss

        x = QTensor([
            0.9476322568516703, 0.226547421131723, 0.5944201443911326,
            0.42830868492969476, 0.76414068655387, 0.00286059168094277,
            0.3574236812873617, 0.9096948856639084, 0.4560809854582528,
            0.9818027091583286, 0.8673569904602182, 0.9860275114020933,
            0.9232667066664217, 0.303693313961628, 0.8461034903175555
        ])
        x=x.reshape([1, 3, 1, 5])
        x.requires_grad = True
        y = QTensor([[[2, 1, 0, 0, 2]]], dtype=kint64)

        loss_result = NLL_Loss()
        result = loss_result(y, x)
        print(result)

    '''
    ComputeLoss: Incomplete
    loss_type: str
    def __init__(self, name: str = '') -> None: ...

class CrossEntropyLoss(Loss):
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

    Example::

        from pyvqnet.tensor import QTensor, kint64
        from pyvqnet.nn import CrossEntropyLoss
        x = QTensor([
            0.9476322568516703, 0.226547421131723, 0.5944201443911326,
            0.42830868492969476, 0.76414068655387, 0.00286059168094277,
            0.3574236812873617, 0.9096948856639084, 0.4560809854582528,
            0.9818027091583286, 0.8673569904602182, 0.9860275114020933,
            0.9232667066664217, 0.303693313961628, 0.8461034903175555
        ])
        x=x.reshape([1, 3, 1, 5])
        x.requires_grad = True
        y = QTensor([[[2, 1, 0, 0, 2]]], dtype=kint64)

        loss_result = CrossEntropyLoss()
        result = loss_result(y, x)
        print(result)
    '''
    ComputeLoss: Incomplete
    loss_type: str
    def __init__(self, name: str = '') -> None: ...
    def __call__(self, target, output) -> QTensor:
        """
        loss forward compute.

        :param target: ground truth data.
        :param output: output data.

        :return: loss data.
        """

class fidelityLoss(Loss):
    """
    FidelityLoss
    """
    ComputeLoss: Incomplete
    loss_type: str
    def __init__(self, name: str = '') -> None: ...
    def loss_forward(self, output) -> QTensor:
        """
        loss forward compute.

        :param output: output data.

        :return: loss data.
        """
    def __call__(self, output):
        """
        loss forward compute.

        :param output: output data.

        :return: loss data.
        """

class qgrnnLoss(Loss):
    """
    loss function for qgrnn
    """
    ComputeLoss: Incomplete
    loss_type: str
    def __init__(self, name: str = '') -> None: ...
    def loss_forward(self, output) -> QTensor: ...
    def __call__(self, output) -> QTensor: ...
