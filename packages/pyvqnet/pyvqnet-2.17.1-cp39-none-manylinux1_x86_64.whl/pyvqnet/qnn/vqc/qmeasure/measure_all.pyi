from .... import tensor as tensor
from ....backends import global_backend as global_backend
from ....tensor import no_grad as no_grad
from ..qcircuit import I as I, PauliX as PauliX, save_op_history as save_op_history
from ..qmachine import QMachine as QMachine, get_just_return_ops as get_just_return_ops, not_just_define_op as not_just_define_op, not_save_op_history as not_save_op_history
from ..qop import Observable as Observable, Operator as Operator
from ..utils.utils import construct_modules_from_ops as construct_modules_from_ops, get_obs_eigvals as get_obs_eigvals, helper_parse_paulisum as helper_parse_paulisum
from .measure_name_dict import get_measure_name_dict as get_measure_name_dict
from .qmeasure import Measurements as Measurements
from .utils import append_measure_proc as append_measure_proc, maybe_parse_obs as maybe_parse_obs, ob_class_parse as ob_class_parse, probs_func as probs_func

def get_enable_use_old_exp() -> bool: ...
def set_enable_use_old_exp(value: bool) -> None: ...
def get_eigvals_real(probs_dtype, probs_device, observables, active_wires): ...
def expval_return_with_eig(q_machine: QMachine, wires: int | list[int], observables: Observable | list[Observable]):
    """
    return expecatation and eigval .
    """
def expval(q_machine: QMachine, wires: int | list[int], observables: Observable | list[Observable]): ...
def maybe_insert_obs_for_adjoint_gradient(q_machine, observables) -> None:
    """insert observables into op history for adjoint gradient."""

class MeasureAll(Measurements):
    """
    Obtain the expectation value of all the qubits based on Pauli opearators.
    
    If measure the observable like:
        PauliZ(1)@PauliX(0)*0.23+PauliY(1)@PauliZ(0)*-3.5
    use:
        obs = {'Z1 X0': 0.23,'Y1 Z0':-3.5}
    
    If measure the multiple observables like :
        [PauliX(0)*1+PauliY(2)*0.5+PauliZ(3)*0.4,
                PauliZ(1)@PauliX(0)*0.23+PauliY(1)@PauliZ(0)*-3.5],
    

    use:
        obs = [{'X0': 1,'Y2':0.5,'Z3':0.4},{'Z1 X0': 0.23,'Y1 Z0':-3.5}]
    }]
    
    """
    def __init__(self, obs, name: str = '') -> None: ...
    def measure_fun_simple_basis(self, q_machine: QMachine, obs):
        """
        measure observables like PauliX,PauliY,I,PauliZ.
        """
    @append_measure_proc
    def forward(self, q_machine: QMachine): ...
    def __call__(self, *args, **kwargs): ...
