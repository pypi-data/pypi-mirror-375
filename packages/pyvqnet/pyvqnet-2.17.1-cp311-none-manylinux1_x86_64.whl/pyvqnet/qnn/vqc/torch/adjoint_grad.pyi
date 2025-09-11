import torch
from . import TorchModule as TorchModule
from .. import load_measure_obs as load_measure_obs, op_history_to_list as op_history_to_list
from .... import nn as nn
from ....backends import global_backend as global_backend
from ....nn.torch import TorchModuleList as TorchModuleList
from ....tensor import QTensor as QTensor
from ..adjoint_grad import AdjointRunningScope as AdjointRunningScope, QuantumLayerAdjoint as NQuantumLayerAdjoint, adjoint_grad_calc as adjoint_grad_calc, apply_operation as apply_operation
from _typeshed import Incomplete

class QuantumLayerAdjoint(TorchModule, NQuantumLayerAdjoint):
    params_dict: Incomplete
    jac: Incomplete
    y: Incomplete
    inputs: Incomplete
    def __init__(self, general_module: nn.Module, use_qpanda: bool = False, name: str = '') -> None:
        '''
        A python QuantumLayer wrapper for adjoint gradient calculation.
        Only support vqc module consists of single paramter quantum gates.

        :param general_module: a vqc nn.Module instance.
        :param use_qpanda: if use qpadna to run forward.
        :name name: name

        .. note::

            general_module\'s QMachine should set grad_method = "adjoint"

        Example::

            import pyvqnet
            pyvqnet.backends.set_backend("torch")
            from pyvqnet import tensor
            from pyvqnet.qnn.vqc.torch import QuantumLayerAdjoint,                 QMachine, RX, RY, CNOT, PauliX, PauliZ, T,                     MeasureAll, RZ, VQC_RotCircuit, VQC_HardwareEfficientAnsatz,                        QModule

            class QModel(QModule):
                def __init__(self, num_wires, dtype, grad_mode=""):
                    super(QModel, self).__init__()

                    self._num_wires = num_wires
                    self._dtype = dtype
                    self.qm = QMachine(num_wires, dtype=dtype, grad_mode=grad_mode)
                    self.rx_layer = RX(has_params=True, trainable=False, wires=0)
                    self.ry_layer = RY(has_params=True, trainable=False, wires=1)
                    self.rz_layer = RZ(has_params=True, trainable=False, wires=1)
                    self.rz_layer2 = RZ(has_params=True, trainable=True, wires=1)

                    self.rot = VQC_HardwareEfficientAnsatz(6, ["rx", "RY", "rz"],
                                                        entangle_gate="cnot",
                                                        entangle_rules="linear",
                                                        depth=5)
                    self.tlayer = T(wires=1)
                    self.cnot = CNOT(wires=[0, 1])
                    self.measure = MeasureAll(obs={
                        "X1":1
                    })

                def forward(self, x, *args, **kwargs):
                    self.qm.reset_states(x.shape[0])

                    self.rx_layer(params=x[:, [0]], q_machine=self.qm)
                    self.cnot(q_machine=self.qm)
                    self.ry_layer(params=x[:, [1]], q_machine=self.qm)
                    self.tlayer(q_machine=self.qm)
                    self.rz_layer(params=x[:, [2]], q_machine=self.qm)
                    self.rz_layer2(q_machine=self.qm)
                    self.rot(q_machine=self.qm)
                    rlt = self.measure(q_machine=self.qm)

                    return rlt


            input_x = tensor.QTensor([[0.1, 0.2, 0.3]])

            input_x = tensor.broadcast_to(input_x, [40, 3])

            input_x.requires_grad = True

            qunatum_model = QModel(num_wires=6,
                                dtype=pyvqnet.kcomplex64,
                                grad_mode="adjoint")

            adjoint_model = QuantumLayerAdjoint(qunatum_model)

            batch_y = adjoint_model(input_x)
            batch_y.backward()

        '''
    def forward(self, x, *args, **kwargs): ...

class HybridFunction(torch.autograd.Function):
    """ Hybrid quantum - classical function definition """
    @staticmethod
    def forward(ctx, qlayer, *tensors):
        """ Forward pass computation """
    @staticmethod
    def backward(ctx, grad_output): ...
