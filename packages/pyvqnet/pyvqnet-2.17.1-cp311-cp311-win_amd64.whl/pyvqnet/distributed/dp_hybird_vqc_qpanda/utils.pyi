from ...device import DEV_CPU as DEV_CPU, DEV_GPU_0 as DEV_GPU_0
from ...distributed import CommController as CommController, all_grad_all_reduce as all_grad_all_reduce, get_local_rank as get_local_rank, post_grad_all_reduce as post_grad_all_reduce
from ...nn.module import Module as Module
from ...qnn.vqc import QuantumLayerAdjoint as QuantumLayerAdjoint
from ...qnn.vqc.qcircuit import vqc_to_originir_list as vqc_to_originir_list
from ...qnn.vqc.qmachine import QMachine as QMachine
from ...qnn.vqc.qop import QModule as QModule
from ...tensor import QTensor as QTensor

def split_module(self, module):
    """split module paramters to different gpu in one node.We assume that every node have a copy of original module."""
def split_data(self, x_train):
    """
    get split input x for every node.
    """
def init_helper(self, Comm_OP: CommController, vqc_module: Module, name: str = ''): ...
