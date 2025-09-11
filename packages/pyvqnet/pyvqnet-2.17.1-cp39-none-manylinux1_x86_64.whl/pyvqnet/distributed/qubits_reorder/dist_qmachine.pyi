from ... import tensor as tensor
from .swap_qubits import QubitReorder as QubitReorder
from _typeshed import Incomplete
from pyvqnet import kcomplex64 as kcomplex64
from pyvqnet.distributed import get_rank as get_rank, get_size as get_size
from pyvqnet.qnn.vqc.qmachine import AbstractQMachine as AbstractQMachine, QMachine as QMachine

class QubitReorderLocalQmachine(QMachine):
    use_qr: bool
    local_qubit: Incomplete
    all_qubit: Incomplete
    states: Incomplete
    global_qubit: Incomplete
    qr_exec: Incomplete
    def __init__(self, q_machine) -> None: ...

class DistributeQMachine(AbstractQMachine):
    world_size: Incomplete
    rank: Incomplete
    log_world_size: Incomplete
    local_qubit: Incomplete
    grad_mode: Incomplete
    def __init__(self, num_wires, dtype=..., grad_mode: str = '') -> None:
        '''
        
        A simulator class for variational quantum computing, including statevectors whose states attribute is a quantum circuit.

        :param num_wires: the number of global qubits.
        :param dtype: The data type of the calculation data. The default is pyvqnet.kcomplex64, and the corresponding parameter precision is pyvqnet.kfloat32.
        :param grad_mode: gradient calculation mode,default: "".use adjoint.

        :return:
            A QMachine instance.

        Example::

            from pyvqnet.distributed.qubits_reorder import DistributeQMachine
            num_wires = 10
            global_qubit = 4
            qm = DistributeQMachine(num_wires)

            qm.set_just_defined(True)
            qm.set_save_op_history_flag(True) # open save op
            qm.set_qr_config({"qubit": num_wires, # open qubit reordered, set config
                                    "global_qubit": global_qubit}) # global_qubit == log2(nproc)
        '''
    qr_config: Incomplete
    use_qr: bool
    def set_qr_config(self, qr_config) -> None: ...
