from .... import tensor as tensor
from ....backends import global_backend as global_backend
from ....device import DEV_CPU as DEV_CPU
from ....tensor import no_grad as no_grad
from ....utils import get_random_seed as get_random_seed
from ...utils import unique_wires as unique_wires
from ..qcircuit import I as I, PauliX as PauliX, PauliY as PauliY, PauliZ as PauliZ, QUnitary as QUnitary, qgate_op_creator as qgate_op_creator, save_op_history as save_op_history
from ..qmachine import QMachine as QMachine, not_just_define_op as not_just_define_op, not_save_op_history as not_save_op_history
from ..qop import Observable as Observable
from ..utils.utils import COMPLEX_2_FLOAT as COMPLEX_2_FLOAT, all_wires as all_wires, check_same_device as check_same_device, check_same_dtype as check_same_dtype, construct_modules_from_ops as construct_modules_from_ops, expand_matrix as expand_matrix, get_sum_mat as get_sum_mat, helper_parse_paulisum as helper_parse_paulisum
from .measure_name_dict import get_measure_name_dict as get_measure_name_dict
from _typeshed import Incomplete
from functools import reduce as reduce
from pyvqnet.dtype import C_DTYPE as C_DTYPE, dtype_map_from_numpy as dtype_map_from_numpy, kint64 as kint64
from pyvqnet.nn import Module as Module

basic_d: Incomplete

def flatten_state(state, num_wires): ...
def ob_class_parse(obs, num_wires): ...
def maybe_parse_obs(measure_proc, obs, num_wires: int):
    '''
    convert obs into format like: {
        "X0":1,"Y2":0.5,"Z3":0.4
    }
    '''
def append_measure_proc(f): ...
def hermitian_expval(H, state: tensor.QTensor, wires):
    """
    input a Hermitian matrix acted on `wires`, return analytic expectation of quantum states.
    
    Supports batch input like [b,2,2...] on CPU/GPU

    :param H: Hermitian matrix of shape [2,2,..].
    :param state: batch quantum state.
    :param wires: the Hermitian matrix acts on.
    :return:
        exepectation of Hermitian matrix.
    """
Hermitian_expval = hermitian_expval

def load_measure_obs(op_history, wires=None, return_obs: bool = False):
    """
    create list of measurements using Qunitary ,only used for adjoint grad for now.
    """
