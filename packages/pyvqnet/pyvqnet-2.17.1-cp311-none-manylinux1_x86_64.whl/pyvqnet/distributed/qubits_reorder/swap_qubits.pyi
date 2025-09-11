from .swap_q1 import swap_global_global_q1 as swap_global_global_q1, swap_local_global_q1 as swap_local_global_q1
from _typeshed import Incomplete
from pyvqnet.distributed import CommController as CommController
from pyvqnet.tensor import permute as permute

def tile_construction(Q, C, T): ...
def qubit_mapping(Q, C, T, n_L): ...
def flat_time_space_tiling(Q, C, T, n_L):
    """
    Qubit_list: all qubit list
    C: all logic gate
    T: logic gate mapping
    n_L: num local qubit nums
    
    """
def compute_qubit_mapping(first_list, second_list):
    """
    generate mapping function for first_list and second_list
    """
def compute_qubit_remapping(after_qubit_list, before_qubit_list): ...

class QubitsPermutation:
    num_elements: Incomplete
    map: Incomplete
    imap: Incomplete
    def __init__(self, num_elements) -> None: ...
    def obtain_intermediate_inverse_maps(self, target_map, M): ...
    def set_new_permutation_from_map(self, m, style_of_map: str = 'direct') -> None: ...
    def exchange_two_elements(self, element_1, element_2) -> None: ...

qr_Comm_OP: Incomplete

def get_global_CommController_for_qr(is_cuda: bool = False): ...

class QubitReorder:
    """
    multi qubits reorder,[q3,q2,q1,q0]
    """
    cur_map: Incomplete
    target_map: Incomplete
    def reset_mapping(self) -> None: ...
    local_states: Incomplete
    def set_input_states(self, local_states) -> None: ...
    num_qubits: Incomplete
    num_proc: Incomplete
    n_global: Incomplete
    n_local: Incomplete
    comm: Incomplete
    batch_size: Incomplete
    def __init__(self, num_qubits, num_proc, local_states) -> None:
        """

        :param num_qubits: number of total qubits.
        :param num_proc: number of process in distributed env, should be equal to global qubits number.
        :param local_states = state vectors qtensor data in distributed env.
        """
    def apply_1q_local_global_swap(self, local_qubit, num_g) -> None: ...
    def run(self, target_map):
        """
        do qubit reoder on target qubits oreder
        """
    def qr_local_to_local(self, target_map) -> None: ...
    def run_gg(self, target_map) -> None: ...
    def run_gl(self, target_map) -> None:
        """
        Do local qubit permute or local-global qubit permute or global-global qubit permute
        :param target_map: target qubits order list
        """

class QubitReorderOp:
    """
    gates with additional info for qubit reorder
    """
    gate_with_qr: Incomplete
    def __init__(self, gate_with_qr) -> None:
        """
        :param gate_with_qr: 
        """

def gen_qr_machine(global_dist_machine, final_qubit_order):
    """
    just create a new qmachine that only store(local_qubits) states.

    """
