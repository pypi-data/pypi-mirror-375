from ..pq3.measure import expval as expval
from _typeshed import Incomplete
from pyvqnet.nn.module import Module as Module
from pyvqnet.tensor import tensor as tensor
from pyvqnet.tensor.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor

CoreTensor: Incomplete

class QLinear(Module):
    """
    Linear module. Inputs to the linear module are of shape (input_channels, output_channels)

    :param input_channels: `int` - Number of input channels
    :param output_channels: `int` - Number of output channels
    :param machine: `str` - cpu simulation
    :return: a quantum linear layer

    exmaple::

        from pyvqnet.qnn.qlinear import QLinear
        import pyvqnet.tensor as tensor
        params = [[0.37454012, 0.95071431, 0.73199394, 0.59865848, 0.15601864, 0.15599452],
                    [1.37454012, 0.95071431, 0.73199394, 0.59865848, 0.15601864, 0.15599452],
                    [1.37454012, 1.95071431, 0.73199394, 0.59865848, 0.15601864, 0.15599452],
                    [1.37454012, 1.95071431, 1.73199394, 1.59865848, 0.15601864, 0.15599452]]

        m = QLinear(6, 2)
        input = tensor.QTensor(params, requires_grad=True)
        output = m(input)
        output.backward()
        print(input.grad)

    """
    machine: Incomplete
    input_channel: Incomplete
    quantum_number: Incomplete
    out_dim: Incomplete
    qlist: Incomplete
    history_expectation: Incomplete
    def __init__(self, input_channels, output_channels, machine: str = 'cpu') -> None: ...
    def forward(self, x: tensor.QTensor): ...

def qlinear_circuit(inputs, qnum, qlist, machine, out_dim):
    """
    qlinear_circuit
    """
