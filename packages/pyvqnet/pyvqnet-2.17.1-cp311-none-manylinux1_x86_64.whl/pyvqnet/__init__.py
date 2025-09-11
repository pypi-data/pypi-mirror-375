# Copyright (c) 2017-2023 Origin Quantum Computing. All Right Reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#pylint:disable=too-many-lines
#pylint:disable=unsubscriptable-object
#pylint:disable=no-name-in-module
#pylint:disable=bare-except
#pylint:disable=unnecessary-lambda
#pylint:disable=wrong-import-position
"""
pyvqnet init
"""

 
import os
import sys
import re
import ctypes


def get_openblas_version_mac():
    possible_paths = [
        "/opt/homebrew/opt/openblas/lib/libopenblas.dylib",   
        "/usr/local/opt/openblas/lib/libopenblas.dylib",      
        "/usr/lib/libopenblas.dylib",                        
        "/opt/OpenBLAS/lib/libopenblas.dylib"               
    ]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                openblas = ctypes.CDLL(path)

                openblas.openblas_get_config.restype = ctypes.c_char_p
                config = openblas.openblas_get_config().decode("utf-8")

                openblas.openblas_get_corename.restype = ctypes.c_char_p
                core_name = openblas.openblas_get_corename().decode("utf-8")

                version_match = re.search(r"OpenBLAS\s+([\d.]+)", config)
                if version_match:
                    version = version_match.group(1)

                    min_required_version = "0.3.29"
                    if version < min_required_version:
                        print(f"Warning: OpenBLAS version {version} is lower than the minimum required {min_required_version}, it is recommended to update!")

                    return version, core_name
                else:
                    print("OpenBLAS version can not be decoded!")

            except OSError:
                print('''OpenBLAS >=0.3.29 is needed!, use brew install openblas first. ''')


if sys.platform == "darwin":
    get_openblas_version_mac()
if sys.platform == 'win32':

    pfiles_path = os.getenv('ProgramFiles', 'C:\\Program Files')
    py_dll_path = os.path.join(sys.exec_prefix, 'Library', 'bin')
    cublas_dll_path = os.path.join(os.path.dirname(__file__), '..\\nvidia\\cublas\\bin')
    cuda_runtime_dll_path =os.path.join(os.path.dirname(__file__), '..\\nvidia\\cuda_runtime\\bin')
    cusolver_dll_path = os.path.join(os.path.dirname(__file__), '..\\nvidia\\cusolver\\bin')

    # When users create a virtualenv that inherits the base environment,
    # we will need to add the corresponding library directory into
    # DLL search directories. Otherwise, it will rely on `PATH` which
    # is dependent on user settings.
    if sys.exec_prefix != sys.base_exec_prefix:
        base_py_dll_path = os.path.join(sys.base_exec_prefix, 'Library', 'bin')
    else:
        base_py_dll_path = ''

    dll_paths = list(filter(os.path.exists, [cublas_dll_path, cuda_runtime_dll_path, cusolver_dll_path,py_dll_path, base_py_dll_path]))

    if all(not os.path.exists(os.path.join(p, 'nvToolsExt64_1.dll')) for p in dll_paths):
        nvtoolsext_dll_path = os.path.join(
            os.getenv('NVTOOLSEXT_PATH', os.path.join(pfiles_path, 'NVIDIA Corporation', 'NvToolsExt')), 'bin', 'x64')
    else:
        nvtoolsext_dll_path = ''

    from .version import CUDA_VERSION as cuda_version
    import glob
    if cuda_version and all(not glob.glob(os.path.join(p, 'cudart64*.dll')) for p in dll_paths):
        cuda_version_1 = cuda_version.replace('.', '_')
        cuda_path_var = 'CUDA_PATH_V' + cuda_version_1
        default_path = os.path.join(pfiles_path, 'NVIDIA GPU Computing Toolkit', 'CUDA', 'v' + cuda_version)
        cuda_path = os.path.join(os.getenv(cuda_path_var, default_path), 'bin')
    else:
        cuda_path = ''

    dll_paths.extend(filter(os.path.exists, [nvtoolsext_dll_path, cuda_path]))

    kernel32 = ctypes.WinDLL('kernel32.dll', use_last_error=True)
    with_load_library_flags = hasattr(kernel32, 'AddDllDirectory')
    prev_error_mode = kernel32.SetErrorMode(0x0001)

    kernel32.LoadLibraryW.restype = ctypes.c_void_p
    if with_load_library_flags:
        kernel32.LoadLibraryExW.restype = ctypes.c_void_p

    for dll_path in dll_paths:
        os.add_dll_directory(dll_path)
        ctypes.windll.kernel32.SetDllDirectoryW(dll_path) 
    os.environ['PATH'] = ';'.join(dll_paths + [os.environ['PATH']])
    try:
        ctypes.CDLL('vcruntime140.dll')
        ctypes.CDLL('msvcp140.dll')
        ctypes.CDLL('vcruntime140_1.dll')
    except OSError:
        print('''Microsoft Visual C++ Redistributable is not installed, this may lead to the DLL load failure.
                 It can be downloaded at https://aka.ms/vs/16/release/vc_redist.x64.exe''')

 

from ._core.vqnet import maybe_set_cuda_lazy_init
maybe_set_cuda_lazy_init()

from . import nn, optim, qnn, tensor, utils, data, _core, dtype, device,backends
from .utils import compare_torch_result
from .dtype import kbool, kcomplex128, kcomplex64, kfloat32, kfloat64, \
    kint16, kint32, kint64, kint8, kuint8, C_DTYPE, Z_DTYPE,\
    get_default_dtype,kcomplex32,kfloat16
from .summary import model_summary, summary

from .tensor import QTensor,no_grad,\
    _tensordot as tensordot,reshape,permute,transpose,einsum#this import is use for opt_einsum,which need this function from pyvqnet
from .config import get_if_show_bp_info, set_if_show_bp_info
from .device import DEV_CPU
from .device import DEV_GPU
from .device import DEV_GPU_0
from .device import DEV_GPU_1
from .device import DEV_GPU_2
from .device import DEV_GPU_3
from .device import DEV_GPU_4
from .device import DEV_GPU_5
from .device import DEV_GPU_6
from .device import DEV_GPU_7
from .device import DEV_GPU_MAX
from .device import if_gpu_compiled, if_nccl_compiled, if_mpi_compiled,\
    get_gpu_free_mem
from .types import _size_type


from .logger import get_should_pyvqnet_use_this_log,set_should_pyvqnet_use_this_log
