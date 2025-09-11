from . import QMachine as QMachine
from ... import nn as nn, tensor as tensor
from ...tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, to_tensor as to_tensor
from .qmachine_utils import find_qmachine as find_qmachine
from .qop import QModule as QModule
from _typeshed import Incomplete

class QuantumLayerES(nn.Module):
    general_module: Incomplete
    qm: Incomplete
    sigma: Incomplete
    train_: bool
    def __init__(self, general_module: nn.Module, q_machine: QMachine, name: str = '', sigma=...) -> None:
        '''
        A python QuantumLayer wrapper for adjoint gradient calculation.
        Only support vqc module consists of single paramter quantum gates.

        :param general_module: a vqc nn.Module instance.
        :param q_machine: q_machine from general_module.
        :param name: name
        :param sigma: Sampling variance of a multivariate nontrivial distribution.
        
        .. note::

            general_module\'s QMachine should set grad_method = "ES"

        Example::

            from pyvqnet import tensor
            from pyvqnet.qnn.vqc import QuantumLayerES, QMachine, RX, RY, CNOT, T, MeasureAll, RZ, VQC_HardwareEfficientAnsatz
            import pyvqnet
            
            class QModel(pyvqnet.nn.Module):
            
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
                                grad_mode="ES")
            ES_model = QuantumLayerES(qunatum_model, qunatum_model.qm)
            batch_y = ES_model(input_x)
            batch_y.backward()
        
        '''
    def forward(self, x, *args, **kwargs): ...
