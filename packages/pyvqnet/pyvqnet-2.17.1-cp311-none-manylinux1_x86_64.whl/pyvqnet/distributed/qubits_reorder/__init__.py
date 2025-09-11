"""
qubits_reorder
"""
import platform

if "linux" in platform.platform() or "Linux" in platform.platform():

    from .utils import _reorder_qr_states_for_obs
    from .utils import all_same_qubit_dist_expval
    from .utils import gen_local_qm_and_op_history
    from .swap_q1 import swap_local_global_q1,swap_global_global_q1
    from .swap_qubits import QubitReorder,QubitsPermutation,QubitReorderOp,flat_time_space_tiling,compute_qubit_remapping,compute_qubit_mapping,gen_qr_machine
    from .dist_qmachine import DistributeQMachine,QubitReorderLocalQmachine
    from .dist_vqc import DistQuantumLayerAdjoint,measure_all_for_qr,exec_states_qr
    from .utils import update_local_states_with_qr,update_global_qmachine_states_in_qr
else:
    from .qr_mock import QubitReorderMock as QubitReorder
    from .qr_mock import QubitReorderMock as QubitReorderOp
    from .qr_mock import QubitReorderMock as gen_qr_machine
    from .qr_mock import QubitReorderMock as DistributeQMachine
    from .qr_mock import QubitReorderMock as DistQuantumLayerAdjoint
    from .qr_mock import QubitReorderMock as flat_time_space_tiling
    from .qr_mock import QubitReorderMock as compute_qubit_remapping
    from .qr_mock import QubitReorderMock as compute_qubit_mapping
    from .qr_mock import QubitReorderMock as measure_all_for_qr
    def update_local_states_with_qr(m, local_q_machine):
        
        pass
    def update_global_qmachine_states_in_qr(m, local_q_machine):
        pass

    def _reorder_qr_states_for_obs(q_machine,cur_qr_info):
        pass
    def all_same_qubit_dist_expval(q_machine,obs,idx_in_paulisum):
        pass

    def gen_local_qm_and_op_history(global_qmachine,origin_op_history):
        pass