from ... import nn as nn, tensor as tensor
from ...backends import global_backend as global_backend
from ...dtype import complex_dtype_to_float_dtype as complex_dtype_to_float_dtype
from ...qnn.vqc import QModule as QModule, op_history_to_list as op_history_to_list, operation_derivative as operation_derivative
from ...qnn.vqc.adjoint_grad import AdjointRunningScope as AdjointRunningScope, adjoint_grad_node_gen as adjoint_grad_node_gen, apply_operation as apply_operation, get_multi_output_obs_num as get_multi_output_obs_num, reduce_sum_real_jac as reduce_sum_real_jac
from ...qnn.vqc.qmeasure.utils import maybe_parse_obs as maybe_parse_obs, ob_class_parse as ob_class_parse
from ...qnn.vqc.qop import Observable as Observable
from ...qnn.vqc.utils.utils import apply_gate_operation_impl as apply_gate_operation_impl
from ...tensor import QTensor as QTensor, no_grad as no_grad
from ..ControlComm import get_world_size as get_world_size
from .dist_qmachine import DistributeQMachine as DistributeQMachine
from .swap_qubits import QubitReorder as QubitReorder, compute_qubit_mapping as compute_qubit_mapping, compute_qubit_remapping as compute_qubit_remapping, get_global_CommController_for_qr as get_global_CommController_for_qr
from .utils import construct_measure_obs_for_qr as construct_measure_obs_for_qr, exec_states_qr as exec_states_qr
from _typeshed import Incomplete

def check_if_need_qr(cur_qr_info):
    """
    check if need qr
    """
def update_all_qubit_obs_bras(cur_wires, cur_qr_infos, cur_ob_infos, new_states, num_wires, num_proc, coeff: int = 1): ...
def adjoint_grad_calc(qm, num_wires, obs_list, ops, qubit_order_before_measure): ...
def find_dist_qmachine(qunatum_model: QModule): ...

class DistQuantumLayerAdjoint(nn.Module):
    vqc_module: Incomplete
    qm: Incomplete
    def __init__(self, vqc_module: nn.Module, name: str = '') -> None: ...
    def get_q_machine(self, vqc_module): ...
    def forward(self, x, *args, **kwargs): ...

def dist_single_paulisum_exp(meas_proc, q_machine, is_complicated, single_paulisum_obs, new_states_adjoint): ...
def measure_all_for_qr(meas_proc, q_machine):
    """
    measure all process for distributed states vectors
    :param meas_proc: measurement
    :param q_machine: local q_machine
    """
