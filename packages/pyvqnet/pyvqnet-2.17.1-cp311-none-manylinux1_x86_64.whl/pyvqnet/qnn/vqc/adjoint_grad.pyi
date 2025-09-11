import types
from . import QMachine as QMachine, apply_gate_operation_impl as apply_gate_operation_impl, load_measure_obs as load_measure_obs, op_history_to_list as op_history_to_list, operation_derivative as operation_derivative
from ... import nn as nn, tensor as tensor
from ...backends import global_backend as global_backend
from ...dtype import complex_dtype_to_float_dtype as complex_dtype_to_float_dtype
from ...tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, adjoint as adjoint, no_grad as no_grad
from .qmachine_utils import find_qmachine as find_qmachine
from _typeshed import Incomplete

def apply_operation(ket, op, if_adjoint: bool = False):
    """
    use for adjoint only
    """
def reduce_sum_real_jac(input_tensor, group_indices_list: list[int]): ...
def get_multi_output_obs_num(observables): ...
def adjoint_grad_calc(qm: QMachine, num_wires, observables, ops):
    """
    calculate jacobian matrix for adjoint grad.
    """

class AdjointRunningScope:
    old_just_define: bool
    save_op_history: bool
    set_in_qadjoint: bool
    qm: Incomplete
    def __init__(self, qm) -> None: ...
    def __enter__(self) -> None: ...
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: types.TracebackType | None) -> None: ...

def adjoint_assign_grad(g, jac, input_or_w): ...
def adjoint_grad_node_gen(params_dict, jac, nodes): ...

class QuantumLayerAdjoint(nn.Module):
    vqc_module: Incomplete
    qm: Incomplete
    def __init__(self, vqc_module: nn.Module, use_qpanda: bool = False, name: str = '') -> None:
        '''
        A python QuantumLayer wrapper for adjoint gradient calculation.
        Only support vqc module consists of single paramter quantum gates.

        :param vqc_module: a vqc nn.Module instance.
        :param use_qpanda: whether use qpanda to do forward for speedup, defualt: False.
            For more deeper and complex circuit, the qpanda have more speed advantages.
            If use_qpanda == True, vqc_module should be instance of HybirdVQCQpandaQVMLayer.
        :name name: name

        .. note::

            vqc_module\'s QMachine should set grad_method = "adjoint"

        Example::

            from pyvqnet import tensor
            from pyvqnet.qnn.vqc import QuantumLayerAdjoint, QMachine, RX, RY, CNOT, PauliX, qmatrix, PauliZ, T, MeasureAll, RZ, VQC_RotCircuit, VQC_HardwareEfficientAnsatz
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
                                grad_mode="adjoint")

            adjoint_model = QuantumLayerAdjoint(qunatum_model)

            batch_y = adjoint_model(input_x)
            batch_y.backward()

        '''
    def get_q_machine(self, vqc_module, use_qpanda: bool = False): ...
    def forward(self, x, *args, **kwargs): ...
QuantumAdjointLayer = QuantumLayerAdjoint
