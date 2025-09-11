from _typeshed import Incomplete

class PQ_QCLOUD_UTILS:
    chip_id: Incomplete
    is_amend: bool
    is_mapping: bool
    is_optimization: bool
    default_task_group_size: int
    test_qcloud_fake: bool
    timeout: Incomplete
    print_query_info: bool
    temp_path: Incomplete
    print_ir: bool
    sub_circuits_split_size: int
    server_ip_address: str
    hacky_measure_nums: int
    shots: int
    def __init__(self) -> None: ...
    def cleanup(self) -> None: ...
    def update_submit_json(self, submit_json) -> None:
        """
        change submit config global.
        """
    def update_query_json(self, query_json) -> None:
        """
        change query config global.
        """
    def get_hacky_measure_nums(self): ...
    def set_hacky_measure_nums(self, hacky_measure_nums) -> None: ...
    def set_test_qcloud_fake(self, value) -> None:
        """
        set_test_qcloud_fake(True) to test function if valid.
        """
    def get_test_qcloud_fake(self): ...
    def reorg_hami(self, pauli_str_dict): ...
    def insert_circuits_with_obs(self, machine, circuits, shots: int = 1000, hamiltonian: Incomplete | None = None, sub_spilt_size: int = 1): ...
    def submit_task_cpuqvm(self, machine, circuits, shots: int = 1000, pauli_str_dict: Incomplete | None = None): ...
    def submit_task_asyn_batched_qcloud(self, machine, circuits, shots: int = 1000, pauli_str_dict: Incomplete | None = None): ...
    def query_by_taskid_sync_batched_qcloud(self, machine, taskids): ...
    def query_by_taskid_cpuqvm(self, machine, taskids): ...

def reverse_output_idx(origin_dict, qubits_len, padding_zero: bool = False): ...
def get_measure_number_from_qprog(qprog, m): ...
def get_measure_number_from_ir(str_ir): ...
def gen_legacy_result(machine, ir, q, c, all_len, shots):
    """
    _parse_dict_fun
    """
def gen_fake_result(machine, ir, q, c, all_len):
    """
    _parse_dict_fun
    """
def parity_check(number): ...
def calc_qmeasure_asyn_batched(outputs, infered_measure_nums: int = -100): ...
def calc_split_circuits_exp_asyn_batched(outputs, qcir_offsets, coffs, pauli_str_dict, sub_circuits_split_size: int = 1): ...
def add_empty_pauli_coeff(Hamiltonian): ...
def calc_exp_asyn_batched(outputs, qcir_offsets, coffs, pauli_str_dict, sub_circuits_split_size: int = 1): ...
def get_one_expectation_component(machine, program, qubit_list, clists, shots: int = 1000, real_chip_type=...):
    """
    get expectation of operator ZiZj....Zm
    """
def get_one_expectation_component_prog(program, qubit_list, clists):
    """
    get expectation of operator ZiZj....Zm
    """
def pauli_str_dict_to_paulioperator(pauli_str_dict): ...
def get_cir_and_coffs_with_hami_obs(program, qubit_list, clists, pauli_str_dict):
    """
    get_cir_and_coffs_with_hami_obs, will omit non pauli

    """
def get_expectation_realchip(machine, qubit_list, program, pauli_str_dict, clists, shots: int = 1000, real_chip_type=...):
    """
    get Hamiltonian's expectation
    """
def hex_to_binary(result, num_qubits): ...
def remapping(circuit_str, mapping: dict[int, int]):
    '''
    remap origin ir to new qubits.

    param circuit_str: single originir.
    param mapping: mapping qubits dict.

    Example::
    
        import pyqpanda3 as pq
        from pyvqnet.qnn.pq_utils import remapping
        ss ="QINIT 8
CREG 8
H q[0]
RY q[0],(-0.164695203304291)
H q[1]
RY q[1],(1.07561600208282)
H q[2]
RY q[2],(-1.66336476802826)
H q[3]
RY q[3],(-1.67083930969238)
H q[4]
RY q[4],(1.89673209190369)
H q[5]
RY q[5],(-1.94548141956329)
H q[6]
RY q[6],(-1.78535354137421)
H q[7]
RY q[7],(1.85956406593323)
CNOT q[0],q[1]
CNOT q[1],q[2]
CNOT q[2],q[3]
CNOT q[3],q[4]
CNOT q[4],q[5]
CNOT q[5],q[6]
CNOT q[6],q[7]
CNOT q[7],q[0]
RX q[0],(4.52745294570923)
RX q[1],(6.13993453979492)
RX q[2],(5.91167688369751)
RX q[3],(1.38978826999664)
RX q[4],(5.748939037323)
RX q[5],(1.54746460914612)
RX q[6],(3.60529494285583)
RX q[7],(0.989788472652435)
MEASURE q[0],c[0]"


        mapping_dict = {0:8,1:9,2:14,3:13,4:12,5:11,6:10}


        ir = remapping(ss,mapping_dict)
        print(ir)

        machine = pq.CPUQVM()
        machine.init_qvm()
        machine.qAlloc_many(15)
        machine.cAlloc_many(15)
        prog,q,l = pq.convert_originir_str_to_qprog(ir, machine)
        shot = 1000
        result = machine.run_with_configuration(prog, shot)
        print(result)
    '''
