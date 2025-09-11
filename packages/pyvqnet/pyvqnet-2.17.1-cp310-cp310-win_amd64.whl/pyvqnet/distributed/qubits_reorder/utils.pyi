from ...backends import global_backend as global_backend
from ...qnn.vqc import Observable as Observable
from ...qnn.vqc.qmeasure.measure_all import get_eigvals_real as get_eigvals_real, maybe_insert_obs_for_adjoint_gradient as maybe_insert_obs_for_adjoint_gradient
from .swap_qubits import QubitReorder as QubitReorder, compute_qubit_remapping as compute_qubit_remapping, flat_time_space_tiling as flat_time_space_tiling, gen_qr_machine as gen_qr_machine

def exec_states_qr(num_qubits, num_proc, states, swap_qubit):
    """
    use QubitReorder to do states qubit reorder based on swap_qubit.
    """
def get_unique_reordered_mappings(list_M, n_all_qubits): ...
def mapping_local_op_idx_with_qr_idx(n_all_qubits, global_qubit):
    """
    gate idx is reversed with qr 
    """
def map_gate_idx_to_cur_order(gate_wires, next_qubit_order): ...
def construct_qr_op_history(q_machine):
    """
    return  new op_history with `qr_op` inserted.
    """
def get_global_qr_info(old_qmachine): ...
def move_sublists(original_list, cur_local_qubit_oreder): ...
def construct_measure_obs_for_qr(obs, final_states_order_init, global_qubit, local_qubit):
    """
    if obs is single dict with single pauli： 
        [{'wires': [[0, 1, 2, 3]], 
        'observables': [[['Z', 'Z', 'Z', 'Z'], ['I', 'I', 'I', 'Z']]], 
        'coefficient': [[21.0, 21.0]], 
        'qubit_swap': [[{'qr': True, 'swap': [0, 1, 2, 4, 3]}, {'qr': True, 'swap': [4, 0, 1, 2, 3]}]]}]
    
    if obs is single dict with multi pauli： 
        [{'wires': [[0, 1, 2, 3], [0, 1, 2, 3]],
         'observables': [['Y', 'I', 'Y', 'Y'], [['Z', 'Z', 'Z', 'Z'], ['I', 'I', 'I', 'Z']]],
          'coefficient': [3.0, [21.0, 21.0]], 
          'qubit_swap': [{'qr': False}, [{'qr': True, 'swap': [0, 1, 2, 4, 3]}, {'qr': True, 'swap': [4, 0, 1, 2, 3]}]]}]
    
    if obs is a list of dict：
        [{'wires': [[0, 1, 2, 3]],
         'observables': [[['Z', 'Z', 'Z', 'Z'], ['I', 'I', 'I', 'Z']]],
          'coefficient': [[21.0, 21.0]], 
          'qubit_swap': [[{'qr': True, 'swap': [0, 1, 2, 4, 3]}, {'qr': True, 'swap': [4, 0, 1, 2, 3]}]]}, 
          
          {'wires': [[0, 1, 2, 3]], 
          'observables': [['I', 'Y', 'Y', 'X']],
           'coefficient': [5.1],
            'qubit_swap': [{'qr': True, 'swap': [0, 2, 4, 1, 3]}]},

             {'wires': [[0, 1, 2, 3]], 
             'observables': [[['X', 'X', 'X', 'X'], ['I', 'I', 'I', 'X']]], 
             'coefficient': [[3.1, 3.1]], 
             'qubit_swap': [[{'qr': True, 'swap': [0, 1, 2, 4, 3]}, {'qr': True, 'swap': [4, 0, 1, 2, 3]}]]}]
    """
def update_global_qmachine_config_in_qr(global_qmachine, old_last_reordered, global_qubit, old_op_history) -> None: ...
def update_global_qmachine_states_in_qr(global_qmachine, q_machine) -> None:
    """
    global_qmachine store local qmachine (states,states_before_measure)
    shape={b,[2]**local_qubit}
    Caution: this states may be not default order !!
    """
def gen_local_qm_and_op_history(global_qmachine, origin_op_history): ...
def update_local_states_with_qr(module, local_q_machine) -> None: ...
def rebase_dist_obs_before_prob(cur_wires, cur_qr_infos, cur_ob_infos, q_machine, coeff: int = 1): ...
def all_same_qubit_dist_expval(q_machine, obs, idx_in_paulisum): ...
