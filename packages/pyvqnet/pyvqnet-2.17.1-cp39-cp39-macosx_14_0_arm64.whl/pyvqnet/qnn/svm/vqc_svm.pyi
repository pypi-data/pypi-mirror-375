import numpy as np
from _typeshed import Incomplete
from pyvqnet.qnn.opt import SPSA as SPSA
from pyvqnet.tensor import QTensor as QTensor, tensor as tensor

class QuantumKernel_VQNet:
    def __init__(self, batch_size: int = 900, qlist: Incomplete | None = None, clist: Incomplete | None = None, n_qbits: Incomplete | None = None) -> None: ...
    def evaluate(self, x_vec: np.ndarray, y_vec: np.ndarray = None) -> np.ndarray: ...
    def build_circuit(self, qlist, n_qbits, weights_x, weights_y): ...
    def run_circuit(self, n_qbits, weights_x, weights_y): ...

gap_value_path: Incomplete

def gen_vqc_qsvm_data(training_size: int = 20, test_size: int = 10, gap: float = 0.3):
    """
    Genertae data for vqc qvm algorithm,the data has '0','1' two labels

    :param training_size: training_size for single class, default = 20
    :param test_size: test_size for single class, default = 10
    :param gap: a gap value seperates the two class on bloch sphere, please refer to thesis:https://arxiv.org/pdf/1804.11326.pdf

    :return train_data: traindata
            test_data: test data
            train_label: train label
            test_label: test label
            sample_total: total sample
    """

class vqc_qsvm:
    qcir: Incomplete
    initial_parameters: Incomplete
    machine: Incomplete
    qubits: Incomplete
    minibatch_size: Incomplete
    reps: Incomplete
    opt: Incomplete
    num_class: int
    run_obj_time: int
    loss: Incomplete
    ret: Incomplete
    def __init__(self, minibatch_size: int = 40, maxiter: int = 40, rep: int = 3) -> None:
        """
        Class for VQC SVM algo.reference:https://arxiv.org/pdf/1804.11326.pdf

        :param minibatch_size: batch size,default = 40
        :param maxiter: max iteration times,default = 40
        :param rep: repeat time for vqc block,default = 3

        """
    def save_thetas(self, save_dir: str = 'RLT') -> None:
        """
        Save trained parameters into a pickle file and draw the cir png.

        :param save_dir: save_dir, default='RLT'
        """
    if_directly_run: Incomplete
    def train(self, train_data, train_labels, if_directly_run: bool = False):
        """
        Use train data to run qpanda circuit and optimize parameters.

        :param train_data: 2D array generated from `gen_vqc_qsvm_data` function.
        :param train_labels: 1D array lables generated from `gen_vqc_qsvm_data` function.
        :param if_directly_run: if use quantum measure or directly run,default= False.
        """
    def predict(self, data, label: Incomplete | None = None):
        """
        Use data to run qpanda circuit and get accuracy if labels are given.

        :param data: 2D array test data generated from `gen_vqc_qsvm_data` function.
        :param label: 1D array lables generated from `gen_vqc_qsvm_data` function. default None.

        :return probability and accurcay if label is given.
        """
    def plot(self, train_features, test_features, train_labels, test_labels, samples) -> None:
        """
        Plot data
        """
