from . import backends as backends, data as data, device as device, dtype as dtype, nn as nn, optim as optim, qnn as qnn, tensor as tensor, utils as utils
from .config import get_if_show_bp_info as get_if_show_bp_info, set_if_show_bp_info as set_if_show_bp_info
from .device import DEV_CPU as DEV_CPU, DEV_GPU as DEV_GPU, DEV_GPU_0 as DEV_GPU_0, DEV_GPU_1 as DEV_GPU_1, DEV_GPU_2 as DEV_GPU_2, DEV_GPU_3 as DEV_GPU_3, DEV_GPU_4 as DEV_GPU_4, DEV_GPU_5 as DEV_GPU_5, DEV_GPU_6 as DEV_GPU_6, DEV_GPU_7 as DEV_GPU_7, DEV_GPU_MAX as DEV_GPU_MAX, get_gpu_free_mem as get_gpu_free_mem, if_gpu_compiled as if_gpu_compiled, if_mpi_compiled as if_mpi_compiled, if_nccl_compiled as if_nccl_compiled
from .dtype import C_DTYPE as C_DTYPE, Z_DTYPE as Z_DTYPE, get_default_dtype as get_default_dtype, kbool as kbool, kcomplex128 as kcomplex128, kcomplex32 as kcomplex32, kcomplex64 as kcomplex64, kfloat16 as kfloat16, kfloat32 as kfloat32, kfloat64 as kfloat64, kint16 as kint16, kint32 as kint32, kint64 as kint64, kint8 as kint8, kuint8 as kuint8
from .logger import get_should_pyvqnet_use_this_log as get_should_pyvqnet_use_this_log, set_should_pyvqnet_use_this_log as set_should_pyvqnet_use_this_log
from .summary import model_summary as model_summary, summary as summary
from .tensor import QTensor as QTensor, einsum as einsum, no_grad as no_grad, permute as permute, reshape as reshape, transpose as transpose
from .utils import compare_torch_result as compare_torch_result
from _typeshed import Incomplete

def get_openblas_version_mac(): ...

pfiles_path: Incomplete
py_dll_path: Incomplete
cublas_dll_path: Incomplete
cuda_runtime_dll_path: Incomplete
cusolver_dll_path: Incomplete
base_py_dll_path: Incomplete
dll_paths: Incomplete
nvtoolsext_dll_path: Incomplete
cuda_version_1: Incomplete
cuda_path_var: Incomplete
default_path: Incomplete
cuda_path: Incomplete
kernel32: Incomplete
with_load_library_flags: Incomplete
prev_error_mode: Incomplete
