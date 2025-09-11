"""
Init for distributrd
"""
import platform

if "linux" in platform.platform() or "Linux" in platform.platform():
    from .datasplit import *
    from .ControlComm import *
    from .runner import *
    from .tensor_parallel import *
    from .zero import *
    from .syncbatchnorm import SyncBatchNorm
    from .gradient_allreduce import post_grad_all_reduce,all_grad_all_reduce
    from .dp_hybird_vqc_qpanda import DataParallelHybirdVQCQpandaQVMLayer,\
        DataParallelVQCAdjointLayer,DataParallelVQCLayer