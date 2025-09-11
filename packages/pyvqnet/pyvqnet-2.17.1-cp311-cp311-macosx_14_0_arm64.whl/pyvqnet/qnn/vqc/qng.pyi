from ... import nn as nn
from ...backends import global_backend as global_backend
from ...native.backprop_utils import keep_activation_in_graph as keep_activation_in_graph
from ...optim import SGD as SGD
from ...tensor import QTensor as QTensor, tensor as tensor
from .qcircuit import helper_get_geneartor_from_dict as helper_get_geneartor_from_dict, op_history_to_list as op_history_to_list
from .qmachine import QMachine as QMachine
from .qmachine_utils import find_qmachine as find_qmachine
from .utils import CircuitGraph as CircuitGraph, cov_matrix as cov_matrix, find_nodes_without_post as find_nodes_without_post
from _typeshed import Incomplete

def wrapper_calculate_qng(f): ...

class QNG:
    """
    Quantum Nature Gradient Optimizer, described in `Quantum Natural Gradient. <https://doi.org/10.22331/q-2020-05-25-269>`_, 2020.
    
    Optimizer with adaptive learning rate, via calculation
    of the diagonal or block-diagonal approximation to the Fubini-Study metric tensor.
    A quantum generalization of natural gradient descent.

    The QNG optimizer uses a step- and parameter-dependent learning rate,
    with the learning rate dependent on the pseudo-inverse
    of the Fubini-Study metric tensor :math:`g`:

    .. math::
        x^{(t+1)} = x^{(t)} - \\eta g(f(x^{(t)}))^{-1} \\nabla f(x^{(t)}),

    where :math:`f(x^{(t)}) = \\langle 0 | U(x^{(t)})^\\dagger \\hat{B} U(x^{(t)}) | 0 \\rangle`
    is an expectation value of some observable measured on the variational
    quantum circuit :math:`U(x^{(t)})`.

    Consider a quantum node represented by the variational quantum circuit

    .. math::

        U(\\mathbf{\\theta}) = W(\\theta_{i+1}, \\dots, \\theta_{N})X(\\theta_{i})
        V(\\theta_1, \\dots, \\theta_{i-1}),

    For each parametric layer :math:`\\ell` in the variational quantum circuit
    containing :math:`n` parameters, the :math:`n\\times n` block-diagonal submatrix
    of the Fubini-Study tensor :math:`g_{ij}^{(\\ell)}` is calculated directly on the
    quantum device in a single evaluation:

    .. math::

        g_{ij}^{(\\ell)} = \\langle \\psi_\\ell | K_i K_j | \\psi_\\ell \\rangle
        - \\langle \\psi_\\ell | K_i | \\psi_\\ell\\rangle
        \\langle \\psi_\\ell |K_j | \\psi_\\ell\\rangle

    where :math:`|\\psi_\\ell\\rangle =  V(\\theta_1, \\dots, \\theta_{i-1})|0\\rangle`
    (that is, :math:`|\\psi_\\ell\\rangle` is the quantum state prior to the application
    of parameterized layer :math:`\\ell`).

    .. note::

        Only tested on non-batched data.
        Only Support pure variational quantum circuit.
        step() will update both input and Paramters's gradients.
        step() will only update model's paramters's value.

    Example::

        from pyvqnet.qnn.vqc import QMachine, RX, RY, RZ, CNOT, rz, PauliX, qmatrix, PauliZ, Probability, rx, ry, MeasureAll, U2
        from pyvqnet.tensor import QTensor, tensor
        import pyvqnet
        import numpy as np


        from pyvqnet.qnn.vqc import wrapper_calculate_qng


        class QModel(pyvqnet.nn.Module):
            def __init__(self, num_wires, dtype):
                super(QModel, self).__init__()

                self._num_wires = num_wires
                self._dtype = dtype
                self.qm = QMachine(num_wires, dtype=dtype)
                self.rz_layer1 = RZ(has_params=True, trainable=False, wires=0)
                self.rz_layer2 = RZ(has_params=True, trainable=False, wires=1)
                self.u2_layer1 = U2(has_params=True, trainable=False, wires=0)
                self.l_train1 = RY(has_params=True, trainable=True, wires=1)
                self.l_train1.params.init_from_tensor(
                    QTensor([333], dtype=pyvqnet.kfloat32))
                self.l_train2 = RX(has_params=True, trainable=True, wires=2)
                self.l_train2.params.init_from_tensor(
                    QTensor([4444], dtype=pyvqnet.kfloat32))
                self.xlayer = PauliX(wires=0)
                self.cnot01 = CNOT(wires=[0, 1])
                self.cnot12 = CNOT(wires=[1, 2])
                self.measure = MeasureAll(obs={'Y0': 1})

            @wrapper_calculate_qng
            def forward(self, x, *args, **kwargs):
                self.qm.reset_states(x.shape[0])

                ry(q_machine=self.qm, wires=0, params=np.pi / 4)
                ry(q_machine=self.qm, wires=1, params=np.pi / 3)
                ry(q_machine=self.qm, wires=2, params=np.pi / 7)
                self.rz_layer1(q_machine=self.qm, params=x[:, [0]])
                self.rz_layer2(q_machine=self.qm, params=x[:, [1]])

                self.u2_layer1(q_machine=self.qm, params=x[:, [3, 4]])  #

                self.cnot01(q_machine=self.qm)
                self.cnot12(q_machine=self.qm)
                ry(q_machine=self.qm, wires=0, params=np.pi / 7)

                self.l_train1(q_machine=self.qm)
                self.l_train2(q_machine=self.qm)
                #rx(q_machine=self.qm, wires=2, params=x[:, [3]])
                rz(q_machine=self.qm, wires=1, params=x[:, [2]])
                ry(q_machine=self.qm, wires=0, params=np.pi / 7)
                rz(q_machine=self.qm, wires=1, params=x[:, [2]])

                self.cnot01(q_machine=self.qm)
                self.cnot12(q_machine=self.qm)
                rlt = self.measure(q_machine=self.qm)
                return rlt


        qmodel = QModel(3, pyvqnet.kcomplex64)

        x = QTensor([[1111.0, 2222, 444, 55, 666]], requires_grad=True)

        qng = pyvqnet.qnn.vqc.QNG(qmodel,0.01)

        qng.step(x)
        print(x)
        print(qmodel.parameters())
        qng.step(x)

    """
    stepsize: Incomplete
    qmodel: Incomplete
    opt: Incomplete
    def __init__(self, qmodel, stepsize: float = 0.01, momentum: int = 0) -> None:
        """
        
        :param qmodel: user provided QModule
        :param stepsize: step size, default: 0.01.
        :param momentum: momentum for sgd. default:0.
        """
    def zero_grad(self) -> None: ...
    def step(self, x, g=None) -> None:
        """
        Run forward function and backward with g. Update parameters with gradient with quantum nature gradient.

        :param x: input parameters, should have requires_grad = True.
        :param g: gradient of outputs. default is None
        
        """
