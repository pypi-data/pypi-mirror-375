import numpy as np
from ..backends import check_not_default_backend as check_not_default_backend, get_backend as get_backend, global_backend as global_backend
from ..native.backprop_utils import AutoGradNode as AutoGradNode, del_kv_in_global_cache_map as del_kv_in_global_cache_map
from ..types import _axis_type, _scalar_type, _shape_type, _size_type
from .hooks import RemovableHandle as RemovableHandle
from .utils import maybe_wrap_dim as maybe_wrap_dim
from _typeshed import Incomplete
from collections import deque as deque
from functools import reduce as reduce
from pyvqnet.device import DEV_CPU as DEV_CPU, DEV_GPU_0 as DEV_GPU_0, get_readable_device_str as get_readable_device_str
from pyvqnet.dtype import dtype_map as dtype_map, get_default_dtype as get_default_dtype, get_readable_dtype_str as get_readable_dtype_str, kbool as kbool, kcomplex128 as kcomplex128, kcomplex64 as kcomplex64, kfloat32 as kfloat32, kfloat64 as kfloat64, vqnet_complex_dtypes as vqnet_complex_dtypes, vqnet_complex_float_dtypes as vqnet_complex_float_dtypes, vqnet_float_dtypes as vqnet_float_dtypes
from typing import Callable

long = int
integer_types: Incomplete
numeric_types: Incomplete
MIN_FLOAT: Incomplete
MAX_FLOAT: Incomplete

def f(): ...
generate_unique_id = f

class QTensor:
    """
        QTensor is basic data struct for quantum circuits and nerual networks.
        It supports multiple operations and implement their gradient function.
    """
    class GraphNode:
        """
            Helper class which models a node in the computational graph.
            Stores tensor and derivative function of the primitive operation.
        """
        tensor: Incomplete
        name: Incomplete
        df: Incomplete
        device: Incomplete
        def __init__(self, tensor, df, name: str = '') -> None:
            """
            Helper class which models a node in the computational graph.
            Stores tensor and derivative function of the primitive operation.

            :param tensor: currnet QTensor to calculate.
            :param df: 'callable' - derivative function of current operation
            :param name: node name.
            """
    data: Incomplete
    requires_grad: Incomplete
    nodes: Incomplete
    id: Incomplete
    name: Incomplete
    output_idx: int
    def __init__(self, data, requires_grad: bool = False, nodes: list = None, device=..., dtype=None, name: str = '') -> None:
        """
        Wrapper of data structure with dynamic computational graph construction
        and automatic differentiation.

        device specifies the device where the data is stored. When device = DEV_CPU, the data is stored on the CPU,
        and when device >= DEV_GPU_0, the data is stored on the GPU. If your computer has multiple GPUs,
        you can specify different devices for data storage. For example, device = 1001, 1002, 1003,
        ... means stored on GPUs with different serial numbers.

        Note:

            QTensor in different GPU could not do calculation.
            If you try to create a QTensor on GPU with id more than maximum number of validate GPUs, will raise Cuda Error.


        :param data: _core.Tensor or numpy array which represents a tensor
        :param requires_grad: should tensor's gradient be tracked, defaults to False
        :param nodes: list of successors in the computational graph, defaults to None
        :param device: current device to save QTensor , default = 0,stored in cpu. 
        :param dtype: data type, default: None, use input dtype.
        :return: A QTensor

        Example::

            from pyvqnet._core import Tensor as CoreTensor
            t = QTensor(np.ones([2,3]))
            t2 = QTensor(CoreTensor.ones([2,3]))
            t3 =  QTensor([2,3,4,5])
            t4 =  QTensor([[[2,3,4,5],[2,3,4,5]]])
            print(t)
            print(t2)
            print(t4)
            print(t3)

        """
    def set_output_idx(self, idx) -> None: ...
    def get_output_idx(self): ...
    @classmethod
    def maybe_convert_from_torch(cls, t):
        """
        return torch.Tensor if torch-native
        return qtensor otherwise
        """
    @classmethod
    def create_from_torch(cls, t):
        """
        return qtensor
        """
    def __del__(self) -> None: ...
    @property
    def grad(self):
        """
        gradient of QTensor.

        :return: QTensor.
        """
    @grad.setter
    def grad(self, new_value: bool): ...
    def register_hook(self, f: Callable): ...
    def hook_function(self): ...
    @property
    def requires_grad(self): ...
    @requires_grad.setter
    def requires_grad(self, new_value: bool): ...
    def __hash__(self): ...
    def __deepcopy__(self, memo):
        """
        Deep copy Tensor, it will always performs Tensor copy.

        """
    def zero_grad(self):
        """
        Sets gradient to zero. Will be used by optimizer in the optimization process.

        :return: None

        Example::

            t3 = QTensor([2,3,4,5],requires_grad = True)
            t3.zero_grad()
            print(t3.grad)
        """
    def backward(self, grad=None, save_grad: bool = False, save_intern_act: bool = True):
        """
        Backward function for QTensor,can input specific value.

        :param grad: a numpy or QTensor as input gradient value,default:None
        :param save_grad: for saving memory, non-paramters' gradients data will be delete if save_grad == False,
        default: False.
        :param save_intern_act: if save_intern_act == True, inernal activation data will be saved ,default:True.
        :return: None

        Note:
            save_intern_act is used for backward compatibility,save_intern_act == False will save peak memory usage.
            However, it will not delete internal data in forward function.

        Example::

           t3  =  QTensor([2,3,4,5],requires_grad = True)
           y = t3 + 4
           y.backward()
        """
    def to_numpy(self): ...
    def numpy(self):
        """

        return a numpy ndarray shares same data with qtensor.

        :return: a numpy array

        Example::

           t3  =  QTensor([2,3,4,5],requires_grad = True)
           t4 = t3.numpy()
        """
    def matmul(self, other): ...
    def argmax(self, dim: _axis_type = None, keepdims: bool = None):
        """        Returns the indices of the maximum value of all elements in the input tensor,or
        Returns the indices of the maximum values of a tensor across a dimension.

        :param dim: dim (int) – the dimension to reduce,only accepts single axis.
                    if dim is None, returns the indices of the maximum value of all
                    elements in the input tensor.
                    The valid dim range is [-R, R), where R is input's ndim. when dim < 0,
                    it works the same way as dim + R.

        :param keepdims: keepdim (bool) – whether the output tensor has dim retained or not.

        :return: the indices of the maximum value in the input tensor.

        Examples::

            a = QTensor([[1.3398, 0.2663, -0.2686, 0.2450],
                       [-0.7401, -0.8805, -0.3402, -1.1936],
                       [0.4907, -1.3948, -1.0691, -0.3132],
                       [-1.6092, 0.5419, -0.2993, 0.3195]])
            flag = a.argmax()
            #[0.000000]
            flag_0 = a.argmax(0, True)
            #[
            #[0.000000, 3.000000, 0.000000, 3.000000]
            #]
            flag_1 = a.argmax(1, True)

        """
    def __matmul__(self, other): ...
    def __rmatmul__(self, other): ...
    def is_complex(self): ...
    def is_float(self): ...
    is_floating_point = is_float
    def mean(self, axis: _axis_type = None, keepdims: bool = False): ...
    def median(self, axis: _axis_type = None, keepdims: bool = False): ...
    def max(self, axis: _axis_type = None, keepdims: bool = False): ...
    def min(self, axis: _axis_type = None, keepdims: bool = False): ...
    def argmin(self, dim: _axis_type = None, keepdims: bool = None):
        """        Returns the indices of the minimum value of all elements in the input tensor, or
        Returns the indices of the minimum values of a tensor across a dimension.

        :param dim: dim (int) – the dimension to reduce,only accepts single axis.
                    if dim is None, returns the indices of the minimum
                    value of all elements in the input tensor.
                    The valid dim range is [-R, R), where R is input's ndim.
                    when dim < 0, it works the same way as dim + R.
        :param keepdims: keepdim (bool) – whether the output tensor has dim retained or not.

        :return: the indices of the minimum  value in the input tensor.

        Examples::

            a = QTensor([[1.3398, 0.2663, -0.2686, 0.2450],
                       [-0.7401, -0.8805, -0.3402, -1.1936],
                       [0.4907, -1.3948, -1.0691, -0.3132],
                       [-1.6092, 0.5419, -0.2993, 0.3195]])
            flag = a.argmin()
            flag_0 = a.argmin(0, True)
            flag_1 = a.argmin(1, False)

        """
    def fill_(self, v: _scalar_type):
        """        Fill the tensor with the specified value inplace.

        :param v: a scalar value to fill
        :return: None

        Examples::

            shape = [2, 3]
            value = 42
            t = tensor.zeros(shape)
            t.fill_(value)
        """
    def all(self):
        """        Return if all tensor value is non-zero.

        :return: `bool` True,if all tensor value is non-zero.

        Examples::

            shape = [2, 3]
            t = tensor.zeros(shape)
            t.fill_(1.0)
            flag = t.all()
        """
    def l2_norm(self):
        """        Return if l2_norm value.

        :return: return if l2_norm value.

        Examples::

            shape = [2, 3]
            t = tensor.zeros(shape)
            t.fill_(1.0)
            flag = t.l2_norm()
        """
    def any(self):
        """        Return if any tensor value is non-zero.

        :return: True,if any tensor value is non-zero.

        Examples::

            shape = [2, 3]
            t = tensor.ones(shape)
            t.fill_(1.0)
            flag = t.any()
        """
    def fill_rand_uniform_with_bound_(self, min_value: _scalar_type, max_value: _scalar_type):
        """        Fills a tensor with values randomly sampled from a uniform distribution
         in the range of (min,max)

        :param min_value: down bound
        :param max_value: up bound
        :return: None

        Examples::

            a = np.arange(6).reshape(2, 3).astype(np.float32)
            t = QTensor(a)

            t.fill_rand_uniform_with_bound_(0.5,0.75)
        """
    def fill_rand_uniform_(self, v: _scalar_type = 1):
        """        Fills a tensor with values randomly sampled from a uniform distribution

        Scale factor of the values generated by the uniform distribution.

        :param v: a scalar value,default = 1.
        :return: None

        Examples::

            a = np.arange(6).reshape(2, 3).astype(np.float32)
            t = QTensor(a)
            value = 42
            t.fill_rand_uniform_(value)
        """
    def fill_rand_signed_uniform_(self, v: _scalar_type = 1):
        """        Fills a tensor with values randomly sampled from a signed uniform distribution

        Scale factor of the values generated by the signed uniform distribution.

        :param v: a scalar value,default = 1.
        :return: None

        Examples::

            a = np.arange(6).reshape(2, 3).astype(np.float32)
            t = QTensor(a)
            value = 42
            t.fill_rand_signed_uniform_(value)
        """
    def fill_rand_normal_(self, m: _scalar_type = 0, s: _scalar_type = 1, fast_math: bool = True):
        """        Fills a tensor with values randomly sampled from a normal distribution
        Mean of the normal distribution. Standard deviation of the normal distribution.
        Whether to use or not the fast math mode.

        :param m: mean a scalar value,default = 0.
        :param s: std a scalar value,default = 1.
        :param fast_math: True if use fast-math
        :return: None

        Examples::

            a = np.arange(6).reshape(2, 3).astype(np.float32)
            t = QTensor(a)
            t.fill_rand_normal_(2, 10, True)

        """
    def fill_rand_binary_(self, v: _scalar_type = 0.5):
        """        Fills a tensor with values randomly sampled from a binary distribution

        Binarization threshold. compare each data with v ,return 1 if data >= v, 0 otherwise

        :param v: threshold a scalar value 1 if data >= t, 0 otherwise
        :return: None

        Examples::

            a = np.arange(6).reshape(2, 3).astype(np.float32)
            t = QTensor(a)
            t.fill_rand_binary_(2)
        """
    def transpose(self, new_dims: _axis_type = None):
        """        Reverse or permute the axes of an array.if new_dims = None, revsers the dim.

        :param new_dims: the new order of the dimensions (list of integers).
        :return: a new QTensor.

        Examples::

            R, C = 3, 4
            a = np.arange(R * C).reshape([2,2,3]).astype(np.float32)
            t = QTensor(a)
            reshape_t = t.transpose([2,0,1])
        """
    def squeeze(self, axis: _axis_type = None):
        """
        QTensor wrapper of tensor.squeeze()
        """
    def unsqueeze(self, axis: _axis_type):
        """
        QTensor wrapper of tensor.unsqueeze()
        """
    def permute(self, permute_dim: _size_type):
        """
        QTensor wrapper of tensor.permute()
        """
    def moveaxis(self, source: _size_type, destination: _size_type):
        """
            QTensor wrapper of tensor.moveaxis()
        """
    def reshape_as(self, other): ...
    def view(self, shape: _size_type):
        """
        Returns a new tensor with the same data as the :attr:`self` tensor but of a
        different :attr:`shape`.

        The returned tensor shares the same data and must have the same number
        of elements, but may have a different size. For a tensor to be viewed, the new
        view size must be compatible with its original size and stride, i.e., each new
        view dimension must either be a subspace of an original dimension, or only span
        across original dimensions :math:`d, d+1, \\dots, d+k` that satisfy the following
        contiguity-like condition that :math:`\x0corall i = d, \\dots, d+k-1`,

        .. math::

        \text{stride}[i] = \text{stride}[i+1] \times \text{size}[i+1]

        Otherwise, it will not be possible to view :attr:`self` tensor as :attr:`shape`
        without copying it (e.g., via :meth:`contiguous`). When it is unclear whether a
        :meth:`view` can be performed, it is advisable to use :meth:`reshape`, which
        returns a view if the shapes are compatible, and copies (equivalent to calling
        :meth:`contiguous`) otherwise.

        :param shape: the desired size

        Example::

            import numpy as np
            from pyvqnet.tensor import QTensor
            R, C = 3, 4
            a = np.arange(R * C).reshape(R, C).astype(np.float32)
            t = QTensor(a)
            reshape_t = t.view([C, R])
            print(reshape_t)
        """
    def reshape(self, new_shape: _size_type):
        """        Change the tensor's shape, return a new Tensor.

        :param new_shape: the new shape (list of integers)
        :return: new QTensor

        Examples::

            import numpy as np
            from pyvqnet.tensor import QTensor
            R, C = 3, 4
            a = np.arange(R * C).reshape(R, C).astype(np.float32)
            t = QTensor(a)
            reshape_t = t.reshape([C, R])
            print(reshape_t)
            -------------------------------------------
                [
                [0.000000, 1.000000, 2.000000],

                [3.000000, 4.000000, 5.000000],

                [6.000000, 7.000000, 8.000000],

                [9.000000, 10.000000, 11.000000]
                ]
            ------------------------------------------

        """
    def reshape_(self, new_shape: _size_type):
        """        Change the current object's shape.

        :param new_shape: the new shape (list of integers)
        :return: None

        Examples::

            R, C = 3, 4
            a = np.arange(R * C).reshape(R, C).astype(np.float32)
            t = QTensor(a)
            t = t.reshape([C, R])
            print(t)
            -------------------------------------------
                [
                [0.000000, 1.000000, 2.000000],
                [3.000000, 4.000000, 5.000000],
                [6.000000, 7.000000, 8.000000],
                [9.000000, 10.000000, 11.000000]
                ]
            ------------------------------------------
        """
    def flatten(self, start: int = 0, end: int = -1):
        """
        Flatten tensor from dim start to dim end.

        :param start: 'int' - dim start
        :param end: 'int' - dim start
        :return:  A QTensor

        Example::

            t = QTensor([1, 2, 3])
            x = t.flatten()
        """
    def norm(self, axis: _axis_type = None):
        """
        get l2 norm value,this function is autograd.
        """
    @property
    def print_prev_node(self): ...
    @property
    def dtype_str(self):
        """        Returns data type

        :return: data type
        """
    @property
    def dtype(self):
        """        Returns data type

        :return: data type
        """
    @property
    def device(self):
        """        Returns data type

        :return: data type
        """
    @property
    def ndim(self):
        """        Returns number of dimensions

        :return: number of dimensions
        """
    def dim(self, axis: int | None = None):
        """
        Return number of dimension if axis is None, return specific dimension of axis if is not None.

        :param axis: default:None,return dimension numbers.return specific dimension of axis if is not None. 
        """
    @property
    def pdata(self): ...
    @property
    def shape(self):
        """
        Returns the shape of the tensor.

        :return: shape
        """
    @property
    def stride(self):
        """
        Returns the stride of the tensor.

        :return: strides
        """
    def numel(self):
        """
        Returns the number of elements in the tensor.

        :return: number of elements
        """
    @property
    def size(self):
        """
        Returns the number of elements in the tensor.

        :return: number of elements
        """
    @property
    def layout(self):
        """        Returns data layout.

        :return: 0 if data is dense, !=0 if data is not dense.
        """
    @property
    def is_sparse(self): ...
    @property
    def is_dense(self):
        """        Returns if data is dense.

        :return: 1 if data is dense
        """
    @property
    def is_csr(self):
        """        Returns if data is CSR sparse tensor.

        :return: 1 if data is sparse tensor.
        """
    is_sparse_csr = is_csr
    def csr_members(self):
        """        Returns tuple of CSR (row_ptr, col_idx, value)

        :return: Returns tuple of CSR (row_ptr, col_idx, value)
        """
    @property
    def nnz(self):
        """        Returns number of nnz in csr sparse QTensor.
        """
    def info(self) -> None:
        """        Print info on the tensor (shape, strides, ...).

        :return: None

        Examples::

            a = np.arange(6).reshape(2, 3).astype(np.float32)
            t = QTensor(a)
            t.info()


        """
    @property
    def is_cpu(self): ...
    @property
    def is_gpu(self): ...
    @property
    def is_contiguous(self):
        """        Returns if data is is_contiguous.

        :return: true if data is is_contiguous.
        """
    def item(self):
        """
        Returns the only element from in the tensor.
        ## Raises
        'RuntimeError' if tensor has more than 1 element.

        :return: only data of this object

        Examples::

          t = tensor.ones([1])
          print(t.item())
        """
    def is_floating_point_or_complex(self):
        """
        return true is self is float, double or complex,return false otherwise.
        """
    def broadcast_to(self, ref: _shape_type):
        """
        Subject to certain constraints, the array t is “broadcast” to the
        reference shape, so that they have compatible shapes.

        https://numpy.org/doc/stable/user/basics.broadcasting.html

        :param ref: reference shape.
        :return : new broadcasted QTensor of self.

        Examples::

            from pyvqnet.tensor.tensor import QTensor
            ref = [2,3,4]
            a = ones([4])
            b = a.broadcast_to(ref)
        """
    def contiguous(self):
        """
        Return contiguous data of input if input is not contiguous, return self otherwise.

        :return: contiguous data

        Example::
            import pyvqnet

            a = pyvqnet.tensor.ones([4,5])
            a = a.permute((1,0))
            b = a.contiguous()
            print(b.is_contiguous)
        """
    def getdata(self):
        """        Get the tensor's data as a NumPy array.

        :return: a NumPy array

        Examples::

          t = tensor.ones([3, 4])
          a = t.getdata()
            ----------------
            [[1. 1. 1. 1.]
             [1. 1. 1. 1.]
             [1. 1. 1. 1.]]
            ----------------

        """
    def GPU(self, device=...):
        """
        Clone a new QTensor into specific GPU device.

        device specifies the device where the it's inner data is stored. When device = DEV_CPU, the data is stored on the CPU, and when device >= DEV_GPU_0, the data is stored on the GPU. If your computer has multiple GPUs, you can specify different devices for data storage. For example, device = 1001, 1002, 1003, ... means stored on GPUs with different serial numbers.

        Note:

            QTensor in different GPU could not do calculation. 
            If you try to create a QTensor on GPU with id more than maximum number of validate GPUs, will raise Cuda Error.
            new Tensor will remove its GraphNode.
        :param device: current device to save QTensor , default = 0,stored in cpu. device= pyvqnet.DEV_GPU_0, stored in 1st GPU, devcie  = 1001,stored in 2nd GPU,and so on

        :return: the QTensor clone to GPU device

        Example::

                from pyvqnet.tensor import QTensor
                a = QTensor([2])
                b = a.GPU()
                print(b.device)
                #1000
        """
    gpu = GPU
    def cpu(self): ...
    def CPU(self):
        """
        Clone QTensor into specific CPU device.

        device specifies the device where the it's inner data is stored. When device = DEV_CPU, the data is stored on the CPU, and when device >= DEV_GPU, the data is stored on the GPU. If your computer has multiple GPUs, you can specify different devices for data storage. For example, device = 1001, 1002, 1003, ... means stored on GPUs with different serial numbers.
           
        The output of CPU() will remove current GraphNode.

        :return: the QTensor move to CPU device

        Example::

                from pyvqnet.tensor import QTensor
                a = QTensor([2])
                b = a.CPU()
                print(b.device)
                # 0
        """
    def to_gpu(self, device=...): ...
    def toGPU(self, device=...):
        """
        Move QTensor into specific GPU device.

        device specifies the device where the it's inner data is stored. When device = DEV_CPU, the data is stored on the CPU, and when device >= DEV_GPU, the data is stored on the GPU. If your computer has multiple GPUs, you can specify different devices for data storage. For example, device = 1001, 1002, 1003, ... means stored on GPUs with different serial numbers.

        Note:

            QTensor in different GPU could not do calculation. 
            If you try to create a QTensor on GPU with id more than maximum number of validate GPUs, will raise Cuda Error.
           
        :param device: current device to save QTensor , default = 0,stored in cpu. device= pyvqnet.DEV_GPU_0, stored in 1st GPU, devcie  = 1001,stored in 2nd GPU,and so on

        :return: the QTensor move to GPU device

        Example::

                from pyvqnet.tensor import QTensor
                a = QTensor([2])
                a = a.toGPU()
                print(a.device)
                #1000
        """
    def move_to_device(self, device):
        """
        Inplace move data to device
        """
    def copy_to_device(self, device):
        """
        create new copy in new device
        """
    to = copy_to_device
    def to_cpu(self):
        """
        Move QTensor into specific CPU device.

        device specifies the device where the it's inner data is stored. When device = DEV_CPU, the data is stored on the CPU, and when device >= DEV_GPU, the data is stored on the GPU. If your computer has multiple GPUs, you can specify different devices for data storage. For example, device = 1001, 1002, 1003, ... means stored on GPUs with different serial numbers.
           
        :return: the QTensor move to CPU device

        Example::

                from pyvqnet.tensor import QTensor
                a = QTensor([2])
                a = a.toCPU()
                print(a.device)
                # 0
        """
    toCPU = to_cpu
    def isCPU(self):
        """
        whether this QTensor's data store on CPU Host Memory.

        :return: whether this QTensor's data store on CPU Host Memory.

        Example::

                from pyvqnet.tensor import QTensor
                a = QTensor([2])
                a = a.isCPU()
                print(a)
                # True
        """
    def isGPU(self):
        """
        whether this QTensor's data store on GPU Device Memory.

        :return: whether this QTensor's data store on GPU Device Memory.

        Example::

                from pyvqnet.tensor import QTensor
                a = QTensor([2])
                a = a.isGPU()
                print(a)
                # False
        """
    @property
    def is_cuda(self): ...
    def __len__(self) -> int: ...
    def unbind(self, dim: int = 0): ...
    def __iter__(self): ...
    def __getitem__(self, item):
        """
        Supports pyslice,integer or QTensor as slice index to slice the QTensor.
        Returns a new QTensor.

        .. note:: a[3][4][1] is not support, use a[3,4,1] instead.
                  Ellipsis `...` is not support.

        :param item: pyslice or integer or QTensor to slice the QTensor.
        :return: new sliced QTensor

        Example::

            from pyvqnet.tensor import tensor, QTensor
            aaa = tensor.arange(1, 61)
            aaa = aaa.reshape([4, 5, 3])
            print(aaa[0:2, 3, :2])
            # [
            # [10.0000000, 11.0000000],
            #  [25.0000000, 26.0000000]
            # ]
            print(aaa[3, 4, 1])
            #[59.0000000]
            print(aaa[:, 2, :])
            # [
            # [7.0000000, 8.0000000, 9.0000000],
            #  [22.0000000, 23.0000000, 24.0000000],
            #  [37.0000000, 38.0000000, 39.0000000],
            #  [52.0000000, 53.0000000, 54.0000000]
            # ]
            print(aaa[2])
            # [
            # [31.0000000, 32.0000000, 33.0000000],
            #  [34.0000000, 35.0000000, 36.0000000],
            #  [37.0000000, 38.0000000, 39.0000000],
            #  [40.0000000, 41.0000000, 42.0000000],
            #  [43.0000000, 44.0000000, 45.0000000]
            # ]
            print(aaa[0:2, ::3, 2:])
            # [
            # [[3.0000000],
            #  [12.0000000]],
            # [[18.0000000],
            #  [27.0000000]]
            # ]
            a = tensor.ones([2, 2])
            b = QTensor([[1, 1], [0, 1]])
            b = b > 0
            c = a[b]
            print(c)
            #[1.0000000, 1.0000000, 1.0000000]
            tt = tensor.arange(1, 56 * 2 * 4 * 4 + 1).reshape([2, 8, 4, 7, 4])
            tt.requires_grad = True
            index_sample1 = tensor.arange(0, 3).reshape([3, 1])
            index_sample2 = QTensor([0, 1, 0, 2, 3, 2, 2, 3, 3]).reshape([3, 3])
            gg = tt[:, index_sample1, 3:, index_sample2, 2:]
            print(gg)
            # [
            # [[[[87.0000000, 88.0000000]],
            # [[983.0000000, 984.0000000]]],
            # [[[91.0000000, 92.0000000]],
            # [[987.0000000, 988.0000000]]],
            # [[[87.0000000, 88.0000000]],
            # [[983.0000000, 984.0000000]]]],
            # [[[[207.0000000, 208.0000000]],
            # [[1103.0000000, 1104.0000000]]],
            # [[[211.0000000, 212.0000000]],
            # [[1107.0000000, 1108.0000000]]],
            # [[[207.0000000, 208.0000000]],
            # [[1103.0000000, 1104.0000000]]]],
            # [[[[319.0000000, 320.0000000]],
            # [[1215.0000000, 1216.0000000]]],
            # [[[323.0000000, 324.0000000]],
            # [[1219.0000000, 1220.0000000]]],
            # [[[323.0000000, 324.0000000]],
            # [[1219.0000000, 1220.0000000]]]]
            # ]

        """
    def __setitem__(self, key, value) -> None:
        """
        Supports pyslice,integer or QTensor as slice index to set sliced QTensor.
        This function modify QTensor in-place.

        .. note:: a[3][4][1] is not support, use a[3,4,1] instead.
                  Ellipsis `...` is not support.

        :param item: pyslice or integer or QTensor to get sliced QTensor.
        :return: None

        Example::

            aaa = tensor.arange(1, 61)
            aaa = aaa.reshape([4, 5, 3])
            vqnet_a2 = aaa[3, 4, 1]
            aaa[3, 4, 1] = tensor.arange(10001,
                                            10001 + vqnet_a2.size).reshape(vqnet_a2.shape)
            print(aaa)

            aaa = tensor.arange(1, 61)
            aaa = aaa.reshape([4, 5, 3])
            vqnet_a3 = aaa[:, 2, :]
            aaa[:, 2, :] = tensor.arange(10001,
                                            10001 + vqnet_a3.size).reshape(vqnet_a3.shape)
            print(aaa)

            aaa = tensor.arange(1, 61)
            aaa = aaa.reshape([4, 5, 3])
            vqnet_a4 = aaa[2, :]
            aaa[2, :] = tensor.arange(10001,
                                        10001 + vqnet_a4.size).reshape(vqnet_a4.shape)
            print(aaa)

            aaa = tensor.arange(1, 61)
            aaa = aaa.reshape([4, 5, 3])
            vqnet_a5 = aaa[0:2, ::2, 1:2]
            aaa[0:2, ::2,
                1:2] = tensor.arange(10001,
                                        10001 + vqnet_a5.size).reshape(vqnet_a5.shape)
            print(aaa)

            a = tensor.ones([2, 2])
            b = tensor.QTensor([[1, 1], [0, 1]])
            b = b > 0
            x = tensor.QTensor([1001, 2001, 3001])

            a[b] = x
            print(a)

            tt = tensor.arange(1, 56 * 2 * 4 * 4 + 1).reshape([2, 8, 4, 7, 4])
            index_sample = tensor.arange(0, 3).reshape([3, 1])
            index_sample1 = QTensor([0, 1, 0, 2, 3, 2, 2, 3, 3]).reshape([3, 3])
            gg = tt[:, index_sample, 3:, index_sample1, 2:]
            gg = QTensor(gg.to_numpy())
            gg.requires_grad = True
            tt = tensor.arange(1001, 56 * 2 * 4 * 4 + 1001).reshape([2, 8, 4, 7, 4])
            index_sample = tensor.arange(0, 3).reshape([3, 1])
            index_sample1 = QTensor([0, 1, 0, 2, 3, 2, 2, 3, 3]).reshape([3, 3])
            tt[:, index_sample, 3:, index_sample1, 2:] = gg
            print(tt)

        """
    def __bool__(self) -> bool: ...
    def __add__(self, t): ...
    def __iadd__(self, t): ...
    def __imul__(self, t): ...
    def __isub__(self, t): ...
    def __idiv__(self, t): ...
    def __radd__(self, t): ...
    def __sub__(self, t): ...
    def __rsub__(self, t): ...
    def __mul__(self, t): ...
    def __rmul__(self, t): ...
    def __neg__(self): ...
    def __truediv__(self, t): ...
    def __rtruediv__(self, t): ...
    def __pow__(self, t): ...
    def __rpow__(self, t): ...
    def __eq__(self, other): ...
    def __ne__(self, other): ...
    def __lt__(self, other): ...
    def __gt__(self, other): ...
    def __le__(self, other): ...
    def __ge__(self, other): ...
    def __and__(self, other): ...
    copy_: Incomplete
    def copy_value_from(self, other_tensor):
        """
        Copy input qtensor C data to self. If other_tensor.dtype != self.dtype ,convert to self.dtype
        
        :param qtensor: from which qtensor to copy form
        
        return: None
        """
    init_from_tensor = copy_value_from
    def float(self): ...
    def copy_(self, src):
        """
        copy from
        """
    def copy(self):
        """
        Create a new QTensor with same data value as self,while the grad and graph nodes are empty.

        """
    def chunk(self, chunks: int, dim: int = 0):
        """
        QTensor method of chunk
        """
    def split(self, split_size_or_sections: int | list[int] | tuple[int, ...], dim: int = 0):
        """
        QTensor method of split
        """
    def clamp(self, min: int | float | None = None, max: int | float | None = None):
        """
        QTensor method of clamp
        """
    def narrow(self, dim: int, start: int, length: int):
        """
        QTensor method of narrow
        """
    def square(self):
        """
        QTensor method of square
        """
    def sum(self, axis: _axis_type = None, keepdims: bool = False):
        """
        QTensor method of sum
        """
    def isinf(self):
        """
        QTensor method of isinf
        """
    def isnan(self):
        """
        QTensor method of isnan
        """
    def logical_or(self, t2):
        """
        QTensor method of logical_or
        """
    def logical_not(self):
        """
        QTensor method of logical_not
        """
    def detach(self):
        """
        Create a tensor shares same data, while removes autograd graph nodes.
        """
    def exp(self): ...
    def masked_fill(self, mask, value: float | int): ...
    def clone(self):
        """
        Copy tensor data and its GraphNode, This function is differentiable,
          so gradients will flow back from the result of this operation.

        Example::

            import pyvqnet
            from pyvqnet.tensor import tensor,QTensor
            x = QTensor([[1, 2, 3],[4,5,6.0]], requires_grad=True)
            y = 1-x
            z = tensor.concatenate((x,y),1)
            z1 = z.clone()
            z.backward()
        """
    @property
    def is_bool(self): ...
    def astype(self, dtype):
        """
        return new tensor with target data type `dtype`

        :param dtype: data type
        :return: new tensor
        """
    type = astype
    def add(self, t):
        """
        return self + t(int,bool,float complex or qtensor,ndarray)
        """
    def add_(self, t):
        """
        inplace impl self + t(int,bool,float complex or qtensor,ndarray)
        return self
        """
    def sub(self, t):
        """
        return self - t(int,bool,float complex or qtensor,ndarray)
        """
    def sub_(self, t):
        """
        inplace impl self - t(int,bool,float complex or qtensor,ndarray)
        return self
        """
    def mul(self, t):
        """
        return self * t(int,bool,float complex or qtensor,ndarray)
        """
    mult = mul
    def mul_(self, t):
        """
        inplace impl self - t(int,bool,float complex or qtensor,ndarray)
        return self
        """
    mult_ = mul_
    def div(self, t):
        """
        return self / t(int,bool,float complex or qtensor,ndarray)
        """
    def div_(self, t):
        """
        inplace impl self / t(int,bool,float complex or qtensor,ndarray)
        return self
        """
    def clamp_(self, min: int | float, max: int | float):
        """
        inplace impl clamp(self)
        return self
        """
    def conj(self):
        """
        return conjugate of self
        """
    def real(self):
        """
        returns a new tensor containing real values of the self tensor
        """
    def imag(self):
        """
        returns a new tensor containing imaginary  values of the self tensor
        """

def is_tensor(x):
    """
    return if x is QTensor

    :return: return true if x is QTensor type.
    """
def as_qtensor(x):
    """
    return qtensor or torch.tensor
    """
def to_tensor(x):
    """
    Convert input (list,np.ndarray) to Qtensor if it isn't already.

    :param x: 'QTensor-like' - input parameter
    :return: QTensor or torch.tensor

    Example::

        from pyvqnet.tensor import tensor
        t = tensor.to_tensor(10.0)

    """
def empty(shape: _size_type, device: int = 0, dtype=None):
    """
    Return empty QTensor with the input shape. Data in the QTensor is intialized with random data.

    :param shape: shape to created.
    :param device: device to use,default = 0,use cpu device.
    :param dtype: data type, default: None, use default data type.
    :return with the input shape.

    Example::

        from vqnet.tensor import tensor
        x = tensor.empty([2,3])

    """
def empty_like(t, device=None, dtype=None):
    """
    Return empty tensor with the same shape as the input tensor.

    :param t: 'QTensor' - input parameter
    :param device: device to use,default = None, use input device.
    :param dtype: data type, default: None, use input dtype.
    :return:  A QTensor

    Example::

        t = QTensor([1, 2, 3])
        x = tensor.empty_like(t)

    """
def ones(shape: _size_type, device: int = 0, dtype=None):
    """
    Return QTensor contains 1 with the input shape.

    :param shape: shape to created.
    :param device: which device(cpu/gpu),default = 0,use cpu device.
    :param dtype: data type, default: None, use default data type.
    :return with the input shape.

    Example::

        from vqnet.tensor import tensor
        from vqnet.tensor.tensor import QTensor
        x = tensor.ones([2,3])

    """
def ones_like(t, device=None, dtype=None):
    """
    Return one-tensor with the same shape as the input tensor.

    :param t: 'QTensor' - input parameter
    :param device: which device(cpu/gpu),default = None,use input data device.
    :param dtype: data type, default: None, use input data type.
    :return:  A QTensor

    Example::

        t = QTensor([1, 2, 3])
        x = tensor.ones_like(t)

    """
def full(shape: _size_type, value: float | int, device: int = 0, dtype=None):
    """    Create a tensor of the specified shape and fill it with ``value``.

    :param shape: shape of the tensor to create
    :param value: value to fill the tensor with
    :param device: device to use,default = 0,use cpu device.
    :param dtype: data type, default: None, use default data type.
    :return: A QTensor

    Examples::

        shape = [2, 3]
        value = 42
        t = tensor.full(shape, value)

    """
def norm(t, axis: _axis_type = None):
    """
    get l2 norm value,this function is autograd.
    """
def full_like(t, value: float | int, device=None, dtype=None):
    """    Create a tensor of the specified shape and fill it with ``value``.

    :param t:  input qtensor
    :param device: device to use,default = None use input device.
    :param value: value to fill the tensor with.
    :param dtype: data type, default: None, use input dtype.
    :return: A QTensor

    Examples::

        a = tensor.randu([3,5])
        value = 42
        t = tensor.full_like(a, value)

    """
def zeros_like(t, device=None, dtype=None):
    """
    Return zero-tensor with the same shape as the input tensor.

    :param t: 'QTensor' - input parameter
    :param device: device to use,default = None,use input device.
    :param dtype: data type, default: None, use input dtype.
    :return:  A QTensor

    Example::

        t = QTensor([1, 2, 3])
        x = tensor.zeros_like(t)

    """
def zeros(shape: _size_type, device=..., dtype=None):
    """
    Return zero-tensor of the passed shape.

    :param shape: shape of tensor
    :param device: device to use,default = 0,use cpu device.
    :param dtype: data type, default: None, use default data type.
    :return:  A QTensor

    Example::

        t = tensor.zeros([2, 3, 4])
    """
def arange(start: float | int, end: float | int, step: float | int = 1, device: int = 0, dtype=None, requires_grad: bool = False):
    """    Create a 1D tensor with evenly spaced values within a given interval.
    Bool, Complex128, Complex64 type is not supported.

    default data type are float32.

    :param start: start of interval
    :param end: end of interval
    :param step: spacing between values
    :param device: device to use,default = 0,use cpu device.
    :param dtype: data type, default: None, use default data type.
    :param requires_grad: if need to calculate grad in backward(),default = False
    :return:  A QTensor

    Examples::

        t = tensor.arange(2,30,4)
        print(t)

    """
def linspace(start: float | int, end: float | int, nums: int, device: int = 0, dtype=None, requires_grad: bool = False):
    """    Create a 1D tensor with evenly spaced values within a given interval.
    Bool, Complex128, Complex64 type is not supported.

    :param start: starting value
    :param end: end value
    :param nums: number of samples to generate
    :param device: device to use,default = 0,use cpu device.
    :param dtype: data type, default: None, use default data type.
    :param requires_grad: if need to calculate grad in backward(),default = False
    :return:  A QTensor

    Examples::

        start, stop, num = -2.5, 10, 10
        t = tensor.linspace(start, stop, num)
    """
def logspace(start: float | int, end: float | int, nums: int, base: float | int, device: int = 0, dtype=None, requires_grad: bool = False):
    """    Create a 1D tensor with evenly spaced values on a log scale.
    Bool, Complex128, Complex64 type is not supported.
    
    :param start: ``base ** start`` is the starting value
    :param end: ``base ** end`` is the final value of the sequence
    :param nums: number of samples to generate
    :param base: the base of the log space
    :param device: device to use,default = 0,use cpu device.
    :param dtype: data type, default: None, use default data type.
    :param requires_grad: if need to calculate grad in backward(),default = False
    :return:  A QTensor

    Examples::

        start, stop, num, base = 0.1, 1.0, 5, 10.0
        t = tensor.logspace(start, stop, num, base)
    """
def eye(size: int, offset: int = 0, device: int = 0, dtype=None, requires_grad: bool = False):
    """    Create a ``size x size`` tensor with ones on the diagonal and zeros
    elsewhere.

    :param size: size of the (square) tensor to create
    :param offset: Index of the diagonal: 0 (the default) refers to the main diagonal,
    a positive value refers to an upper diagonal, and a negative value to a lower diagonal.
    :param device: device to use,default = 0,use cpu device.
    :param dtype: data type, default: None, use default data type.
\t:param requires_grad: if need to calculate grad in backward(),default = False
    :return:  A QTensor

    Examples::

        size = 3
        from pyvqnet import tensor
        t = tensor.eye(size)
    """
def diagonal(t, offset: int = 0, dim1: int = 0, dim2: int = 1):
    """
    Returns a partial view of :attr:`t` with the its diagonal elements with respect to :attr:`dim1` and :attr:`dim2` appended as a dimension at the end of the shape.
    :attr:`offset` is the offset of the main diagonal.

    :param t: input tensor
    :param offset: offset (0 for the main diagonal, positive for the nth
        diagonal above the main one, negative for the nth diagonal below the
        main one)
    :param dim1: first dimension with respect to which to take diagonal. Default: 0.
    :param dim2: second dimension with respect to which to take diagonal. Default: 1.

    Example::

        from pyvqnet.tensor import randn,diagonal

        x = randn((2, 5, 4, 2))
        diagonal_elements = diagonal(x, offset=-1, dim1=1, dim2=2)
        print(diagonal_elements)
        # [[[-0.4641751,-0.1410288,-0.1215512, 0.5423283],
        #   [ 0.9556418, 0.0376572, 1.2571657, 0.8268463]],

        #  [[-0.7972266, 0.2080281,-0.1157126,-0.7342224],
        #   [ 1.1039937, 0.4700735, 1.0219841,-0.146358 ]]]

    """
def diag(t, k: int = 0):
    """
    If input is 2-D QTensor,returns a new tensor which is the same as this one, except that
    elements other than those in the selected diagonal are set to zero.

    If t is a 1-D QTensor, return a 2-D QTensor with v on the k-th diagonal.

    :param t: input tensor
    :param k: offset (0 for the main diagonal, positive for the nth
        diagonal above the main one, negative for the nth diagonal below the
        main one)

    :return: A QTensor

    Examples::

        a = np.arange(16).reshape(4, 4).astype(np.float32)
        t = QTensor(a)
        for k in range(-3, 4):
            u = tensor.diag(t,k=k)
            print(u)
    """
def randu(shape: _size_type, min: float | int = 0.0, max: float | int = 1.0, device=..., dtype=None, requires_grad: bool = False):
    """    Create a tensor with uniformly distributed random values.

    :param shape: shape of the tensor to create
    :param min: minimum of uniform distribution,default:0.
    :param max: maximum of uniform distribution,default:1.
    :param device: device to use,default = 0
    :param dtype: data type, default: None ,use default data type.
\t:param requires_grad: if need to calculate grad in backward(),default = False

    :return:  A QTensor

    Examples::

        shape = [2, 3]
        t = tensor.randu(shape)

    """
def randn_like(x, mean: float | int = 0.0, std: float | int = 1.0): ...
def randn(shape: _size_type, mean: float | int = 0.0, std: float | int = 1.0, device: int = 0, dtype=None, requires_grad: bool = False):
    """    Create a tensor with normally distributed random values.

    :param shape: shape of the tensor to create
    :param mean: mean of normal distribution,default:0.
    :param std: std of normal distribution,default:1.
    :param device: device to use,default = 0
    :param dtype: data type, default: None ,use default data type.
\t:param requires_grad: if need to calculate grad in backward(),default = False
    :return: A QTensor

    Examples::

        shape = [2, 3]
        t = tensor.randn(shape)

    """
def floor(t):
    """    Compute the element-wise floor (largest integer i such that i <= t)
    of the tensor.

    :param t: input QTensor
    :return: A QTensor

    Examples::

        t = tensor.arange(-2.0, 2.0, 0.25)
        u = tensor.floor(t)
    """
def ceil(t):
    """    Compute the element-wise ceiling (smallest integer i such that i >= x)
    of the tensor.

    :param t: input QTensor
    :return: A QTensor

    Examples::

        t = tensor.arange(-2.0, 2.0, 0.25)
        u = tensor.ceil(t)
    """
def sort(t, axis: int, descending: bool = False, stable: bool = True):
    """
    Sort tensor along the axis

    :param t: input tensor
    :param axis: sort axis
    :param descending: sort order if desc,default= False
    :param stable:  Whether to use stable sorting or not,default = True
    :return: A QTensor

    Examples::

        a = np.random.randint(10, size=24).reshape(3,8).astype(np.float32)
        A = QTensor(a)
        AA = tensor.sort(A,1,False)
    """
def argsort(t, axis: int, descending: bool = False, stable: bool = True):
    """
    Returns an array of indices of the same shape as input that index data
    along the given axis in sorted order.

    :param t: input tensor
    :param axis: sort axis
    :param descending: sort order if desc
    :param stable:  Whether to use stable sorting or not
    :return:  A QTensor

    Examples::

        a = np.random.randint(10, size=24).reshape(3,8).astype(np.float32)
        A = QTensor(a)
        bb = tensor.argsort(A,1,False)
    """
def is_nonzero(t):
    """
    Checks if a QTensor contains any non-zero elements.

    This function delegates the operation to the `is_nonzero` function of the current global backend.
    This allows the `is_nonzero` operation to have different implementations depending on the
    specific backend being used (e.g., NumPy, PyTorch, TensorFlow).

    :param t: The QTensor to check
    :type t
    :return: True if the QTensor contains any non-zero elements, False otherwise.
             The return type may depend on the backend implementation, but is typically a Python bool
             or a tensor containing a single boolean value.
    :rtype: bool or boolean-like type (backend-dependent)

    :Example:

    .. code-block:: python

        import pyvqnet.tensor as tensor

        a = tensor.zeros([2, 2])
        print(tensor.is_nonzero(a))  # Output: False

        b = tensor.tensor([0, 0, 1, 0])
        print(tensor.is_nonzero(b))  # Output: True

        c = tensor.randn([3, 3]) # Random tensor, likely to contain non-zero elements
        print(tensor.is_nonzero(c)) # Output: likely True
    """
def nonzero(t):
    """    Returns a tensor containing the indices of nonzero elements.

    :param t: input tensor
    :return: A new QTensor

    Examples::

        start = -5.0
        stop = 5.0
        num = 1
        t = tensor.arange(start, stop, num)
        t = tensor.nonzero(t)

    """
def isfinite(t):
    """    Test element-wise for finiteness (not infinity or not Not a Number).

    :param t: input QTensor
    :return with each elements presents 1, if the tensor value is isfinite. else 0.

    Examples::

        t = QTensor([1, float('inf'), 2, float('-inf'), float('nan')])
        flag = tensor.isfinite(t)
    """
def isinf(t):
    """    Test element-wise for positive or negative infinity.

    :param t: input QTensor
    :return with each elements presents 1, if the tensor value is isinf. else 0.

    Examples::

        t = QTensor([1, float('inf'), 2, float('-inf'), float('nan')])
        flag = tensor.isinf(t)
    """
def isnan(t):
    """    Test element-wise for Nan.

    :param t: input QTensor
    :return with each elements presents 1, if the tensor value is isnan. else 0.

    Examples::

        t = QTensor([1, float('inf'), 2, float('-inf'), float('nan')])
        flag = tensor.isnan(t)
    """
def isneginf(t):
    """    Test element-wise for negative infinity.

    :param t: a QTensor
    :return with each elements presents 1, if the tensor value is isneginf. else 0.

    Examples::

        t = QTensor([1, float('inf'), 2, float('-inf'), float('nan')])
        flag = tensor.isneginf(t)
    """
def isposinf(t):
    """    Test element-wise for positive infinity.

    :param t: a QTensor
    :return with each elements presents 1, if the tensor value is isposinf. else 0.

    Examples::

        t = QTensor([1, float('inf'), 2, float('-inf'), float('nan')])
        flag = tensor.isposinf(t)
    """
def bitwise_and(t1, t2):
    """
    Compute the bit-wise And of two QTensor element-wise.

    :param t1: input QTensor t1.Only integer or bool is valid input.
    :param t2: input QTensor t2.Only integer or bool is valid input.

    Example::

        from pyvqnet.tensor import *
        import numpy as np
        from pyvqnet.dtype import *
        powers_of_two = 1 << np.arange(14, dtype=np.int64)[::-1]
        samples = tensor.QTensor([23],dtype=kint8)
        samples = samples.unsqueeze(-1)
        states_sampled_base_ten = samples & tensor.QTensor(powers_of_two,dtype = samples.dtype, device = samples.device)
        print(states_sampled_base_ten)
        #[[ 0, 0, 0, 0, 0, 0, 0, 0, 0,16, 0, 4, 2, 1]]
    """
def logical_and(t1, t2):
    """    Compute the truth value of ``t1 and t2`` element-wise.
    if element is 0, it presents False,else True.

    :param t1: a QTensor
    :param t2: a QTensor
    :return:  A QTensor

    Examples::

        a = QTensor([0, 1, 10, 0])
        b = QTensor([4, 0, 1, 0])
        flag = tensor.logical_and(a,b)
    """
def logical_or(t1, t2):
    """    Compute the truth value of ``t1 or t2`` element-wise.
    if element is 0, it presents False,else True.

    :param t1: a QTensor
    :param t2: a QTensor
    :return:  A QTensor

    Examples::

        a = QTensor([0, 1, 10, 0])
        b = QTensor([4, 0, 1, 0])
        flag = tensor.logical_or(a,b)
    """
def logical_not(t):
    """    Compute the truth value of ``not t`` element-wise.if element is 0, it presents False,else True.

    :param t: a QTensor
    :return:  A QTensor

    Examples::

        a = QTensor([0, 1, 10, 0])
        flag = tensor.logical_not(a)
    """
def logical_xor(t1, t2):
    """    Compute the truth value of ``t1 xor t2`` element-wise.
    if element is 0, it presents False,else True.

    :param t1: a QTensor
    :param t2: a QTensor
    :return:  A QTensor

    Examples::

        a = QTensor([0, 1, 10, 0])
        b = QTensor([4, 0, 1, 0])
        flag = tensor.logical_xor(a,b)
    """
def greater(t1, t2):
    """    Return the truth value of ``t1 > t2`` element-wise.
    :param t1: a QTensor
    :param t2: a QTensor
    :return: A boolean tensor that is True where t1 > t2 and False elsewhere

    Examples::

        a = QTensor([[1, 2], [3, 4]])
        b = QTensor([[1, 1], [4, 4]])
        flag = tensor.greater(a,b)
    """
def greater_equal(t1, t2):
    """    Return the truth value of ``t1 >= t2`` element-wise.

    :param t1: a QTensor
    :param t2: a QTensor
    :return: A boolean tensor that is True where t1 >= t2 and False elsewhere

    Examples::

        a = QTensor([[1, 2], [3, 4]])
        b = QTensor([[1, 1], [4, 4]])
        flag = tensor.greater_equal(a,b)
    """
def less(t1, t2):
    """    Return the truth value of ``t1 < t2`` element-wise.

    :param t1: a QTensor
    :param t2: a QTensor
    :return: A boolean tensor that is True where t1 < t2 and False elsewhere

    Examples::

        a = QTensor([[1, 2], [3, 4]])
        b = QTensor([[1, 1], [4, 4]])
        flag = tensor.less(a,b)
    """
def less_equal(t1, t2):
    """    Return the truth value of ``t1 <= t2`` element-wise.

    :param t1: a QTensor
    :param t2: a QTensor
    :return: A boolean tensor that is True where t1 is less than or equal to t2 and False elsewhere

    Examples::

        a = QTensor([[1, 2], [3, 4]])
        b = QTensor([[1, 1], [4, 4]])
        flag = tensor.less_equal(a,b)
    """
def equal(t1, t2):
    """    Return the truth value of ``t1 == t2`` element-wise.

    :param t1: a QTensor
    :param t2: a QTensor
    :return: True if two tensors have the same size and elements, False otherwise.

    Examples::

        a = QTensor([[1, 2], [3, 4]])
        b = QTensor([[1, 1], [4, 4]])
        flag = tensor.equal(a,b)
    """
def not_equal(t1, t2):
    """    Return the truth value of `` t1 != t2`` element-wise.

    :param t1: a QTensor
    :param t2: a QTensor
    :return: A boolean tensor that is True where t1 is not equal to t2 and False elsewhere

    Examples::

        from pyvqnet import tensor, QTensor
        a = QTensor([[1, 2], [3, 4]])
        b = QTensor([[1, 1], [4, 4]])
        flag = tensor.not_equal(a,b)
    """
def broadcast(t1, t2):
    """
    Subject to certain constraints, the smaller array is “broadcast” across the
    larger array so that they have compatible shapes.

    https://numpy.org/doc/stable/user/basics.broadcasting.html

    :param t1: input QTensor 1
    :param t2: input QTensor 2
    :return t1 :  t1 with new broadcasted shape.
    :return t2 :  t2 with new broadcasted shape.

    Example::

        from pyvqnet.tensor import *
        t1 = ones([5,4])
        t2 = ones([4])

        t11, t22 = tensor.broadcast(t1, t2)

        print(t11.shape)
        print(t22.shape)


        t1 = ones([5,4])
        t2 = ones([1])

        t11, t22 = tensor.broadcast(t1, t2)

        print(t11.shape)
        print(t22.shape)


        t1 = ones([5,4])
        t2 = ones([2,1,4])

        t11, t22 = tensor.broadcast(t1, t2)

        print(t11.shape)
        print(t22.shape)


        # [5, 4]
        # [5, 4]
        # [5, 4]
        # [5, 4]
        # [2, 5, 4]
        # [2, 5, 4]

    """
def accumulate(tensor_list: list[QTensor]): ...
def add_scalar(t1, val: _scalar_type): ...
def add(t1, t2):
    """
    Element-wise Adds two tensors .

    :param t1: 'QTensor' - first tensor
    :param t2: 'QTensor' - second tensor
    :return:  A QTensor

    Example::

        from pyvqnet.tensor import QTensor, add
        t1 = QTensor([1, 2, 3])
        t2 = QTensor([4, 5, 6])
        x = add(t1, t2)
    """
def rsub_scalar(tensor, scalar: _scalar_type):
    """
    Perform scalar - tensor.
    """
def sub(t1, t2):
    """
    Element-wise subtracts two tensors.

    :param t1: 'QTensor' - first tensor
    :param t2: 'QTensor' - second tensor
    :return:  A QTensor

    Example::

        from pyvqnet.tensor import QTensor, sub
        t1 = QTensor([1, 2, 3])
        t2 = QTensor([4, 5, 6])
        x = sub(t1, t2)
    """
def mul(t1, t2):
    """
    Element-wise multiplies two tensors.

    :param t1: 'QTensor' - first tensor
    :param t2: 'QTensor' - second tensor
    :return:  A QTensor

    Example::

        from pyvqnet.tensor import QTensor, mul
        t1 = QTensor([1, 2, 3])
        t2 = QTensor([4, 5, 6])
        x = mul(t1, t2)
    """
def mul_scalar(t1, val: _scalar_type): ...
def rdivide(t1, t2):
    """t2/t1"""
def divide(t1, t2):
    """
    Element-wise divides two tensors.

    :param t1: 'QTensor' - first tensor
    :param t2: 'QTensor' - second tensor
    :return:  A QTensor

    Example::

        from pyvqnet.tensor import QTensor, divide

        t1 = QTensor([1, 2, 3])
        t2 = QTensor([4, 5, 6])
        x = divide(t1, t2)

    """
div = divide

def sums(t, axis: _axis_type = None, keepdims: bool = False):
    """
    Sums all the elements in tensor along given axis

    :param t: 'QTensor' - input tensor
    :param axis: 'int' or list - defaults to None
    :param keepdims: 'bool' - defaults to False
    :return:  A QTensor

    Example::

        t = QTensor(([1, 2, 3], [4, 5, 6]))
        x = tensor.sums(t)
    """
sum = sums

def adjoint(t):
    """
    return the new tensor as the tranposed conjugate of input t.
    dimension of input should >=1. if ndim == 1, conjugate of t will be returned, tranpose last two dimension otherwise.

    :param t: input QTensor.
    :return: tranposed conjugate

    Example::

        from pyvqnet.tensor import QTensor, adjoint
        from pyvqnet import kcomplex128

        x1 = QTensor([[0. + 0.j, 1. + 1.j], [2. + 2.j, 3. - 3.j]], dtype=kcomplex128)
        Z1 = adjoint(x1)

    """
def conj(t):
    """
    Return the new tensor as the conjugate of input t.

    :param t: input QTensor.
    :return: conjugate
    """
conjugate = conj

def copy_to_device(self, device):
    """
    create new copy in new device
    """
def move_to_device(self, device):
    """
    Inplace move data to device
    """
def view_as_real(t):
    """
    Returns a view of :attr:`input` as a real tensor. For an input complex tensor of
    :attr:`size` :math:`m1, m2, \\dots, mi`, this function returns a new
    real tensor of size :math:`m1, m2, \\dots, mi, 2`, where the last dimension of size 2
    represents the real and imaginary components of complex numbers.

    .. warning::
        :func:`view_as_real` is only supported for tensors with ``complex dtypes``.

    :param t: input complex QTensor.
    :return: output QTensor


    """
def view_as_complex(t):
    """
    Returns a view of :attr:`input` as a complex tensor. For an input complex
    tensor of :attr:`size` :math:`m1, m2, \\dots, mi, 2`, this function returns a
    new complex tensor of :attr:`size` :math:`m1, m2, \\dots, mi` where the last
    dimension of the input tensor is expected to represent the real and imaginary
    components of complex numbers.

    .. warning::
        :func:`view_as_complex` is only supported for tensors with
        :class:`torch.dtype` ``torch.float64`` and ``torch.float32``.  The input is
        expected to have the last dimension of :attr:`size` 2. In addition, the
        tensor must have a `stride` of 1 for its last dimension. The strides of all
        other dimensions must be even numbers.
    """
def real(t):
    """
    Get real part of input.

    :param t: 'QTensor' - input tensor
    :return: real part of t.

    """
def imag(t):
    """
    get imaginary part of input

    :param t: 'QTensor' - input tensor
    :return: imaginary part of t.

    """
def eigvalsh(t):
    """
    eig value
    """
def eigh(t):
    """
    Return the eigenvalues and eigenvectors of a complex Hermitian (conjugate symmetric) or a real symmetric matrix.
    Returns two objects, a 1-D array containing the eigenvalues of a, 
    and a 2-D square array or matrix (depending on the input type) of the corresponding eigenvectors (in columns).
    
    :param t: input QTensor.

    :return: eigenvalues and eigenvectors of t.

    Examples::

        import numpy as np
        import pyvqnet
        from pyvqnet import tensor


        def generate_random_symmetric_matrix(n):
                A = pyvqnet.tensor.randn((n, n))
                A = A + A.transpose()
                return A

        n = 3
        symmetric_matrix = generate_random_symmetric_matrix(n)

        evs,vecs = pyvqnet.tensor.eigh(symmetric_matrix)
        print(evs)
        print(vecs)
        # [-4.0669565,-1.9191254,-1.3642329]
        # <QTensor [3] DEV_CPU kfloat32>

        # [[-0.9889652, 0.0325959,-0.1445187],
        #  [ 0.0912495, 0.9025176,-0.4208745],
        #  [ 0.1167119,-0.4294176,-0.8955328]]
        # <QTensor [3, 3] DEV_CPU kfloat32>
    """
def frobenius_norm(t, axis: int = None, keepdims: bool = False):
    """
    Sums all the elements in tensor along given axis

    :param t: 'QTensor' - input tensor
    :param axis: 'int' - defaults to None
    :param keepdims: 'bool' - defaults to False
    :return:  A QTensor

    Example::

        from pyvqnet.tensor import *
        t = QTensor([[[ 1.,  2.,  3.],
         [ 4.,  5.,  6.]],

        [[ 7.,  8.,  9.],
         [10., 11., 12.]],

        [[13., 14., 15.],
         [16., 17., 18.]]])
        result = tensor.frobenius_norm(t,0,True)
        
    """
l2_norm = frobenius_norm

def outer(t1, t2):
    """
    Outer product of :attr:`t1` and :attr:`t2`.

    :param t1: 1-D input vector
    :param t2: 1-D input vector
    :return:
        return outer product.

    Example::

        from pyvqnet.tensor import *
        v1 = tensor.arange(1., 5.)
        v2 = tensor.arange(1., 13.)
        z = tensor.outer(v1, v2)
    """
def kron(t1, t2):
    """

    Computes the Kronecker product, denoted by :math:`\\otimes`, of :attr:`input` and :attr:`other`.

    If :attr:`input` is a :math:`(a_0 \times a_1 \times \\dots \times a_n)` tensor and :attr:`other` is a
    :math:`(b_0 \times b_1 \times \\dots \times b_n)` tensor, the result will be a
    :math:`(a_0*b_0 \times a_1*b_1 \times \\dots \times a_n*b_n)` tensor with the following entries:

    .. math::
        (\text{input} \\otimes \text{other})_{k_0, k_1, \\dots, k_n} =
            \text{input}_{i_0, i_1, \\dots, i_n} * \text{other}_{j_0, j_1, \\dots, j_n},

    where :math:`k_t = i_t * b_t + j_t` for :math:`0 \\leq t \\leq n`.
    If one tensor has fewer dimensions than the other it is unsqueezed until it has the same number of dimensions.

    Supports real-valued and complex-valued inputs.

    Example::
        from pyvqnet.tensor import *
        a = tensor.arange(1,1+ 24).reshape([2,1,2,3,2])
        b = tensor.arange(1,1+ 24).reshape([6,4])
        c = tensor.kron(a,b)

    """
def default_matmul2d(t1, t2): ...
def matmul(t1, t2):
    """
    Matrix multiplications of 2d matrixs or batch matrix multiplications of 3d,4d matrix.

    :param t1: 'QTensor' - first tensor
    :param t2: 'QTensor' - second tensor
    :return:  A QTensor

    Example::

        t1 = tensor.ones([2,3])
        t1.requires_grad = True
        t2 = tensor.ones([3,4])
        t2.requires_grad = True
        t3  = tensor.matmul(t1,t2)
        t3.backward(tensor.ones_like(t3))
        print(t1.grad)
        print(t2.grad)

    """
def mv(t1, t2): ...
def bmm(t1, t2): ...
def reciprocal(t):
    """    Compute the element-wise reciprocal of the tensor.

    :param t: input tensor
    :return: A QTensor

    Examples::

        t = tensor.arange(1, 10, 1)
        u = tensor.reciprocal(t)
    """
def round(t):
    """    Round tensor values to the nearest integer.
    
    This function implements the “round half to even” to break ties when a number is equidistant from two integers (e.g. round(2.5) is 2).

    :param t: input tensor
    :return: A QTensor

    Examples::

        t = tensor.arange(-2.0, 2.0, 0.4)
        u = tensor.round(t)
    """
def sign(t):
    """    Compute the element-wise sign (-1 if x < 0, 0 if x == 0, 1 if x > 0)
    of the tensor.

    For complex input,the sign() return values follow the definition of:

    .. math::
        \text{out}_{i} = \x08egin{cases}
                        0 & |\text{{input}}_i| == 0 \\\n                        \x0crac{{\text{{input}}_i}}{|{\text{{input}}_i}|} & \text{otherwise}
                        \\end{cases}

    :param t: input tensor
    :return: A QTensor

    Examples::

        t = tensor.arange(-5, 5, 1)
        u = tensor.sign(t)
    """
def neg(t):
    """
    Unary negation of tensor elements.

    :param t: 'QTensor' - input tensor
    :return:  A QTensor

    Example::

        t = QTensor([1, 2, 3])
        x = tensor.neg(t)

    """
def triu(t, diagonal: int = 0):
    """
    Returns the upper triangular part of a matrix (2-D tensor) or batch of matrices input,
    the other elements of the result tensor out are set to 0.
    The upper triangular part of the matrix is defined as the elements on and above the diagonal.
    The argument diagonal controls which diagonal to consider. If diagonal = 0, all elements on and
    above the main diagonal are retained. A positive value excludes
    just as many diagonals above the main diagonal,
    and similarly a negative value includes just as many diagonals below the main diagonal.

    :param t: 'QTensor' - input QTensor
    :param diagonal: offset (0 for the main diagonal, positive for the nth
        diagonal above the main one, negative for the nth diagonal below the
        main one), default =0.
    :return: output QTensor

    Examples::

        a = tensor.arange(1.0,2*6*5+1.0).reshape([2,6,5])
        u = tensor.triu(a,1)

    """
def tril(t, diagonal: int = 0):
    """
    Returns the lower triangular part of the matrix (2-D tensor) or batch of matrices input,
    the other elements of the result tensor out are set to 0.
    The lower triangular part of the matrix is defined as the elements on and below the diagonal.
    The argument diagonal controls which diagonal to consider. If diagonal = 0, all elements on and
    below the main diagonal are retained. A positive value includes
    just as many diagonals above the main diagonal,
    and similarly a negative value excludes just as many diagonals below the main diagonal.

    :param t: 'QTensor' - input QTensor
    :param diagonal: offset (0 for the main diagonal, positive for the nth
        diagonal above the main one, negative for the nth diagonal below the
        main one), default =0.
    :return: output QTensor

    Examples::

        a = tensor.arange(1.0,2*6*5+1.0).reshape([2,6,5])
        u = tensor.tril(a,-1)

    """
def trace(t, k: int = 0):
    """    Sum diagonal elements.

    :param t: 'QTensor' - input tensor
    :param k: offset (0 for the main diagonal, positive for the nth
        diagonal above the main one, negative for the nth diagonal below the
        main one)
    :return: float

    Examples::

        t = tensor.randn([4,4])
        for k in range(-3, 4):
            u=tensor.trace(t,k=k)
    """
def exp(t):
    """
    Applies exp function to all the elements of the input tensor.

    :param t: 'QTensor' - input tensor
    :return:  A QTensor

    Example::

        t = QTensor([1, 2, 3])
        x = tensor.exp(t)
    """
def acos(t):
    """    Compute the element-wise inverse cosine of the tensor. in-place opration
    Modifies the tensor.

    :param t: input tensor
    :return: None

    Example::

        a = np.arange(36).reshape(2,6,3).astype(np.float32)
        a =a/100
        A = QTensor(a,requires_grad = True)
        y = tensor.acos(A)
    """
def asin(t):
    """    Compute the element-wise inverse sine of the tensor.
    Returns a new tensor.

    :param t: input tensor
    :return: A QTensor

    Examples::

        t = tensor.arange(-1, 1, .5)
        u = tensor.asin(t)
    """
def atan(t):
    """    Compute the element-wise inverse tangent of the tensor.
    Returns a new tensor.

    :return: A QTensor

    Examples::

        t = tensor.arange(-1, 1, .5)
        u = Tensor.atan(t)

    """
def relu(x):
    """
    Rectified Linear Unit activation function.

    .. math::

        \\text{ReLU}(x) = \\max(0, x)

    :param x: input tensor
    :type x
    :return: output tensor after relu activation
    :rtype

    :Example:

    .. code-block:: python

        import pyvqnet.tensor as tensor
        a = tensor.randn([2,2])
        b = tensor.relu(a)

    """
def tanh(t):
    """
    Applies tanh function to all the elements of the input tensor.

    :param t: 'QTensor' - input tensor
    :return:  A QTensor

    Example::

        t = QTensor([1, 2, 3])
        x = tensor.tanh(t)

    """
def sinh(t):
    """
    Applies sinh function to all the elements of the input tensor.

    :param t: 'QTensor' - input tensor
    :return:  A QTensor

    Example::

        t = QTensor([1, 2, 3])
        x = tensor.sinh(t)

    """
def cosh(t):
    """
    Applies cosh function to all the elements of the input tensor.

    :param t: 'QTensor' - input tensor
    :return:  A QTensor
    
    Example::

        t = QTensor([1, 2, 3])
        x = tensor.cosh(t)

    """
def clip(t, min_val: int | float | None = None, max_val: int | float | None = None):
    """
    Clips input tensor to minimum and maximum value.

    :param t: 'QTensor' - input tensor
    :param min_val: 'float' - minimum value, if min_val is None, lower bound is minimum float, default:None. 
    :param max_val: 'float' - maximum value, if max_val is None, upper bound is maximum float, default:None. 
    :return:  A QTensor

    Example::

        t = QTensor([2, 4, 6])
        x = tensor.clip(t, 3, 8)

    """
clamp = clip

def power(t1, t2):
    """
    Raises first tensor to the power of second tensor.

    :param t1: 'QTensor' - first tensor
    :param t2: 'QTensor' - second tensor
    :return:  A QTensor

    Example::

        t1 = QTensor([1, 4, 3])
        t2 = QTensor([2, 5, 6])
        x = tensor.power(t1, t2)

    """
pow = power

def abs(t):
    """
    Applies abs function to all the elements of the input tensor.

    :param t: 'QTensor' - input tensor
    :return:  A QTensor

    Example::

        t = QTensor([1, -2, 3])
        x = tensor.abs(t)

    """
def log(t):
    """
    Applies log (ln) function to all the elements of the input tensor.

    :param t: 'QTensor' - input tensor
    :return:  A QTensor

    Example::

        t = QTensor([1, 2, 3])
        x = tensor.log(t)

    """
def sqrt(t):
    """
    Applies square root function to all the elements of the input tensor.

    :param t: 'QTensor' - input tensor
    :return:  A QTensor

    Example::
        
        from pyvqnet import tensor,QTensor
        t = QTensor([1, 2, 3])
        x = tensor.sqrt(t)
    """
def rsqrt(t):
    """
    Applies reciprocal square root function to all the elements of the input tensor.

    :param t: 'QTensor' - input tensor
    :return:  A QTensor

    Example::
        
        from pyvqnet import tensor,QTensor
        t = QTensor([1, 2, 3])
        x = tensor.rsqrt(t)
    """
def square(t):
    """
    Applies square function to all the elements of the input tensor.

    :param t: 'QTensor' - input tensor
    :return:  A QTensor

    Example::

        t = QTensor([1, 2, 3])
        x = tensor.square(t)
    """
def sin(t):
    """
    Applies sin function to all the elements of the input tensor.

    :param t: 'QTensor' - input tensor
    :return:  A QTensor

    Example::

        from vqnet.tensor import tensor
        from vqnet.tensor.tensor import QTensor
        t = QTensor([1, 2, 3])
        x = tensor.sin(t)

    """
def cos(t):
    """
    Applies cos function to all the elements of the input tensor.

    :param t: 'QTensor' - input tensor
    :return:  A QTensor

    Example::

        t = QTensor([1, 2, 3])
        x = tensor.cos(t)
    """
def atan2(y, x):
    """
    Element-wise arctangent of input/other with consideration of the quadrant. 
    
    :param y: the first input tensor
    :param x: the second input tensor

    :return:  A QTensor
    """
def silu(input):
    """
    Applies the Sigmoid Linear Unit (SiLU) function, element-wise.
        The SiLU function is also known as the swish function.

        .. math::
            \text{silu}(x) = x * \\sigma(x), \text{where } \\sigma(x) \text{ is the logistic sigmoid.}
    
    :param input: input qtensor.
    :return:  A QTensor

    """
def sigmoid(input):
    """Applies the element-wise function:

        .. math::
            \\text{Sigmoid}(x) = \\sigma(x) = \\frac{1}{1 + \\exp(-x)}
    
        :param input: input QTensor

        :return:
            result.

        Example::

            from pyvqnet import tensor
            x = tensor.arange(2,25)

            y = tensor.sigmoid(x)
            print(y)
            # [0.880797 ,0.9525741,0.9820138,0.9933072,0.9975274,0.999089 ,0.9996647,
            #  0.9998766,0.9999546,0.9999833,0.9999938,0.9999977,0.9999992,0.9999996,
            #  0.9999999,1.       ,1.       ,1.       ,1.       ,1.       ,1.       ,
            #  1.       ,1.       ]
    """
def binomial(total_counts: int | QTensor, probs):
    """
    Creates a Binomial distribution parameterized by :attr:`total_count` and
        either :attr:`probs`.

    :param total_counts: number of Bernoulli trials.
    :param probs: Event probabilities.

    :return:
        QTensor of Binomial distribution.

    Example::

        import pyvqnet.tensor as tensor

        a = tensor.randu([3,4])
        b = 1000

        c = tensor.binomial(b,a)
        print(c)

        # [[221.,763., 30.,339.],
        #  [803.,899.,105.,356.],
        #  [550.,688.,828.,493.]]

    """
def tan(t):
    """
    Applies tan function to all the elements of the input tensor.

    :param t: 'QTensor' - input tensor
    :return:  A QTensor

    Example::

        t = QTensor([1, 2, 3])
        x = tensor.tan(t)
    """
def mean(t, axis: _axis_type = None, keepdims: bool = False):
    """
    Obtain the mean of QTensor along a specific axis or get mean value of all elements.

    :param t:  the input tensor.
    :param dim:  the dimension to reduce,default None: get mean value of all elements.
    :param keepdims:  whether the output tensor has dim retained or not,default False.
    :return: returns the mean value of the input tensor.

    Example::

        t = QTensor([[1, 2, 3], [4, 5, 6]])
        x = tensor.mean(t, axis=1)

    """
def median(t, axis: _axis_type = None, keepdims: bool = False):
    """    Obtain the median value of QTensor along a specific axis or get median value of all elements.

    :param t: the input tensor.
    :param axis: the dimension to reduce,default None: get median value of all elements.default:None.
    :param keepdims: whether the output tensor has dim retained or not,default False.

    :return: Returns the median of the values in input.

    Examples::

        a = QTensor([[1.5219, -1.5212,  0.2202]])
        median_a = tensor.median(a)
        print(median_a)

        b = QTensor([[0.2505, -0.3982, -0.9948,  0.3518, -1.3131],
                    [0.3180, -0.6993,  1.0436,  0.0438,  0.2270],
                    [-0.2751,  0.7303,  0.2192,  0.3321,  0.2488],
                    [1.0778, -1.9510,  0.7048,  0.4742, -0.7125]])
        median_b = tensor.median(b,1, False)
        print(median_b)

    """
def std(t, axis: list[int] | tuple[int, ...] | int | None = None, keepdims: bool = False, unbiased: bool = True):
    """        Obtain the standard deviation value of QTensor along a specific axis
        or get standard deviation value of all elements.

        :param t: the input tensor.
        :param axis:  the dimension to reduce, default None: get standard deviation
                      value of all elements.
        :param keepdim: whether the output tensor has dim retained or not,default False.
        :param unbiased: unbiased (bool) – whether to use Bessel’s correction,default True.

        :return: Returns the median of the values in input.

        Examples::

            a = QTensor([[-0.8166, -1.3802, -0.3560]])
            std_a = tensor.std(a)
            print(std_a)

            b = QTensor([[0.2505, -0.3982, -0.9948,  0.3518, -1.3131],
                        [0.3180, -0.6993,  1.0436,  0.0438,  0.2270],
                        [-0.2751,  0.7303,  0.2192,  0.3321,  0.2488],
                        [1.0778, -1.9510,  0.7048,  0.4742, -0.7125]])
            std_b = tensor.std(b, 1, False, False)
            print(std_b)


        """
def var(t, axis: list[int] | tuple[int, ...] | int | None = None, keepdims: bool = False, unbiased: bool = True):
    """        Obtain the variance value of QTensor along a specific
        axis or get variance value of all elements.

        :param t: the input tensor.
        :param axis:  the dimension to reduce, default None: get variance value of all elements.
        :param keepdim: whether the output tensor has dim retained or not,default False.
        :param unbiased: unbiased (bool) – whether to use Bessel’s correction,default True.

        Examples::

            a = QTensor([[-0.8166, -1.3802, -0.3560]])
            a_var = tensor.var(a)
            print(a_var)

        """
def maximum(t1, t2):
    """
    Element-wise maximum of two tensor.

    :param t1: 'QTensor' - first tensor
    :param t2: 'QTensor' - second tensor
    :return:  A QTensor

    Example::

        t1 = QTensor([6, 4, 3])
        t2 = QTensor([2, 5, 7])
        x = tensor.maximum(t1, t2)

    """
def minimum(t1, t2):
    """
    Element-wise minimum of two tensor.

    :param t1: 'QTensor' - first tensor
    :param t2: 'QTensor' - second tensor
    :return:  A QTensor

    Example::

        t1 = QTensor([6, 4, 3])
        t2 = QTensor([2, 5, 7])
        x = tensor.minimum(t1, t2)
    """
def where(condition, t1, t2):
    """
    Return elements chosen from x or y depending on condition.

    :param condition: 'QTensor' - condition tensor
    :param t1: 'QTensor' - tensor from which to take elements if condition is met
    :param t2: 'QTensor' - tensor from which to take elements if condition is not met
    defaults to None
    :return:  A QTensor

    Example::

        t1 = QTensor([1, 2, 3])
        t2 = QTensor([4, 5, 6])
        x = tensor.where(t1 < 2, t1, t2)

    """
def min(t, axis: list[int] | tuple[int, ...] | int | None = None, keepdims: bool = False):
    """
    Returns min elements of the input tensor alongside given axis.
    if axis is None, return the min value of all elements in tensor.

    :param t: 'QTensor' - input tensor
    :param axis: 'int' - defaults to None
    :param keepdims: 'bool' - defaults to False
    :return or float

    Note:
        When the minimum value appears on multiple elements,
        if the min function specifies an axis, its gradient will
        all be passed to the element positions of these minimum values in the input;
        if no axis is specified, the gradient will be passed to the input equally.
        several minimum element positions.

    Example::

        t = QTensor([[1, 2, 3], [4, 5, 6]])
        x = tensor.min(t, axis=1, keepdims=True)
    """
def argmax(t, dim: int | None = None, keepdims: bool = None):
    """        Returns the indices of the maximum value of all elements in the input tensor,or
        returns the indices of the maximum values of a tensor across a dimension.

        :param t: input QTensor.
        :param dim: dim (int) – the dimension to reduce,only accepts single axis.
                    if dim is None, returns the indices of the maximum value of all
                    elements in the input tensor.
                    The valid dim range is [-R, R), where R is input's ndim. when dim < 0,
                    it works the same way as dim + R.

        :param keepdims: keepdim (bool) – whether the output tensor has dim retained or not.

        :return: the indices of the maximum value in the input tensor.
        
        Example::

            from pyvqnet.tensor.tensor import QTensor,argmax
            a = QTensor([[1.3398, 0.2663, -220.2686, 10.2450],
                                    [-0.7401, -0.8805, -80.3402, -1.1936],
                                    [-0.74201, -0.81805, -80.34202, -1.11936],
                                    [-10.74201, -10.81805, -280.34202, -41.11936],
                                    [-30.74201, -770.81805, -2280.34202, -331.11936],
                                    [10.4907, -21.3948, -111.0691, -20.3132],
                                    [-11.6092,40.5419, -30.2993, 0.3195]])
            b = argmax(a,1,False)
    """
def argmin(t, dim: int | None = None, keepdims: bool = None):
    """
        Returns the indices of the minimum value of all elements in the input tensor,or
        returns the indices of the minimum values of a tensor across a dimension.

        :param t: input QTensor.
        :param dim: dim (int) – the dimension to reduce,only accepts single axis.
                    if dim is None, returns the indices of the minimum value of all
                    elements in the input tensor.
                    The valid dim range is [-R, R), where R is input's ndim. when dim < 0,
                    it works the same way as dim + R.

        :param keepdims: keepdim (bool) – whether the output tensor has dim retained or not.

        :return: the indices of the minimum value in the input tensor.
        
        Example::

            from pyvqnet.tensor.tensor import QTensor,argmax
            a = QTensor([[1.3398, 0.2663, -220.2686, 10.2450],
                                    [-0.7401, -0.8805, -80.3402, -1.1936],
                                    [-0.74201, -0.81805, -80.34202, -1.11936],
                                    [-10.74201, -10.81805, -280.34202, -41.11936],
                                    [-30.74201, -770.81805, -2280.34202, -331.11936],
                                    [10.4907, -21.3948, -111.0691, -20.3132],
                                    [-11.6092,40.5419, -30.2993, 0.3195]])
            b = argmin(a,1,False)
    """
def max(t, axis: list[int] | tuple[int, ...] | int | None = None, keepdims: bool = False):
    """
    Returns max elements of the input tensor alongside given axis.

    :param t: 'QTensor' - input tensor
    :param axis: 'int' - defaults to None
    :param keepdims: 'bool' - defaults to False
    :return or float

    Note:

        When the maximum value appears on multiple elements,
        if the max function specifies an axis, its gradient will all be passed to
        the element positions of these maximum values in the input;
        if no axis is specified, the gradient will be passed to the input equally.
        several maxima at the element positions.

    Example::

        t = QTensor([[1, 2, 3], [4, 5, 6]])
        x = tensor.max(t, axis=1, keepdims=True)
    """
def flatten_dense_tensors(tensors):
    """
    Flatten dense tensors into a 1D QTensor.

    :param tensors: list or tuple of several QTensor.
    :return: 1d concat tensor.

    """
def unflatten_dense_tensors(flat, tensors: list[QTensor] | tuple[QTensor, ...]):
    """
    Unflattened dense tensors with sizes same as tensors and values from
        flat.
    :param flat: input flat qtensor.
    :param tensors: list or tuple of several QTensor.

    :return: list of unflattened tensors.
    """
def flatten(t, start: int = 0, end: int = -1):
    """
    Flatten tensor from dim start to dim end.

    :param t: 'QTensor' - input tensor
    :param start: 'int' - dim start
    :param end: 'int' - dim start
    :return:  A QTensor

    Example::

        t = QTensor([1, 2, 3])
        x = tensor.flatten(t)
    """
def swapaxis(t, axis1: int, axis2: int):
    """
    Interchange two axes of an array.

    :param axis1: First axis.
    :param axis2:  Destination position for the original axis. These must also be unique
    :return: A QTensor

    Examples::

        a = np.arange(24).reshape(2,3,4).astype(np.float32)
        A = QTensor(a)
        AA = tensor.swapaxis(A,2,1)

    """
swapaxes = swapaxis

def moveaxis(t, src: _size_type, dst: _size_type):
    """
    Moves the dimension(s) of :attr:`t` at the position(s) in :attr:`source`
    to the position(s) in :attr:`destination`.

    Other dimensions of :attr:`t` that are not explicitly moved remain in
    their original order and appear at the positions not specified in :attr:`destination`.

    :param t: input QTensor.
    :param src (int or tuple of ints): Original positions of the dims to move. These must be unique.
    :param dst (int or tuple of ints): Destination positions for each of the original dims. These must also be unique.
    
    :return:
        new QTensor

    Example::

        from pyvqnet import QTensor,tensor
        a = tensor.arange(0,24).reshape((2,3,4))
        b = tensor.moveaxis(a,(1, 2), (0, 1))
        print(b.shape)
        #[3, 4, 2]
    """
def view(t, shape: _size_type):
    """
    equivalent to QTensor.view
    """
def reshape(t, shape: _size_type):
    """
    Reshapes tensor.

    :param t: 'QTensor' - input tensor
    :param shape: 'tuple' - new shape
    :return:  A QTensor

    Example::

        t = QTensor([[1, 2, 3], [4, 5, 6]])
        x = tensor.reshape(t, shape=(1, 6))
    """
def set_select(t, index: list, set_tensor):
    '''
    Set value with slices of the input according to the string list in index. This interface is deprecated. Please use __setitem__

    :param t: input QTensor
    :param index: a list of string contains slices.
    :param set_tensor: a QTensor contains value need to be set
    :return: None

    Example::

        d = np.arange(1,96+1)
        d = d.reshape([2,3,16])
        g = np.arange(-550,-500).reshape([2,5,5])
        g = QTensor(g)
        g.requires_grad = True
        d1 = QTensor(d)
        d1.requires_grad = True
        yy = 2*d1
        tensor.set_select(d,[":", "-12:14:2"], g)

    '''
def split(input, split_size_or_sections: int | list[int] | tuple[int, ...], dim: int = 0):
    """Splits the tensor into chunks. Each chunk is a view of the original tensor.

    If :attr:`split_size_or_sections` is an integer type, then :attr:`tensor` will
    be split into equally sized chunks (if possible). Last chunk will be smaller if
    the tensor size along the given dimension :attr:`dim` is not divisible by
    :attr:`split_size`.

    If :attr:`split_size_or_sections` is a list, then :attr:`tensor` will be split
    into ``len(split_size_or_sections)`` chunks with sizes in :attr:`dim` according
    to :attr:`split_size_or_sections`.

    :param tensor (Tensor): tensor to split.
    :param split_size_or_sections (int), (list(int)), (tuple(int)): size of a single chunk or
            list of sizes for each chunk
    :param dim (int): dimension along which to split the tensor.

    :return:
        tuple of split tensors.

    Examples::

        from pyvqnet import tensor
        a = tensor.arange(0,2*5*3).reshape([2,5,3])
        b = tensor.split(a,2,-2)
        print(b)
        # (
        # [[[ 0., 1., 2.],
        #   [ 3., 4., 5.]],

        #  [[15.,16.,17.],
        #   [18.,19.,20.]]]
        # <QTensor [2, 2, 3] DEV_CPU kfloat32>, 
        # [[[ 6., 7., 8.],
        #   [ 9.,10.,11.]],

        #  [[21.,22.,23.],
        #   [24.,25.,26.]]]
        # <QTensor [2, 2, 3] DEV_CPU kfloat32>, 
        # [[[12.,13.,14.]],

        #  [[27.,28.,29.]]]
        # <QTensor [2, 1, 3] DEV_CPU kfloat32>)
        b = tensor.split(a,(2,3),-2)
        print(b)
        # (
        # [[[ 0., 1., 2.],
        #   [ 3., 4., 5.]],

        #  [[15.,16.,17.],
        #   [18.,19.,20.]]]
        # <QTensor [2, 2, 3] DEV_CPU kfloat32>, 
        # [[[ 6., 7., 8.],
        #   [ 9.,10.,11.],
        #   [12.,13.,14.]],

        #  [[21.,22.,23.],
        #   [24.,25.,26.],
        #   [27.,28.,29.]]]
        # <QTensor [2, 3, 3] DEV_CPU kfloat32>)
    """
def chunk(input, chunks: int, dim: int = 0):
    """Attempts to split a tensor into the specified number of chunks.

    If the tensor size along the given dimension dim is divisible by chunks, all returned chunks will be the same size. If the tensor size along the given dimension dim is not divisible by chunks, all returned chunks will be the same size, except the last one. If such division is not possible, this function may return fewer than the specified number of chunks.

    :param input: (QTensor) - the tensor to split
    :param chunks (int) - number of chunks to return
    :param dim (int) - dimension along which to split the tensor

    :return:
        Tuple of new tensors.

    Examples::

        from pyvqnet import tensor
        a = tensor.arange(0,2*5*3).reshape([2,5,3])
        b = tensor.chunk(a,2,-2)
        print(b)
        # [[[ 9.,10.,11.],
        #   [12.,13.,14.]],

        #  [[24.,25.,26.],
        #   [27.,28.,29.]]]
    """
def narrow(input, dim: int, start: int, length: int):
    """

    Returns a new tensor that is a narrowed version of input tensor. The dimension dim is input from start to start + length. 
    The returned tensor and input tensor may share the same underlying storage if possible.

    :param input: the tensor to narrow
    :param dim: the dimension along which to narrow
    :param start: index of the element to start the narrowed dimension from.
    :param length : length of the narrowed dimension, must be weakly positive.

    """
slice_in_dim = narrow

def select(t, index: list):
    '''
    Slices the input according to the string list in index. This interface is deprecated. Please use __getitem__

    :param t: input QTensor
    :param index: a list of string contains slices.
    :return

    Example::

        t = QTensor(np.arange(1,25).reshape(2,3,4))
        print(t)
        indx = [":", QTensor([1,2,1,0,1]), "1:3"]
        t.requires_grad = True
        t.zero_grad()
        ts = tensor.select(t,indx)
        ts.backward(tensor.ones(ts.shape))
    '''
def select_1dim(t, dim, index):
    """
    Selects a sub-tensor along a specified dimension at the given index (similar to torch.select())
    
    :param input: Input tensor of at least 1 dimension
    :type input: torch.Tensor
    :param dim: Dimension to select from (0 <= dim < input.dim())
    :type dim: int
    :param index: Index to select along the specified dimension (0 <= index < input.size(dim))
    :type index: int
    
    :return: The selected sub-tensor (with one fewer dimension than input)
    """

class PackedSequence:
    data: Incomplete
    batch_sizes: Incomplete
    sorted_indice: Incomplete
    unsorted_indice: Incomplete
    def __init__(self, data, batch_sizes, sort_indice, unsorted_indice) -> None: ...

def pad_packed_sequence(sequence: PackedSequence, batch_first: bool = False, padding_value: float | int = 0, total_length: None | int = None):
    """Pads a packed batch of variable length sequences.

    It is an inverse operation to :func:`pack_pad_sequence`.

    The returned Tensor's data will be of size ``T x B x *``, where `T` is the length
    of the longest sequence and `B` is the batch size. If ``batch_first`` is True,
    the data will be transposed into ``B x T x *`` format.

    :param sequence:  batch data to pad
    :param batch_first: if ``True``, batch would be the first dim of input.default:False.
    :param padding_value: values for padded elements.default:0.
    :param total_length: if not ``None``, the output will be padded to have length :attr:`total_length`.default:None.
    :return:
        Tuple of Tensor containing the padded sequence, and a list of lengths of each sequence in the batch.
        Batch elements will be re-ordered as they were ordered originally.

    Examples::

        from pyvqnet.tensor import tensor
        a = tensor.ones([4, 2,3])
        b = tensor.ones([2, 2,3])
        c = tensor.ones([1, 2,3])
        a.requires_grad = True
        b.requires_grad = True
        c.requires_grad = True
        y = tensor.pad_sequence([a, b, c], True)
        seq_len = [4, 2, 1]
        data = tensor.pack_pad_sequence(y,
                                seq_len,
                                batch_first=True,
                                enforce_sorted=True)

        seq_unpacked, lens_unpacked = tensor.pad_packed_sequence(data, batch_first=True)
        print(seq_unpacked)
        # [
        # [[1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000]],
        # [[1.0000000, 1.0000000],
        #  [0.0000000, 0.0000000],
        #  [1.0000000, 1.0000000]],
        # [[1.0000000, 1.0000000],
        #  [0.0000000, 0.0000000],
        #  [0.0000000, 0.0000000]],
        # [[1.0000000, 1.0000000],
        #  [0.0000000, 0.0000000],
        #  [0.0000000, 0.0000000]]
        # ]
        print(lens_unpacked)
        # [4 1 2]

    """
def pack_pad_sequence(input, lengths: list[int], batch_first: bool = False, enforce_sorted: bool = True) -> PackedSequence:
    """Packs a Tensor containing padded sequences of variable length.
    `input` should be shape of [batch_size,length,*] if batch_first is True, 
    be [length,batch_size,*] otherwise.
    `*` is any number of dimensions represent feature dimensions.
    For unsorted sequences, use `enforce_sorted = False`. If :attr:`enforce_sorted` is
        ``True``, the sequences should be sorted by length in a decreasing order.

    :param input: padded batch of variable length sequences.
    :param lengths: list of sequence lengths of each batch
        element.
    :param batch_first: if ``True``, the input is expected in ``B x T x *``
        format,default:False.
    :param enforce_sorted: if ``True``, the input is expected to
        contain sequences sorted by length in a decreasing order. If
        ``False``, the input will get sorted unconditionally. Default: ``True``.

    :return: a :class:`PackedSequence` object.

    Examples::

        from pyvqnet.tensor import tensor
        a = tensor.ones([4, 2,3])
        b = tensor.ones([2, 2,3])
        c = tensor.ones([1, 2,3])
        a.requires_grad = True
        b.requires_grad = True
        c.requires_grad = True
        y = tensor.pad_sequence([a, b, c], True)
        seq_len = [4, 2, 1]
        data = tensor.pack_pad_sequence(y,
                                seq_len,
                                batch_first=True,
                                enforce_sorted=True)
        print(data.data)
        print(data.batch_sizes)
        print(data.sorted_indice)
        print(data.unsorted_indice)

        # [
        # [[1.0000000, 1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000, 1.0000000]],
        # [[1.0000000, 1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000, 1.0000000]],
        # [[1.0000000, 1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000, 1.0000000]],
        # [[1.0000000, 1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000, 1.0000000]],
        # [[1.0000000, 1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000, 1.0000000]],
        # [[1.0000000, 1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000, 1.0000000]],
        # [[1.0000000, 1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000, 1.0000000]]
        # ]
        # [3, 2, 1, 1]
        # [0, 2, 1]
        # [0, 2, 1]

    """
def pad_sequence(qtensor_list: list[QTensor], batch_first: bool = False, padding_value: int | float = 0):
    """Pad a list of variable length Tensors with ``padding_value``

    ``pad_sequence`` stacks a list of Tensors along a new dimension,
    and pads them to equal length.the input is list of
    sequences with size ``L x *``. L is variable length.

    :param qtensor_list: list of variable length sequences.
    :param batch_first: output should be in ``bacth_size x the longest sequence legnth x *`` if True, or in
        `` the longest sequence legnth x bacth_size x *`` otherwise. Default: False.
    :param padding_value: padding value. Default: 0.

    :return:
        Tensor of size ``bacth_size x the longest sequence legnth x *`` if :attr:`batch_first` is ``False``.
        Tensor of size `` the longest sequence legnth x bacth_size x *`` otherwise.

    Examples::

        from pyvqnet.tensor import tensor
        a = tensor.ones([4, 2,3])
        b = tensor.ones([1, 2,3])
        c = tensor.ones([2, 2,3])
        a.requires_grad = True
        b.requires_grad = True
        c.requires_grad = True
        y = tensor.pad_sequence([a, b, c], True)

        print(y)
        # [
        # [[[1.0000000, 1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000, 1.0000000]],
        # [[1.0000000, 1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000, 1.0000000]],
        # [[1.0000000, 1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000, 1.0000000]],
        # [[1.0000000, 1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000, 1.0000000]]],
        # [[[1.0000000, 1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000, 1.0000000]],
        # [[0.0000000, 0.0000000, 0.0000000],
        #  [0.0000000, 0.0000000, 0.0000000]],
        # [[0.0000000, 0.0000000, 0.0000000],
        #  [0.0000000, 0.0000000, 0.0000000]],
        # [[0.0000000, 0.0000000, 0.0000000],
        #  [0.0000000, 0.0000000, 0.0000000]]],
        # [[[1.0000000, 1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000, 1.0000000]],
        # [[1.0000000, 1.0000000, 1.0000000],
        #  [1.0000000, 1.0000000, 1.0000000]],
        # [[0.0000000, 0.0000000, 0.0000000],
        #  [0.0000000, 0.0000000, 0.0000000]],
        # [[0.0000000, 0.0000000, 0.0000000],
        #  [0.0000000, 0.0000000, 0.0000000]]]
        # ]

    """
def index_select(t, dim: int, indice):
    """
    Returns a new tensor which indexes the input tensor along dimension ``dim`` 
    using the entries in index.

    The returned tensor has the same number of dimensions as the original tensor (input). 
    The ``dim`` dimension has the same size as the length of index;
    other dimensions have the same size as in the original tensor.

    :param t: input QTensor
    :param dim: the dimension which we index
    :param indice: the 1D QTensor containing index

    :return: A new QTensor

    Examples::

        import pyvqnet
        A = pyvqnet.tensor.arange(1,121).reshape([3,5,8])
        import pyvqnet.tensor as tensor
        A.requires_grad = True
        y = tensor.index_select(A,1,tensor.QTensor([2,1,1,0,3]))
    """
def cat(args, axis: int = 0) -> QTensor:
    """
    alais for concatenate
    """
def concatenate(args, axis: int = 0) -> QTensor:
    """
       concatenate with channels, i.e. concatenate C of Tensor shape (N,C,H,W)

       :param args: tuple consist of Tensor
       :param axis: along which aixs to concat,default = 0
       :return: cat of tuple

    Example::

        x = QTensor([[1, 2, 3],[4,5,6]], requires_grad=True)
        y = 1-x
        x = tensor.concatenate((x,y),1)

    """
def stack(QTensors, axis: int = 0) -> QTensor:
    """    Join a sequence of arrays along a new axis,return a new Tensor.

    :param QTensors: list contains QTensors
    :param axis: stack axis
    :return: A QTensor

    Examples::

        R, C = 3, 4
        a = np.arange(R * C).reshape(R, C).astype(np.float32)
        t11 = QTensor(a)
        t22 = QTensor(a)
        R, C = 3, 4
        a = np.arange(R * C).reshape(R, C).astype(np.float32)
        t33 = QTensor(a)
        rlt1 = tensor.stack([t11,t22,t33],2)
    """
def hstack(arrs): ...
def vstack(arrs): ...
def permute(t, dim: _size_type):
    """    Reverse or permute the axes of an array.if new_dims = None, revsers the dim.

    :param t: input QTensor
    :param new_dims: the new order of the dimensions (list of integers).
    :return: result QTensor.

    Examples::

        R, C = 3, 4
        a = np.arange(R * C).reshape([2,2,3]).astype(np.float32)
        t = QTensor(a)
        tt = tensor.permute(t,[2,0,1])

    """
def transpose(t, dim: _size_type | None | np.ndarray = None):
    """    Reverse or permute the axes of an array.if dim = None, revsers the dim.
    if dim is a list with two elements, transpose() will permute these two dim.

    :param t: input QTensor
    :param dim: the new order of the dimensions (list of integers).If dim is None and t is 2d, will tranpose this two dim.
    :return: result QTensor.

    Examples::

        R, C = 3, 4
        a = np.arange(R * C).reshape([2,2,3]).astype(np.float32)
        t = QTensor(a)
        tt = tensor.transpose(t,[2,0,1])

    """
def tile(t, reps: list[int] | tuple[int, ...]):
    """
    Construct an array by repeating tensors the number of times given by reps.

    If reps has length d, the result will have dimension of max(d, t.ndim).

    If t.ndim < d, t is promoted to be d-dimensional by prepending new axes.
    So a shape (4,) array is promoted to (1, 4) for 2-D replication,
    or shape (1, 1, 4) for 3-D replication.

    If this is not the desired behavior, promote t to d-dimensions manually
    before calling this function.

    If t.ndim > d, reps is promoted to t.ndim by pre-pending 1’s to it.
    Thus for an A of shape (4, 1, 2, 5), a reps of (3, 2) is treated as (1, 1, 3, 2).

    :param t: input QTensor
    :param reps: the number of repetitions per dimension.
    :return: new tensor

    Examples::

        a = np.arange(24).reshape(4,6).astype(np.float32)
        A = QTensor(a)
        reps = [1,2,3,4,5]
        B = tensor.tile(A,reps)
    """
def squeeze(t, axis: list[int] | tuple[int, ...] | int | None = None):
    """
    Remove axes of length one .if `axis` is not specified, remove all single-dimensional axis from the shape of a tensor. 

    :param t: input QTensor
    :param axis: squeeze axis
    :return: A QTensor

    Examples::

        a = np.arange(6).reshape(1,6,1).astype(np.float32)
        A = QTensor(a)
        AA = tensor.squeeze(A,0)

    """
def unsqueeze(t, axis: int = 0):
    """
    Returns a new tensor with a dimension of size one added at the specified position.

    :param t: input QTensor
    :param axis: unsqueeze axis,default:0.
    :return: A QTensor

    Examples::

        a = np.arange(24).reshape(2,1,1,4,3).astype(np.float32)
        A = QTensor(a)
        AA = tensor.unsqueeze(A,1)

    """
def broadcast_to(t, ref: _size_type):
    """
    Subject to certain constraints, the array t is “broadcast” to the
    reference shape, so that they have compatible shapes.

    https://numpy.org/doc/stable/user/basics.broadcasting.html

    :param t: input QTensor
    :param ref: reference shape.
    :return :  new broadcasted QTensor of t.

    Examples::

        from pyvqnet.tensor.tensor import QTensor
        from pyvqnet.tensor import *
        ref = [2,3,4]
        a = ones([4])
        b = tensor.broadcast_to(a,ref)
    """
def masked_fill(t, mask, value: float | int):
    """
    Fills elements of self tensor with value where mask ==1.
    The shape of mask must be broadcastable with the shape of the underlying QTensor.

    :param t: input QTensor
    :param mask: mask QTensor
    :param value: filled value
    :return: A QTensor

    Examples::

        from pyvqnet.tensor import tensor
        import numpy as np
        a = tensor.ones([2,2,2,2])
        mask =np.random.randint(0,2, size=4).reshape([2,2])
        b = tensor.QTensor(mask)
        c = tensor.masked_fill(a,b,13)
    """
def argtopk(t, k: int, axis: int = -1, if_descent: bool = True):
    """
    Returns indices of the largest k elements of each row of
    the input tensor in the given dimension axis.The stable sort is used for this function.

    If if_descent is False then the k smallest elements indices are retruned.

    :param t: input QTensor
    :param k: top K
    :param axis: the dimension to sort along,default = -1 ,last axis
    :param if_descent: get descent topk results or not,default True
    :return: A QTensor

    Examples::

        x = QTensor([24., 13., 15. ,4. , 3. ,8. ,11.  ,3. , 6. ,15.,
        24., 13., 15. ,3. , 3. ,8. ,7.  ,3. , 6. ,11. ])
        x = x.reshape([2,5,1,2])
        x.requires_grad = True
        y = tensor.argtopK(x, 3, 1)
    """
argtopK = argtopk

def topk(t, k: int, axis: int = -1, if_descent: bool = True):
    """
    Returns the k largest elements of the given input tensor along a given dimension.

    If if_descent is False then the k smallest elements are returned.

    :param t: input QTensor
    :param k: top K
    :param axis: the dimension to sort along.default = -1 ,last axis
    :param if_descent: if set to true, algorithm will sort by descending order,
            otherwise sort by ascending order.default is True.
    :return: A QTensor

    Examples::

        x = QTensor([24., 13., 15. ,4. , 3. ,8. ,11.  ,3. , 6. ,15.,24.,
         13., 15. ,3. , 3. ,8. ,7.  ,3. , 6. ,11. ])
        x = x.reshape([2,5,1,2])
        x.requires_grad = True
        y =  tensor.topK(x, 3, 1)
    """
topK = topk

def cumsum(t, axis: int = -1):
    """
    Returns the cumulative sum of elements of input in the dimension axis.

    :param t: 'QTensor' - input QTensor
    :param axis: 'int' - defaults -1, ues last axis
    :return:  A QTensor

    Example::

        t = QTensor(([1, 2, 3], [4, 5, 6]))
        x = tensor.cumsum(t,-1)

    """
def flip(t, flip_dims: _size_type):
    """
    Reverse the order of a n-D tensor along given axis in dims.

    :param t: 'QTensor' - input QTensor
    :param flip_dims: a list or tuple,axis to flip on
    :return:  A QTensor

    Example::

        t = tensor.ones([3,4,5,6])
        y = tensor.flip(t,[0,-1])
        print(y)
    """
def multinomial(t, num_samples: int):
    """
    Returns a tensor where each row contains num_samples indices sampled
    from the multinomial probability distribution located in the corresponding row of tensor input.

    :param t: the input tensor containing probabilities.
    :param num_samples: number of samples to draw

    :return:
         the output index.

    Examples::

        from pyvqnet import tensor
        weights = tensor.QTensor([0,10, 3, 1]) 
        idx = tensor.multinomial(weights,3)
        print(idx)


    """
def scatter(input, dim: int, indices, src):
    """
    Writes all values from the tensor `src` into `input` at the indices specified in the `indices` tensor.

    For a 3-D tensor the output is specified by::

    input[indices[i][j][k]][j][k] = src[i][j][k]  # if dim == 0
    input[i][indices[i][j][k]][k] = src[i][j][k]  # if dim == 1
    input[i][j][indices[i][j][k]] = src[i][j][k]  # if dim == 2

    :param input: input QTensor.
    :param dim: scatter axis.
    :param indices: index QTensor,should have the same dimension size as the input.
    :param src: the source tensor to scatter.

    :return scattered result

    Examples::

        from pyvqnet.tensor import scatter,QTensor,tensor
        import numpy as np

        np.random.seed(25)
        npx = np.random.randn( 3, 2,4,2)
        npindex = np.array([2,3,1,2,1,2,3,0,2,3,1,2,3,2,0,1]).reshape([2,2,4,1]).astype(np.int64)
        npsrc = QTensor(np.full_like(npindex,200))
        npsrc.requires_grad = True
        x1 = QTensor(npx)
        indices1 =  QTensor(npindex)
        y1 = scatter(x1,2,indices1,npsrc)
    """
def gather(t, dim: int, index):
    """
    Gathers values along an axis specified by `dim`.

    For a 3-D tensor the output is specified by::

        out[i][j][k] = t[index[i][j][k]][j][k]  # if dim == 0
        out[i][j][k] = t[i][index[i][j][k]][k]  # if dim == 1
        out[i][j][k] = t[i][j][index[i][j][k]]  # if dim == 2

    :param t: input QTensor.
    :param dim: gather axis.
    :param index: index QTensor,should have the same dimension size as the input.

    :return: gathered result

    Examples::

        from pyvqnet.tensor import gather,QTensor,tensor
        import numpy as np
        np.random.seed(25)
        npx = np.random.randn( 3, 4,6)
        npindex = np.array([2,3,1,2,1,2,3,0,2,3,1,2,3,2,0,1]).reshape([2,2,4]).astype(np.int64)

        x1 = QTensor(npx)
        indices1 =  QTensor(npindex)
        x1.requires_grad = True
        y1 = gather(x1,1,indices1)
        y1.backward(tensor.arange(0,y1.numel()).reshape(y1.shape))

        print(y1)
        # [
        # [[2.1523438, -0.4196777, -2.0527344, -1.2460938],
        #  [-0.6201172, -1.3349609, 2.2949219, -0.5913086]],
        # [[0.2170410, -0.7055664, 1.6074219, -1.9394531],
        #  [0.2430420, -0.6333008, 0.5332031, 0.3881836]]
        # ]

    """
def tensordot(x, y, dim1: _size_type, dim2: _size_type):
    """
    This function computes a contraction, which sum the product of elements from two tensors along the given axes.

    :param x: The left tensor for contraction.
    :param y: The right tensor for contraction.
    :param dim1: explicit lists of dimensions for x to contract.
    :param dim2: explicit lists of dimensions for y to contract.
    """
def softmax(t, axis: int = -1):
    """Applies the Softmax function to an n-dimensional input Tensor.

    Rescales them so that the elements of the n-dimensional output Tensor
    lie in the range [0,1] and sum to 1.

    Softmax is defined as:

    .. math::
        \\text{Softmax}(x_{i}) = \\frac{\\exp(x_i)}{\\sum_j \\exp(x_j)}
    
    :param t: input qtensor.
    :param axis: the dimension along which Softmax will be computed.
    
    :return: result qtensor.

    Examples::

        from pyvqnet.tensor import tensor
    """
def einsum(equation: str, *operands):
    """
    Sums the product of the elements of the input operands along dimensions specified using a notation based on the Einstein summation convention.

    .. note::

            This function uses opt_einsum (https://optimized-einsum.readthedocs.io/en/stable/) to speed up computation or to
            consume less memory by optimizing contraction order. This optimization occurs when there are at least three
            inputs.
        
    :param equation: The subscripts for the Einstein summation.
    :param operands: The tensors to compute the Einstein summation of.

    :return:
        result

    Example::

        from pyvqnet import tensor

        vqneta = tensor.randn((3, 5, 4))
        vqnetl = tensor.randn((2, 5))
        vqnetr = tensor.randn((2, 4))
        z = tensor.einsum('bn,anm,bm->ba',  vqnetl, vqneta, vqnetr)
        print(z.shape)
        #[2, 3]
        vqneta = tensor.randn((20,30,40,50))
        z = tensor.einsum('...ij->...ji', vqneta)
        print(z.shape)
        #[20, 30, 50, 40]
    """
def square_sum(a, b): ...
def log_softmax(t, axis: int = -1):
    """
    Combines log and softmax function into one function.
    :param t: input
    :param axis: reduce axis,default = -1
    :return QTensor

    Example::

        from pyvqnet import tensor
        output = tensor.arange(1,13).reshape([3,2,2])
        t = tensor.log_softmax(output,1)
        print(t)
        # [
        # [[-2.1269281, -2.1269281],
        #  [-0.1269280, -0.1269280]],
        # [[-2.1269281, -2.1269281],
        #  [-0.1269280, -0.1269280]],
        # [[-2.1269281, -2.1269281],
        #  [-0.1269280, -0.1269280]]
        # ]
    """
def pad(t, pad: _shape_type, value: _scalar_type = 0):
    """

    Padding input tensor with constant value.

    Padding size:
    The padding size by which to pad some dimensions of :attr:`input`
    are described starting from the last dimension and moving forward.
    :math:`\\left\\lfloor\x0crac{\text{len(pad)}}{2}\right\rfloor` dimensions
    of ``input`` will be padded.
    For example, to pad only the last dimension of the input tensor, then
    :attr:`pad` has the form
    :math:`(\text{padding\\_left}, \text{padding\\_right})`;
    to pad the last 2 dimensions of the input tensor, then use
    :math:`(\text{padding\\_left}, \text{padding\\_right},`
    :math:`\text{padding\\_top}, \text{padding\\_bottom})`;
    to pad the last 3 dimensions, use
    :math:`(\text{padding\\_left}, \text{padding\\_right},`
    :math:`\text{padding\\_top}, \text{padding\\_bottom}`
    :math:`\text{padding\\_front}, \text{padding\\_back})`.

    :param t: input tensor.
    :param pad: pad list.
    :param value: constant padding value,default:0.

    Example::

        from pyvqnet import tensor
        t4d = tensor.ones((4, 2,3))
        z = tensor.pad(t4d, (0, 1, 3, 3,5,2), 2.)

    """
def roll(self, shifts, dims): ...
def roll_common(input_tensor, shifts, dims): ...
def pad2d(t, pad_list: list[int] | tuple[int], value: int | float = 0):
    """
    Pad 4d tensor of [b,c,w,h] to [b,c, w+pad_list[0]+pad_list[1], h+ pad_list[2]+pad_list[3] ] with value.

    :param t: input QTensor
    :param pad_list: pad length of (padding_left,padding_right, padding_top,padding_bottom)
    :param value: value to fill the padding area,default:0.

    :return new QTensor

    Example::
        from pyvqnet.tensor import ones,pad2d
        t4d = ones([1, 1, 4, 2], dtype=kk)
        t4d.requires_grad = True
        p1d = (2, 1, 0, 2)
        out = pad2d(t4d, p1d, 0)
    """
def allclose(t1, t2, rtol: float = 1e-05, atol: float = 1e-08, equal_nan: bool = False): ...
def dense_to_csr(x):
    """
    create a csr format sparse tensor from dense tensor.

    :param x: input dense QTensor
    :return: csr format sparse QTensor.
    """
def csr_to_dense(x):
    """
    create a dense tensor from csr format sparse tensor.

    :param x: csr format sparse QTensor.
    :return: dense QTensor.
    """
def block_diag(tensors: list[QTensor]):
    """Autograd implementation of scipy.linalg.block_diag。
    
    :param tensors: list of input qtensors,should be 2d.
    :return:
         block_diag of inputs.

    """
def astype(t1, dtype): ...
def solver(A, b, type: str = 'LU'): ...
def autograd_backward(tensors, grad_tensors) -> None: ...
