from .circuit import CirCuit_QGRU as CirCuit_QGRU
from _typeshed import Incomplete
from pyvqnet.nn.linear import Linear as Linear
from pyvqnet.nn.module import Module as Module, Parameter as Parameter
from pyvqnet.qnn.vqc import PauliZ as PauliZ, QMachine as QMachine, cnot as cnot, rx as rx, ry as ry, rz as rz
from pyvqnet.qnn.vqc.qmeasure import expval as expval
from pyvqnet.tensor import tensor as tensor
from pyvqnet.utils.initializer import quantum_uniform as quantum_uniform

class QGRU(Module):
    '''
    QGRU module. A quantum-enhanced version of the GRU (Gated Recurrent Unit) that leverages quantum circuits for state updates and memory retention. Inputs to the QGRU module are of shape (batch_size, seq_length, feature_size).


    Example::
            import numpy as np
            from pyvqnet.tensor import tensor
            from pyvqnet.qnn.qgru.qgru import QGRU
            from pyvqnet.dtype import *
            # Example usage
            if __name__ == "__main__":
                # Set parameters
                para_num = 8
                num_of_qubits = 8
                input_size = 4
                hidden_size = 4
                batch_size = 1
                seq_length = 1
                # Create QGRU model
                qgru = QGRU(para_num, num_of_qubits, input_size, hidden_size, batch_first=True)

                # Create input data
                x = tensor.QTensor(np.random.randn(batch_size, seq_length, input_size), dtype=kfloat32)

                # Call the model
                output, h_t = qgru(x)

                print("Output shape:", output.shape)  # Output shape
                print("h_t shape:", h_t.shape)  # Final hidden state shape

    '''
    input_size: Incomplete
    hidden_size: Incomplete
    concat_size: Incomplete
    n_qubits: Incomplete
    batch_first: Incomplete
    para_num: Incomplete
    num_of_qubits: Incomplete
    clayer_in: Incomplete
    VQC_reset: Incomplete
    VQC_update: Incomplete
    VQC_output: Incomplete
    clayer_out: Incomplete
    def __init__(self, para_num, num_of_qubits: int = 4, input_size: int = 100, hidden_size: int = 100, batch_first: bool = True) -> None:
        """

        :param para_num: `int` - The number of parameters in the quantum circuit.
        :param num_of_qubits: `int` - The number of qubits.
        :param input_size: `int` - The feature dimension of the QGRU input data.
        :param hidden_size: `int` - Dimension of the hidden units of the QGRU.
        :param batch_first: `bool` - Whether the input first dimension of the QGRU is the number of batches.

        """
    def forward(self, x, init_states=None):
        """
        x.shape is (batch_size, seq_length, feature_size)
        recurrent_activation -> sigmoid
        activation -> tanh
        """
