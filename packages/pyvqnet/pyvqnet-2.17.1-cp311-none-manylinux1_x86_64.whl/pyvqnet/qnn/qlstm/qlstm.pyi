from .circuit import CirCuit_QLSTM as CirCuit_QLSTM
from _typeshed import Incomplete
from pyvqnet.nn.linear import Linear as Linear
from pyvqnet.nn.module import Module as Module, Parameter as Parameter
from pyvqnet.tensor import tensor as tensor

class QLSTM(Module):
    '''
    QLSTM module. Inputs to the qlstm module are of shape (batch_size, seq_length, feature_size)


    Exmaple::
        import numpy as np
        from pyvqnet.tensor import tensor
        from pyvqnet.qnn.qlstm import QLSTM
        from pyvqnet.dtype import *
        if __name__ == "__main__":
            para_num = 4
            num_of_qubits = 4
            input_size = 4
            hidden_size = 20
            batch_size = 3
            seq_length = 5
            qlstm = QLSTM(para_num, num_of_qubits, input_size, hidden_size, batch_first=True)
            x = tensor.QTensor(np.random.randn(batch_size, seq_length, input_size), dtype=kfloat32)

            output, (h_t, c_t) = qlstm(x)

            print("Output shape:", output.shape)
            print("h_t shape:", h_t.shape)
            print("c_t shape:", c_t.shape)



    '''
    input_size: Incomplete
    hidden_size: Incomplete
    concat_size: Incomplete
    n_qubits: Incomplete
    batch_first: Incomplete
    para_num: Incomplete
    num_of_qubits: Incomplete
    clayer_in: Incomplete
    VQC_forget: Incomplete
    VQC_input: Incomplete
    VQC_update: Incomplete
    VQC_output: Incomplete
    clayer_out: Incomplete
    def __init__(self, para_num, num_of_qubits: int = 4, input_size: int = 100, hidden_size: int = 100, batch_first: bool = True) -> None:
        """

        :param para_num: `int` - The number of parameters in the quantum circuit.
        :param num_of_qubits: `int` - The number of qubits.
        :param input_size: `int` - The feature dimension of the QLSTM input data.
        :param hidden_size: `int` - Dimension of the hidden units of the QLSTM.
        :param batch_first: `bool` - Whether the input first dimension of the QLSTM is the number of batches.

        """
    def forward(self, x, init_states=None):
        """
        x.shape is (batch_size, seq_length, feature_size)
        recurrent_activation -> sigmoid
        activation -> tanh
        """
