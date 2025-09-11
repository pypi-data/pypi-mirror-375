from _typeshed import Incomplete
from pyvqnet.dtype import kfloat32 as kfloat32
from pyvqnet.nn import LeakyReLu as LeakyReLu, Linear as Linear, Module as Module, Parameter as Parameter, Sigmoid as Sigmoid
from pyvqnet.optim import Adam as Adam
from pyvqnet.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, tensor as tensor
from pyvqnet.utils import initializer as initializer
from pyvqnet.utils.initializer import ones as ones

def qgenrator_cir(x, param, num_of_qubits, rep):
    """
    quantum generator circuits
    """

class QGANAPI:
    '''
    QGAN class for random distribution generations

    Example::
            import pickle
            import os
            import pyqpanda as pq
            from pyvqnet.qnn.qgan.qgan_utils import QGANAPI
            import numpy as np


            ##################################
            num_of_qubits = 3  # paper config
            rep = 1

            number_of_data = 10000
            # Load data samples from different distributions
            mu = 1
            sigma = 1
            real_data = np.random.lognormal(mean=mu, sigma=sigma, size=number_of_data)


            # intial
            save_dir = None
            qgan_model = QGANAPI(
                real_data,
                # numpy generated data distribution, 1 - dim.
                num_of_qubits,
                batch_size=2000,
                num_epochs=2000,
                q_g_cir=None,
                bounds = [0.0,2**num_of_qubits -1],
                reps=rep,
                metric="kl",
                tol_rel_ent=0.01,
                if_save_param_dir=save_dir
            )

            # train
            qgan_model.train()  # train qgan

            # show probability distribution function of generated distribution and real distribution
            qgan_model.eval(real_data)  #draw pdf

            # get trained quantum parameters
            param = qgan_model.get_trained_quantum_parameters()
            print(f" trained param {param}")

            #load saved parameters files
            if save_dir is not None:
                path = os.path.join(
                    save_dir, qgan_model._start_time + "trained_qgan_param.pickle")
                with open(path, "rb") as file:
                    t3 = pickle.load(file)
                param = t3["quantum_parameters"]
                print(f" trained param {param}")

            #show probability distribution function of generated distribution and real distribution
            qgan_model.load_param_and_eval(param)

            #calculate metric
            print(qgan_model.eval_metric(param, "kl"))

            #get generator quantum circuit
            machine = pq.CPUQVM()
            machine.init_qvm()
            qubits = machine.qAlloc_many(num_of_qubits)
            qpanda_cir = qgan_model.get_circuits_with_trained_param(qubits)
            print(qpanda_cir)
    '''
    def __init__(self, data, num_qubits: int = 3, batch_size: int = 2000, num_epochs: int = 2000, q_g_cir: Incomplete | None = None, opt_g: Incomplete | None = None, opt_d: Incomplete | None = None, bounds: Incomplete | None = None, reps: int = 1, metric: str = 'kl', tol_rel_ent: float = 0.001, if_save_param_dir: str = 'tmp') -> None:
        '''
            Init QGAN class for train and eval

            :param data: real data for train, should be numpy array
            :param num_qubits: number of qubits ,should be same as your
             defined quantum generator "s qubits number.
            :param batch_size: batch sizee for training.
            :param num_epochs: number of train iters.
            :param q_g_cir: quantum circuits run function for generator,it should be defined like
            `qgenrator_cir`.otherwise, it cannot run.
            :param opt_g: optimizator instance for generator,use vqnet optim class
            :param opt_g: optimizator instance for discriminator,use vqnet optim class
            :param bounds: boundary for real data distribution
            :param reps: repeat times for default circuits block in papers.
            :param metric: metric for eval gan result.
            "KL" stands for kl divergence, "CE": stands for CrossEntropy.
            :param tol_rel_ent: tolerence for metric
            :param if_save_param_dir: save dir for parameters file and evaluations results.

        '''
    def get_trained_quantum_parameters(self):
        """
            get best trained quantum parameters numpy array based on metric

            return : parameters array
        """
    def train(self) -> None:
        """
            train function
        """
    def eval_metric(self, param, metric: str):
        """
            eval metric with input param

            param param: quantum generator parameters array
            param metric: metric string
            return: metric
        """
    def eval(self, compare_dist: Incomplete | None = None) -> None:
        """
            eval real data distribution with trained best param.

            :param compare_dist: numpy real data distribution 1-dim
        """
    def get_circuits_with_trained_param(self, qubits):
        """
        get qpanda circuit instance with trained parameters for qgan

        param qubits: pyqpanda allocated qubits.
        """
    def load_param_and_eval(self, param):
        """
            load param array and plot pdf

            param param: quantum generator parameters array
            return: prob of quantum generator each statevector
        """

class QGANLayer(Module):
    """
        a pyvqnet module for qgan quantum circuit calculation. modified for qgan only.
    """
    m_prog_func: Incomplete
    m_para: Incomplete
    delta: Incomplete
    history_expectation: Incomplete
    w_jacobian: Incomplete
    x_jacobian: Incomplete
    def __init__(self, qprog_with_meansure, para_num, data_grid, num_qubits, diff_method: str = 'parameter_shift', delta: float = 0.01) -> None:
        """
           a pyvqnet module for qgan quantum circuit calculation. modified for qgan only.
        """
    def forward(self, x): ...

class QuantumGenerator(Module):
    """
    Quantum generator module, contains a trainable QGANLayer
    """
    qgenrator: Incomplete
    def __init__(self, cir, num_of_qubits, data_grid, reps: int = 1) -> None: ...
    def forward(self, x): ...

class ClassicDiscriminator(Module):
    """
    Classic discriminator module, contains a trainable Classic nerual network.
    """
    mlp1: Incomplete
    mlp2: Incomplete
    mlp3: Incomplete
    def __init__(self) -> None: ...
    def forward(self, x): ...
