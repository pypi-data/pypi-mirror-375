from _typeshed import Incomplete
from pyvqnet.qnn.ansatz import HardwareEfficientAnsatz as HardwareEfficientAnsatz
from pyvqnet.tensor import tensor as tensor

num_qubit: int
num_sample: int
outputs_y: Incomplete

def plot_hist(data, num_bin, title_str): ...
def haar_unitary(num_qubits: int): ...
def state_fidelity(rho, sigma): ...
def fidelity_harr_sample(n, s, b: int = 50):
    """
    Calculate Harr sample fidelity

    :param n: number of qubits
    :param s: number of sample
    :param b: histogram bin size ,default:50
    
    :return:

            sample distribution
            theory distribution
    """
def get_state(cir_func, num_qubits, depth): ...
def fidelity_of_cir(cir_func, num_qubits, num_depth, s, b: int = 50): ...
