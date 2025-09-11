from ..ControlComm import CommController as CommController
from _typeshed import Incomplete
from pyvqnet.nn import BatchNorm1d as BatchNorm1d
from pyvqnet.tensor import AutoGradNode as AutoGradNode, no_grad as no_grad, tensor as tensor
from pyvqnet.utils.initializer import ones as ones, zeros as zeros
from typing import Callable

class BN_SYNC:
    sum_dy_flag: bool
    sum_dy: Incomplete
    sum_dy_xmu: Incomplete

def batch_norm_stats(input, eps): ...
def batch_norm_elemt(input, weight, bias, mean, invstd): ...
def batch_norm_backward_elemt_kernel_impl(input, grad_output, mean, invstd, weight, sum_dy, sum_dy_xmu, norm_fct): ...

class SyncBatchNorm(BatchNorm1d):
    '''
    
    Batch Normalization while doing synchronization of batchnorm statistics.

    :param comm: `CommController` - a CommController for distributed training.
    :param channel_num: `int` - the number of input features channels
    :param momentum: `float` - momentum when calculation exponentially weighted average,
     defaults to 0.1
    :param beta_initializer: `callable` - defaults to zeros
    :param gamma_initializer: `callable` - defaults to ones
    :param epsilon: `float` - numerical stability constant, defaults to 1e-5
    :param name: name of module,default:"".
    :return: a BatchNorm1d class
    
    Example::

        from pyvqnet.distributed import CommController,SyncBatchNorm
        import numpy as np
        import pyvqnet
        from pyvqnet import QTensor

        
        CC = CommController("nccl")
        
        test_conv = SyncBatchNorm(CC, 4)
        test_conv.toGPU(CC.get_rank()+pyvqnet.DEV_GPU_0)
        x = QTensor(np.arange(1,17).reshape([4,4]),requires_grad=True,dtype=pyvqnet.kfloat32,device=CC.get_rank()+pyvqnet.DEV_GPU_0)
        y = test_conv.forward(x)
        y.backward()
 
    '''
    comm_controller: Incomplete
    world_size: Incomplete
    def __init__(self, comm: CommController, channel_num: int, momentum: float = 0.1, epsilon: float = 1e-05, affine: bool = True, beta_initializer: Callable = ..., gamma_initializer: Callable = ..., dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...
