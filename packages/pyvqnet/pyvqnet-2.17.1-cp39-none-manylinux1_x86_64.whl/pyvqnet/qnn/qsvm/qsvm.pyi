from . import swaptest as swaptest
from .data_process import input_normalize as input_normalize
from _typeshed import Incomplete

class InitQMachine:
    m_machine: Incomplete
    def __init__(self, machinetype: str = '') -> None: ...
    def __del__(self) -> None: ...

class QSVM:
    """
    Quantum Support Vector Machine class
    """
    X_origin: Incomplete
    n: Incomplete
    X: Incomplete
    lable: Incomplete
    M: Incomplete
    C: Incomplete
    kernel: Incomplete
    def __init__(self, input_data, labels, c: float = 0.6) -> None:
        """
        Quantum Support Vector Machine class

        :param input_data: train data
        :param labels: train data labels
        :param c: regularization parameter,default = 0.6
        :return: qsvm instance
        """
    def get_matrix(self): ...
    def predict(self, testvec):
        """
        predict on testvec use qsvm model.

        :param testvec: input single sample
        :return: predict result
        """

def cir_test(q_index, q_psi, testvec): ...
def cir_train(q_index, q_psi, x_origin): ...
