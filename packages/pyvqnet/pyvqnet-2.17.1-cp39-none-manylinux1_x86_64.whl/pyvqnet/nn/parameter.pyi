from ..backends import check_not_default_backend as check_not_default_backend, get_backend as get_backend
from ..types import _size_type
from _typeshed import Incomplete
from pyvqnet.dtype import get_default_dtype as get_default_dtype, kcomplex128 as kcomplex128, kcomplex64 as kcomplex64, kfloat32 as kfloat32, kfloat64 as kfloat64, valid_param_dtype as valid_param_dtype
from pyvqnet.tensor.tensor import QTensor as QTensor
from pyvqnet.utils.initializer import empty as empty, normal as normal
from typing import Callable

class Parameter(QTensor):
    def __init__(self, shape: _size_type = (1, 1), initializer: Callable = ..., device: int | None = None, dtype: int | None = None) -> None:
        """
        Represents one parameter in a neural network


        :param shape: `tuple` - shape of the parameter
        :param initializer: 'callable' - parameter initializer, default to normal
        :param device: run on device, default: None,use cpu. if use GPU,set DEV_GPU_0.
        :param dtype: data type of parameters,default: None,use default data type.
        """
    data: Incomplete
    def init_from_tensor(self, other_tensor) -> None:
        """
        this function copy data from other tensor.
        """
