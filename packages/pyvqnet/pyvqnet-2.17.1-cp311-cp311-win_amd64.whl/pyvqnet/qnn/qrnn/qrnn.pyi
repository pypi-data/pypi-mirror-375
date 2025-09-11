from .circuit import CirCuit_QRNN as CirCuit_QRNN
from _typeshed import Incomplete
from pyvqnet.nn.linear import Linear as Linear
from pyvqnet.nn.module import Module as Module
from pyvqnet.tensor import tensor as tensor

class QRNN(Module):
    '''
    QRNN is a type of Quantum Recurrent Neural Network designed to process sequential data and capture long-term dependencies in the sequence.

        
    Exmaple::
            from pyvqnet.dtype import *

            if __name__ == "__main__":

                para_num = 8
                num_of_qubits = 8
                input_size = 4
                hidden_size = 4
                batch_size = 1
                seq_length = 1
                qrnn = QRNN(para_num, num_of_qubits, input_size, hidden_size, batch_first=True)

                x = tensor.QTensor(np.random.randn(batch_size, seq_length, input_size), dtype=kfloat32)

                output, h_t = qrnn(x)

                print("Output shape:", output.shape)
                print("h_t shape:", h_t.shape)

    '''
    input_size: Incomplete
    hidden_size: Incomplete
    concat_size: Incomplete
    n_qubits: Incomplete
    batch_first: Incomplete
    para_num: Incomplete
    num_of_qubits: Incomplete
    clayer_in: Incomplete
    VQC_hidden: Incomplete
    clayer_out: Incomplete
    def __init__(self, para_num, num_of_qubits: int = 4, input_size: int = 100, hidden_size: int = 100, batch_first: bool = True) -> None:
        """
        :param para_num: `int` - The number of parameters in the quantum circuit.
        :param num_of_qubits: `int` - The number of qubits.
        :param input_size: `int` - The feature dimension of the QRNN input data.
        :param hidden_size: `int` - Dimension of the hidden units of the QRNN.
        :param batch_first: `bool` - Whether the input first dimension of the QRNN is the number of batches.
        """
    def forward(self, x, init_states=None):
        """
        x.shape is (batch_size, seq_length, feature_size)
        activation -> tanh
        """
