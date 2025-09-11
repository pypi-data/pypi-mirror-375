import pyqpanda3.core as pq
from ..pq_utils import hex_to_binary as hex_to_binary, remapping as remapping
from _typeshed import Incomplete
from copy import deepcopy as deepcopy
from pyqpanda3.hamiltonian import PauliOperator as PauliOperator
from pyqpanda3.qcloud import QCloudBackend as QCloudBackend, QCloudJob as QCloudJob, QCloudResult as QCloudResult, QCloudService as QCloudService

current_originqc_chip_type: str

class PQ_QCLOUD_UTILS:
    """
    A class helps to deal with pyqpanda3 qcloud or qvm, including setting configs ,
    do quantum circuits task submit and query and process data to compatible format.
    """
    chip_id: Incomplete
    is_amend: bool
    is_mapping: bool
    is_optimization: bool
    default_task_group_size: int
    test_qcloud_fake: bool
    timeout: Incomplete
    print_query_info: bool
    print_ir: bool
    sub_circuits_split_size: int
    server_ip_address: str
    hacky_measure_nums: int
    shots: int
    total_timeout: Incomplete
    def __init__(self) -> None: ...
    def update_submit_json(self, submit_json) -> None:
        """
        update submit config .
        """
    def update_query_json(self, query_json) -> None:
        """
        update qcloud query config.
        """
    def get_hacky_measure_nums(self): ...
    def set_hacky_measure_nums(self, hacky_measure_nums) -> None: ...
    def set_test_qcloud_fake(self, value) -> None:
        """
        set_test_qcloud_fake(True) to use qvm simulation locally.
        """
    def get_test_qcloud_fake(self): ...
    def reorg_hami(self, pauli_str_dict): ...
    def insert_circuits_with_obs(self, machine, circuits: list[pq.QProg], shots: int = 1000, hamiltonian=None, sub_spilt_size: int = 1):
        """
        insert specific hamiltonian into circuits for expectation before submit to qcloud or qvm.
        """
    def submit_task_qvm(self, machine, circuits, shots: int = 1000, pauli_str_dict=None):
        """
        submit quantum circuit to pyqpanda qvm for simulation.
        """
    def submit_task_asyn_batched_qcloud(self, machine, circuits, shots: int = 1000, pauli_str_dict=None):
        """
        use pyqpanda qcloud api to submit batched task asynchronously.
        """
    def query_by_taskid_sync_batched_qcloud(self, machine, taskids):
        """
        get qcloud or qvm compute result asynchronously.
        """
    def query_by_taskid_qvm(self, machine, taskids):
        """
        cpu or gpu qvm run.
        """

def get_measure_number_from_qprog_or_ir(x): ...
def get_measure_number_from_qprog(qprog): ...
def get_measure_number_from_ir(str_ir): ...
def get_qc_number_from_ir_or_qprog(x): ...
def get_qc_number_from_ir(input_str): ...
def gen_fake_result(machine, prog):
    """
    _parse_result_dict_fun
    """
def parity_check(number): ...
def calc_qmeasure_asyn_batched(outputs, infered_measure_nums: int = -100):
    """
    post process qmeasure outputs
    """
def calc_split_circuits_exp_asyn_batched(outputs, qcir_offsets, coffs, pauli_str_dict, sub_circuits_split_size: int = 1): ...
def add_empty_pauli_coeff(hami): ...
def calc_exp_asyn_batched(outputs, qcir_offsets, coffs, pauli_str_dict, sub_circuits_split_size: int = 1):
    """
    post process batch data(circuits)'s expectation asynchronous
    """
def get_one_expectation_component(machine, program, qubit_list, clists, shots: int = 1000, qtype=..., option=None):
    """
    insert pq.measure and get expecation result.
    """
def get_one_expectation_component_prog(program, qubit_list, clists):
    """
    insert measure into prog
    """
def get_cir_and_coffs_with_hami_obs(program, qubit_list, clists, pauli_str_dict):
    """
    get_cir_and_coffs_with_hami_obs, will omit non pauli

    """
def get_expectation_realchip(machine, qubit_list, program, pauli_str_dict, clists, shots: int = 1000, qtype=..., option=None):
    """
    get Hamiltonian's expectation
    """
def pq3_vqc_run(x, param, pauli_dicts, m_prog_func): ...
