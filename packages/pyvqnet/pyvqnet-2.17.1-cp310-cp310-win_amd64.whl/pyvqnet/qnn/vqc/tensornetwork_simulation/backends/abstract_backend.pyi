from ..utils import return_partial as return_partial
from typing import Any, Callable, Sequence

Tensor = Any

class ExtendedBackend:
    """
    Add tensorcircuit specific backend methods, especially with their docstrings.
    """
    def copy(self, a: Tensor) -> Tensor:
        """
        Return the copy of ``a``, matrix exponential.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: matrix exponential of matrix ``a``
        :rtype: Tensor
        """
    def expm(self, a: Tensor) -> Tensor:
        """
        Return the expm of tensor ''a''.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: matrix exponential of matrix ``a``
        :rtype: Tensor
        """
    def sqrtmh(self, a: Tensor) -> Tensor:
        """
        Return the sqrtm of a Hermitian matrix ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: sqrtm of ``a``
        :rtype: Tensor
        """
    def eigvalsh(self, a: Tensor) -> Tensor:
        """
        Get the eigenvalues of matrix ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: eigenvalues of ``a``
        :rtype: Tensor
        """
    def sin(self, a: Tensor) -> Tensor:
        """
        Return the  elementwise sine of a tensor ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: sine of ``a``
        :rtype: Tensor
        """
    def cos(self, a: Tensor) -> Tensor:
        """
        Return the cosine of a tensor ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: cosine of ``a``
        :rtype: Tensor
        """
    def acos(self, a: Tensor) -> Tensor:
        """
        Return the acos of a tensor ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: acos of ``a``
        :rtype: Tensor
        """
    def acosh(self, a: Tensor) -> Tensor:
        """
        Return the acosh of a tensor ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: acosh of ``a``
        :rtype: Tensor
        """
    def asin(self, a: Tensor) -> Tensor:
        """
        Return the acos of a tensor ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: asin of ``a``
        :rtype: Tensor
        """
    def asinh(self, a: Tensor) -> Tensor:
        """
        Return the asinh of a tensor ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: asinh of ``a``
        :rtype: Tensor
        """
    def atan(self, a: Tensor) -> Tensor:
        """
        Return the atan of a tensor ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: atan of ``a``
        :rtype: Tensor
        """
    def atan2(self, y: Tensor, x: Tensor) -> Tensor:
        """
        Return the atan of a tensor ``y``/``x``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: atan2 of ``a``
        :rtype: Tensor
        """
    def atanh(self, a: Tensor) -> Tensor:
        """
        Return the atanh of a tensor ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: atanh of ``a``
        :rtype: Tensor
        """
    def cosh(self, a: Tensor) -> Tensor:
        """
        Return the cosh of a tensor ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: cosh of ``a``
        :rtype: Tensor
        """
    def tan(self, a: Tensor) -> Tensor:
        """
        Return the tan of a tensor ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: tan of ``a``
        :rtype: Tensor
        """
    def tanh(self, a: Tensor) -> Tensor:
        """
        Return the tanh of a tensor ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: tanh of ``a``
        :rtype: Tensor
        """
    def sinh(self, a: Tensor) -> Tensor:
        """
        Return the sinh of a tensor ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: sinh of ``a``
        :rtype: Tensor
        """
    def abs(self, a: Tensor) -> Tensor:
        """
        Return the elementwise abs value of a matrix ``a``.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: abs of ``a``
        :rtype: Tensor
        """
    def kron(self, a: Tensor, b: Tensor) -> Tensor:
        """
        Return the kronecker product of two matrices ``a`` and ``b``.

        :param a: tensor in matrix form
        :type a: Tensor
        :param b: tensor in matrix form
        :type b: Tensor
        :return: kronecker product of ``a`` and ``b``
        :rtype: Tensor
        """
    def size(self, a: Tensor) -> Tensor:
        """
        Return the total number of elements in ``a`` in tensor form.

        :param a: tensor
        :type a: Tensor
        :return: the total number of elements in ``a``
        :rtype: Tensor
        """
    def sizen(self, a: Tensor) -> int:
        """
        Return the total number of elements in tensor ``a``, but in integer form.

        :param a: tensor
        :type a: Tensor
        :return: the total number of elements in tensor ``a``
        :rtype: int
        """
    def numpy(self, a: Tensor) -> Tensor:
        """
        Return the numpy array of a tensor ``a``, but may not work in a jitted function.

        :param a: tensor in matrix form
        :type a: Tensor
        :return: numpy array of ``a``
        :rtype: Tensor
        """
    def real(self, a: Tensor) -> Tensor:
        """
        Return the elementwise real value of a tensor ``a``.

        :param a: tensor
        :type a: Tensor
        :return: real value of ``a``
        :rtype: Tensor
        """
    def imag(self, a: Tensor) -> Tensor:
        """
        Return the elementwise imaginary value of a tensor ``a``.

        :param a: tensor
        :type a: Tensor
        :return: imaginary value of ``a``
        :rtype: Tensor
        """
    def adjoint(self, a: Tensor) -> Tensor:
        """
        Return the conjugate and transpose of a tensor ``a``

        :param a: Input tensor
        :type a: Tensor
        :return: adjoint tensor of ``a``
        :rtype: Tensor
        """
    def i(self, dtype: str) -> Tensor:
        '''
        Return 1.j in as a tensor compatible with the backend.

        :param dtype: "complex64" or "complex128"
        :type dtype: str
        :return: 1.j tensor
        :rtype: Tensor
        '''
    def reshape2(self, a: Tensor) -> Tensor:
        """
        Reshape a tensor to the [2, 2, ...] shape.

        :param a: Input tensor
        :type a: Tensor
        :return: the reshaped tensor
        :rtype: Tensor
        """
    def reshapem(self, a: Tensor) -> Tensor:
        """
        Reshape a tensor to the [l, l] shape.

        :param a: Input tensor
        :type a: Tensor
        :return: the reshaped tensor
        :rtype: Tensor
        """
    def dtype(self, a: Tensor) -> str:
        '''
        Obtain dtype string for tensor ``a``

        :param a: The tensor
        :type a: Tensor
        :return: dtype str, such as "complex64"
        :rtype: str
        '''
    def stack(self, a, axis: int = 0) -> Tensor:
        """
        Concatenates a sequence of tensors ``a`` along a new dimension ``axis``.

        :param a: List of tensors in the same shape
        :type a: Sequence[Tensor]
        :param axis: the stack axis, defaults to 0
        :type axis: int, optional
        :return: concatenated tensor
        :rtype: Tensor
        """
    def concat(self, a: Sequence[Tensor], axis: int = 0) -> Tensor:
        """
        Join a sequence of arrays along an existing axis.

        :param a: [description]
        :type a: Sequence[Tensor]
        :param axis: [description], defaults to 0
        :type axis: int, optional
        """
    def tile(self, a: Tensor, rep: Tensor) -> Tensor:
        """
        Constructs a tensor by tiling a given tensor.

        :param a: [description]
        :type a: Tensor
        :param rep: 1d tensor with length the same as the rank of ``a``
        :type rep: Tensor
        :return: [description]
        :rtype: Tensor
        """
    def mean(self, a: Tensor, axis: Sequence[int] | None = None, keepdims: bool = False) -> Tensor:
        """
        Compute the arithmetic mean for ``a`` along the specified ``axis``.

        :param a: tensor to take average
        :type a: Tensor
        :param axis: the axis to take mean, defaults to None indicating sum over flatten array
        :type axis: Optional[Sequence[int]], optional
        :param keepdims: _description_, defaults to False
        :type keepdims: bool, optional
        :return: _description_
        :rtype: Tensor
        """
    def std(self, a: Tensor, axis: Sequence[int] | None = None, keepdims: bool = False) -> Tensor:
        """
        Compute the standard deviation along the specified axis.

        :param a: _description_
        :type a: Tensor
        :param axis: Axis or axes along which the standard deviation is computed,
            defaults to None, implying all axis
        :type axis: Optional[Sequence[int]], optional
        :param keepdims: If this is set to True,
            the axes which are reduced are left in the result as dimensions with size one,
            defaults to False
        :type keepdims: bool, optional
        :return: _description_
        :rtype: Tensor
        """
    def min(self, a: Tensor, axis: int | None = None) -> Tensor:
        """
        Return the minimum of an array or minimum along an axis.

        :param a: [description]
        :type a: Tensor
        :param axis: [description], defaults to None
        :type axis: Optional[int], optional
        :return: [description]
        :rtype: Tensor
        """
    def max(self, a: Tensor, axis: int | None = None) -> Tensor:
        """
        Return the maximum of an array or maximum along an axis.

        :param a: [description]
        :type a: Tensor
        :param axis: [description], defaults to None
        :type axis: Optional[int], optional
        :return: [description]
        :rtype: Tensor
        """
    def argmax(self, a: Tensor, axis: int = 0) -> Tensor:
        """
        Return the index of maximum of an array an axis.

        :param a: [description]
        :type a: Tensor
        :param axis: [description], defaults to 0, different behavior from numpy defaults!
        :type axis: int
        :return: [description]
        :rtype: Tensor
        """
    def argmin(self, a: Tensor, axis: int = 0) -> Tensor:
        """
        Return the index of minimum of an array an axis.

        :param a: [description]
        :type a: Tensor
        :param axis: [description], defaults to 0, different behavior from numpy defaults!
        :type axis: int
        :return: [description]
        :rtype: Tensor
        """
    def unique_with_counts(self, a: Tensor, **kws: Any) -> tuple[Tensor, Tensor]:
        """
        Find the unique elements and their corresponding counts of the given tensor ``a``.

        :param a: [description]
        :type a: Tensor
        :return: Unique elements, corresponding counts
        :rtype: Tuple[Tensor, Tensor]
        """
    def sigmoid(self, a: Tensor) -> Tensor:
        """
        Compute sigmoid of input ``a``

        :param a: [description]
        :type a: Tensor
        :return: [description]
        :rtype: Tensor
        """
    def relu(self, a: Tensor) -> Tensor:
        """
        Rectified linear unit activation function.
        Computes the element-wise function:

        .. math ::

            \\mathrm{relu}(x)=\\max(x,0)


        :param a: Input tensor
        :type a: Tensor
        :return: Tensor after relu
        :rtype: Tensor
        """
    def softmax(self, a: Sequence[Tensor], axis: int | None = None) -> Tensor:
        """
        Softmax function.
        Computes the function which rescales elements to the range [0,1] such that the elements along axis sum to 1.

        .. math ::

            \\mathrm{softmax}(x) = \\frac{\\exp(x_i)}{\\sum_j \\exp(x_j)}


        :param a: Tensor
        :type a: Sequence[Tensor]
        :param axis: A dimension along which Softmax will be computed , defaults to None for all axis sum.
        :type axis: int, optional
        :return: concatenated tensor
        :rtype: Tensor
        """
    def onehot(self, a: Tensor, num: int) -> Tensor:
        """
        One-hot encodes the given ``a``.
        Each index in the input ``a`` is encoded as a vector of zeros of length ``num``
        with the element at index set to one:

        :param a: input tensor
        :type a: Tensor
        :param num: number of features in onehot dimension
        :type num: int
        :return: onehot tensor with the last extra dimension
        :rtype: Tensor
        """
    def one_hot(self, a: Tensor, num: int) -> Tensor:
        """
        See doc for :py:meth:`onehot`
        """
    def cumsum(self, a: Tensor, axis: int | None = None) -> Tensor:
        """
        Return the cumulative sum of the elements along a given axis.

        :param a: [description]
        :type a: Tensor
        :param axis: The default behavior is the same as numpy, different from tf/torch
            as cumsum of the flatten 1D array, defaults to None
        :type axis: Optional[int], optional
        :return: [description]
        :rtype: Tensor
        """
    def is_tensor(self, a: Tensor) -> bool:
        """
        Return a boolean on whether ``a`` is a tensor in backend package.

        :param a: a tensor to be determined
        :type a: Tensor
        :return: whether ``a`` is a tensor
        :rtype: bool
        """
    def cast(self, a: Tensor, dtype: str) -> Tensor:
        '''
        Cast the tensor dtype of a ``a``.

        :param a: tensor
        :type a: Tensor
        :param dtype: "float32", "float64", "complex64", "complex128"
        :type dtype: str
        :return: ``a`` of new dtype
        :rtype: Tensor
        '''
    def mod(self, x: Tensor, y: Tensor) -> Tensor:
        """
        Compute y-mod of x (negative number behavior is not guaranteed to be consistent)

        :param x: input values
        :type x: Tensor
        :param y: mod ``y``
        :type y: Tensor
        :return: results
        :rtype: Tensor
        """
    def reverse(self, a: Tensor) -> Tensor:
        """
        return ``a[::-1]``, only 1D tensor is guaranteed for consistent behavior

        :param a: 1D tensor
        :type a: Tensor
        :return: 1D tensor in reverse order
        :rtype: Tensor
        """
    def right_shift(self, x: Tensor, y: Tensor) -> Tensor:
        """
        Shift the bits of an integer x to the right y bits.

        :param x: input values
        :type x: Tensor
        :param y: Number of bits shift to ``x``
        :type y: Tensor
        :return: result with the same shape as ``x``
        :rtype: Tensor
        """
    def left_shift(self, x: Tensor, y: Tensor) -> Tensor:
        """
        Shift the bits of an integer x to the left y bits.

        :param x: input values
        :type x: Tensor
        :param y: Number of bits shift to ``x``
        :type y: Tensor
        :return: result with the same shape as ``x``
        :rtype: Tensor
        """
    def arange(self, start: int, stop: int | None = None, step: int = 1) -> Tensor:
        """
        Values are generated within the half-open interval [start, stop)

        :param start: start index
        :type start: int
        :param stop: end index, defaults to None
        :type stop: Optional[int], optional
        :param step: steps, defaults to 1
        :type step: Optional[int], optional
        :return: _description_
        :rtype: Tensor
        """
    def solve(self, A: Tensor, b: Tensor, **kws: Any) -> Tensor:
        """
        Solve the linear system Ax=b and return the solution x.

        :param A: The multiplied matrix.
        :type A: Tensor
        :param b: The resulted matrix.
        :type b: Tensor
        :return: The solution of the linear system.
        :rtype: Tensor
        """
    def searchsorted(self, a: Tensor, v: Tensor, side: str = 'left') -> Tensor:
        '''
        Find indices where elements should be inserted to maintain order.

        :param a: input array sorted in ascending order
        :type a: Tensor
        :param v: value to inserted
        :type v: Tensor
        :param side:  If ‘left’, the index of the first suitable location found is given.
            If ‘right’, return the last such index.
            If there is no suitable index, return either 0 or N (where N is the length of a),
            defaults to "left"
        :type side: str, optional
        :return: Array of insertion points with the same shape as v, or an integer if v is a scalar.
        :rtype: Tensor
        '''
    def tree_map(self, f: Callable[..., Any], *pytrees: Any) -> Any:
        """
        Return the new tree map with multiple arg function ``f`` through pytrees.

        :param f: The function
        :type f: Callable[..., Any]
        :param pytrees: inputs as any python structure
        :type pytrees: Any
        :raises NotImplementedError: raise when neither tensorflow or jax is installed.
        :return: The new tree map with the same structure but different values.
        :rtype: Any
        """
    def tree_flatten(self, pytree: Any) -> tuple[Any, Any]:
        """
        Flatten python structure to 1D list

        :param pytree: python structure to be flattened
        :type pytree: Any
        :return: The 1D list of flattened structure and treedef
            which can be used for later unflatten
        :rtype: Tuple[Any, Any]
        """
    def tree_unflatten(self, treedef: Any, leaves: Any) -> Any:
        """
        Pack 1D list to pytree defined via ``treedef``

        :param treedef: Def of pytree structure, the second return from ``tree_flatten``
        :type treedef: Any
        :param leaves: the 1D list of flattened data structure
        :type leaves: Any
        :return: Packed pytree
        :rtype: Any
        """
    def to_dlpack(self, a: Tensor) -> Any:
        """
        Transform the tensor ``a`` as a dlpack capsule

        :param a: _description_
        :type a: Tensor
        :return: _description_
        :rtype: Any
        """
    def from_dlpack(self, a: Any) -> Tensor:
        """
        Transform a dlpack capsule to a tensor

        :param a: the dlpack capsule
        :type a: Any
        :return: _description_
        :rtype: Tensor
        """
    def set_random_state(self, seed: int | None = None, get_only: bool = False) -> Any:
        """
        Set the random state attached to the backend.

        :param seed: the random seed, defaults to be None
        :type seed: Optional[int], optional
        :param get_only: If set to be true, only get the random state in return
            instead of setting the state on the backend
        :type get_only: bool, defaults to be False
        """
    def get_random_state(self, seed: int | None = None) -> Any:
        """
        Get the backend specific random state object.

        :param seed: [description], defaults to be None
        :type seed: Optional[int], optional
        :return:the backend specific random state object
        :rtype: Any
        """
    def random_split(self, key: Any) -> tuple[Any, Any]:
        """
        A jax like split API, but it doesn't split the key generator for other backends.
        It is just for a consistent interface of random code;
        make sure you know what the function actually does.
        This function is mainly a utility to write backend agnostic code instead of doing magic things.

        :param key: [description]
        :type key: Any
        :return: [description]
        :rtype: Tuple[Any, Any]
        """
    def implicit_randn(self, shape: int | Sequence[int] = 1, mean: float = 0, stddev: float = 1, dtype: str = '32') -> Tensor:
        '''
        Call the random normal function with the random state management behind the scene.

        :param shape: [description], defaults to 1
        :type shape: Union[int, Sequence[int]], optional
        :param mean: [description], defaults to 0
        :type mean: float, optional
        :param stddev: [description], defaults to 1
        :type stddev: float, optional
        :param dtype: [description], defaults to "32"
        :type dtype: str, optional
        :return: [description]
        :rtype: Tensor
        '''
    def stateful_randn(self, g: Any, shape: int | Sequence[int] = 1, mean: float = 0, stddev: float = 1, dtype: str = '32') -> Tensor:
        '''
        [summary]

        :param self: [description]
        :type self: Any
        :param g: stateful register for each package
        :type g: Any
        :param shape: shape of output sampling tensor
        :type shape: Union[int, Sequence[int]]
        :param mean: [description], defaults to 0
        :type mean: float, optional
        :param stddev: [description], defaults to 1
        :type stddev: float, optional
        :param dtype: only real data type is supported, "32" or "64", defaults to "32"
        :type dtype: str, optional
        :return: [description]
        :rtype: Tensor
        '''
    def implicit_randu(self, shape: int | Sequence[int] = 1, low: float = 0, high: float = 1, dtype: str = '32') -> Tensor:
        '''
        Call the random normal function with the random state management behind the scene.

        :param shape: [description], defaults to 1
        :type shape: Union[int, Sequence[int]], optional
        :param mean: [description], defaults to 0
        :type mean: float, optional
        :param stddev: [description], defaults to 1
        :type stddev: float, optional
        :param dtype: [description], defaults to "32"
        :type dtype: str, optional
        :return: [description]
        :rtype: Tensor
        '''
    def stateful_randu(self, g: Any, shape: int | Sequence[int] = 1, low: float = 0, high: float = 1, dtype: str = '32') -> Tensor:
        '''
        Uniform random sampler from ``low`` to ``high``.

        :param g: stateful register for each package
        :type g: Any
        :param shape: shape of output sampling tensor, defaults to 1
        :type shape: Union[int, Sequence[int]], optional
        :param low: [description], defaults to 0
        :type low: float, optional
        :param high: [description], defaults to 1
        :type high: float, optional
        :param dtype: only real data type is supported, "32" or "64", defaults to "32"
        :type dtype: str, optional
        :return: [description]
        :rtype: Tensor
        '''
    def implicit_randc(self, a: int | Sequence[int] | Tensor, shape: int | Sequence[int], p: Sequence[float] | Tensor | None = None) -> Tensor:
        """
        [summary]

        :param g: [description]
        :type g: Any
        :param a: The possible options
        :type a: Union[int, Sequence[int], Tensor]
        :param shape: Sampling output shape
        :type shape: Union[int, Sequence[int]]
        :param p: probability for each option in a, defaults to None, as equal probability distribution
        :type p: Optional[Union[Sequence[float], Tensor]], optional
        :return: [description]
        :rtype: Tensor
        """
    def stateful_randc(self, g: Any, a: int | Sequence[int] | Tensor, shape: int | Sequence[int], p: Sequence[float] | Tensor | None = None) -> Tensor:
        """
        [summary]

        :param g: [description]
        :type g: Any
        :param a: The possible options
        :type a: Union[int, Sequence[int], Tensor]
        :param shape: Sampling output shape
        :type shape: Union[int, Sequence[int]]
        :param p: probability for each option in a, defaults to None, as equal probability distribution
        :type p: Optional[Union[Sequence[float], Tensor]], optional
        :return: [description]
        :rtype: Tensor
        """
    def probability_sample(self, shots: int, p: Tensor, status: Tensor | None = None, g: Any = None) -> Tensor:
        """
        Drawn ``shots`` samples from probability distribution p, given the external randomness
        determined by uniform distributed ``status`` tensor or backend random generator ``g``.
        This method is similar with ``stateful_randc``, but it supports ``status`` beyond ``g``,
        which is convenient when jit or vmap

        :param shots: Number of samples to draw with replacement
        :type shots: int
        :param p: prbability vector
        :type p: Tensor
        :param status: external randomness as a tensor with each element drawn uniformly from [0, 1],
            defaults to None
        :type status: Optional[Tensor], optional
        :param g: backend random genrator, defaults to None
        :type g: Any, optional
        :return: The drawn sample as an int tensor
        :rtype: Tensor
        """
    def gather1d(self, operand: Tensor, indices: Tensor) -> Tensor:
        """
        Return ``operand[indices]``, both ``operand`` and ``indices`` are rank-1 tensor.

        :param operand: rank-1 tensor
        :type operand: Tensor
        :param indices: rank-1 tensor with int dtype
        :type indices: Tensor
        :return: ``operand[indices]``
        :rtype: Tensor
        """
    def scatter(self, operand: Tensor, indices: Tensor, updates: Tensor) -> Tensor:
        """
        Roughly equivalent to operand[indices] = updates, indices only support shape with rank 2 for now.

        :param operand: [description]
        :type operand: Tensor
        :param indices: [description]
        :type indices: Tensor
        :param updates: [description]
        :type updates: Tensor
        :return: [description]
        :rtype: Tensor
        """
    def coo_sparse_matrix(self, indices: Tensor, values: Tensor, shape: Tensor) -> Tensor:
        """
        Generate the coo format sparse matrix from indices and values,
        which is the only sparse format supported in different ML backends.

        :param indices: shape [n, 2] for n non zero values in the returned matrix
        :type indices: Tensor
        :param values: shape [n]
        :type values: Tensor
        :param shape: Tuple[int, ...]
        :type shape: Tensor
        :return: [description]
        :rtype: Tensor
        """
    def coo_sparse_matrix_from_numpy(self, a: Tensor) -> Tensor:
        """
        Generate the coo format sparse matrix from scipy coo sparse matrix.

        :param a: Scipy coo format sparse matrix
        :type a: Tensor
        :return: SparseTensor in backend format
        :rtype: Tensor
        """
    def sparse_dense_matmul(self, sp_a: Tensor, b: Tensor) -> Tensor:
        """
        A sparse matrix multiplies a dense matrix.

        :param sp_a: a sparse matrix
        :type sp_a: Tensor
        :param b: a dense matrix
        :type b: Tensor
        :return: dense matrix
        :rtype: Tensor
        """
    def to_dense(self, sp_a: Tensor) -> Tensor:
        """
        Convert a sparse matrix to dense tensor.

        :param sp_a: a sparse matrix
        :type sp_a: Tensor
        :return: the resulted dense matrix
        :rtype: Tensor
        """
    def is_sparse(self, a: Tensor) -> bool:
        """
        Determine whether the type of input ``a`` is  ``sparse``.

        :param a: input matrix ``a``
        :type a: Tensor
        :return: a bool indicating whether the matrix ``a`` is sparse
        :rtype: bool
        """
    def device(self, a: Tensor) -> str:
        """
        get the universal device str for the tensor, in the format of tf

        :param a: the tensor
        :type a: Tensor
        :return: device str where the tensor lives on
        :rtype: str
        """
    def device_move(self, a: Tensor, dev: Any) -> Tensor:
        """
        move tensor ``a`` to device ``dev``

        :param a: the tensor
        :type a: Tensor
        :param dev: device str or device obj in corresponding backend
        :type dev: Any
        :return: the tensor on new device
        :rtype: Tensor
        """
    def cond(self, pred: bool, true_fun: Callable[[], Tensor], false_fun: Callable[[], Tensor]) -> Tensor:
        """
        The native cond for XLA compiling, wrapper for ``tf.cond`` and limited functionality of ``jax.lax.cond``.

        :param pred: [description]
        :type pred: bool
        :param true_fun: [description]
        :type true_fun: Callable[[], Tensor]
        :param false_fun: [description]
        :type false_fun: Callable[[], Tensor]
        :return: [description]
        :rtype: Tensor
        """
    def switch(self, index: Tensor, branches: Sequence[Callable[[], Tensor]]) -> Tensor:
        """
        ``branches[index]()``

        :param index: [description]
        :type index: Tensor
        :param branches: [description]
        :type branches: Sequence[Callable[[], Tensor]]
        :return: [description]
        :rtype: Tensor
        """
    def stop_gradient(self, a: Tensor) -> Tensor:
        """
        Stop backpropagation from ``a``.

        :param a: [description]
        :type a: Tensor
        :return: [description]
        :rtype: Tensor
        """
    def grad(self, f: Callable[..., Any], argnums: int | Sequence[int] = 0, has_aux: bool = False) -> Callable[..., Any]:
        """
        Return the function which is the grad function of input ``f``.

        :Example:

        >>> f = lambda x,y: x**2+2*y
        >>> g = tc.backend.grad(f)
        >>> g(tc.num_to_tensor(1),tc.num_to_tensor(2))
        2
        >>> g = tc.backend.grad(f, argnums=(0,1))
        >>> g(tc.num_to_tensor(1),tc.num_to_tensor(2))
        [2, 2]

        :param f: the function to be differentiated
        :type f: Callable[..., Any]
        :param argnums: the position of args in ``f`` that are to be differentiated, defaults to be 0
        :type argnums: Union[int, Sequence[int]], optional
        :return: the grad function of ``f`` with the same set of arguments as ``f``
        :rtype: Callable[..., Any]
        """
    def value_and_grad(self, f: Callable[..., Any], argnums: int | Sequence[int] = 0, hax_aux: bool = False) -> Callable[..., tuple[Any, Any]]:
        """
        Return the function which returns the value and grad of ``f``.

        :Example:

        >>> f = lambda x,y: x**2+2*y
        >>> g = tc.backend.value_and_grad(f)
        >>> g(tc.num_to_tensor(1),tc.num_to_tensor(2))
        5, 2
        >>> g = tc.backend.value_and_grad(f, argnums=(0,1))
        >>> g(tc.num_to_tensor(1),tc.num_to_tensor(2))
        5, [2, 2]

        :param f: the function to be differentiated
        :type f: Callable[..., Any]
        :param argnums: the position of args in ``f`` that are to be differentiated, defaults to be 0
        :type argnums: Union[int, Sequence[int]], optional
        :return: the value and grad function of ``f`` with the same set of arguments as ``f``
        :rtype: Callable[..., Tuple[Any, Any]]
        """
    def jvp(self, f: Callable[..., Any], inputs: Tensor | Sequence[Tensor], v: Tensor | Sequence[Tensor]) -> tuple[Tensor | Sequence[Tensor], Tensor | Sequence[Tensor]]:
        """
        Function that computes a (forward-mode) Jacobian-vector product of ``f``.
        Strictly speaking, this function is value_and_jvp.

        :param f: The function to compute jvp
        :type f: Callable[..., Any]
        :param inputs: input for ``f``
        :type inputs: Union[Tensor, Sequence[Tensor]]
        :param v: tangents
        :type v: Union[Tensor, Sequence[Tensor]]
        :return: (``f(*inputs)``, jvp_tensor), where jvp_tensor is the same shape as the output of ``f``
        :rtype: Tuple[Union[Tensor, Sequence[Tensor]], Union[Tensor, Sequence[Tensor]]]
        """
    def vjp(self, f: Callable[..., Any], inputs: Tensor | Sequence[Tensor], v: Tensor | Sequence[Tensor]) -> tuple[Tensor | Sequence[Tensor], Tensor | Sequence[Tensor]]:
        """
        Function that computes the dot product between a vector v and the Jacobian
        of the given function at the point given by the inputs. (reverse mode AD relevant)
        Strictly speaking, this function is value_and_vjp.

        :param f: the function to carry out vjp calculation
        :type f: Callable[..., Any]
        :param inputs: input for ``f``
        :type inputs: Union[Tensor, Sequence[Tensor]]
        :param v: value vector or gradient from downstream in reverse mode AD
            the same shape as return of function ``f``
        :type v: Union[Tensor, Sequence[Tensor]]
        :return: (``f(*inputs)``, vjp_tensor), where vjp_tensor is the same shape as inputs
        :rtype: Tuple[Union[Tensor, Sequence[Tensor]], Union[Tensor, Sequence[Tensor]]]
        """
    def jacfwd(self, f: Callable[..., Any], argnums: int | Sequence[int] = 0) -> Tensor:
        """
        Compute the Jacobian of ``f`` using the forward mode AD.

        :param f: the function whose Jacobian is required
        :type f: Callable[..., Any]
        :param argnums: the position of the arg as Jacobian input, defaults to 0
        :type argnums: Union[int, Sequence[int]], optional
        :return: outer tuple for input args, inner tuple for outputs
        :rtype: Tensor
        """
    def jacrev(self, f: Callable[..., Any], argnums: int | Sequence[int] = 0) -> Tensor:
        """
        Compute the Jacobian of ``f`` using reverse mode AD.

        :param f: The function whose Jacobian is required
        :type f: Callable[..., Any]
        :param argnums: the position of the arg as Jacobian input, defaults to 0
        :type argnums: Union[int, Sequence[int]], optional
        :return: outer tuple for output, inner tuple for input args
        :rtype: Tensor
        """
    jacbwd = jacrev
    def hessian(self, f: Callable[..., Any], argnums: int | Sequence[int] = 0) -> Tensor: ...
    def jit(self, f: Callable[..., Any], static_argnums: int | Sequence[int] | None = None, jit_compile: bool | None = None) -> Callable[..., Any]:
        """
        Return the jitted version of function ``f``.

        :param f: function to be jitted
        :type f: Callable[..., Any]
        :param static_argnums: index of args that doesn't regarded as tensor,
            only work for jax backend
        :type static_argnums: Optional[Union[int, Sequence[int]]], defaults to None
        :param jit_compile: whether open XLA compilation, only works for tensorflow backend,
            defaults False since several ops has no XLA correspondence
        :type jit_compile: bool
        :return: jitted version of ``f``
        :rtype: Callable[..., Any]
        """
    def vmap(self, f: Callable[..., Any], vectorized_argnums: int | Sequence[int] = 0) -> Any:
        """
        Return the vectorized map or batched version of ``f`` on the first extra axis.
        The general interface supports ``f`` with multiple arguments and broadcast in the fist dimension.

        :param f: function to be broadcasted.
        :type f: Callable[..., Any]
        :param vectorized_argnums: the args to be vectorized,
            these arguments should share the same batch shape in the fist dimension
        :type vectorized_argnums: Union[int, Sequence[int]], defaults to 0
        :return: vmap version of ``f``
        :rtype: Any
        """
    def vectorized_value_and_grad(self, f: Callable[..., Any], argnums: int | Sequence[int] = 0, vectorized_argnums: int | Sequence[int] = 0, has_aux: bool = False) -> Callable[..., tuple[Any, Any]]:
        """
        Return the VVAG function of ``f``. The inputs for ``f`` is (args[0], args[1], args[2], ...),
        and the output of ``f`` is a scalar. Suppose VVAG(f) is a function with inputs in the form
        (vargs[0], args[1], args[2], ...), where vagrs[0] has one extra dimension than args[0] in the first axis
        and consistent with args[0] in shape for remaining dimensions, i.e. shape(vargs[0]) = [batch] + shape(args[0]).
        (We only cover cases where ``vectorized_argnums`` defaults to 0 here for demonstration).
        VVAG(f) returns a tuple as a value tensor with shape [batch, 1] and a gradient tuple with shape:
        ([batch]+shape(args[argnum]) for argnum in argnums). The gradient for argnums=k is defined as

        .. math::

            g^k = \\frac{\\partial \\sum_{i\\in batch} f(vargs[0][i], args[1], ...)}{\\partial args[k]}

        Therefore, if argnums=0, the gradient is reduced to

        .. math::

            g^0_i = \\frac{\\partial f(vargs[0][i])}{\\partial vargs[0][i]}

        , which is specifically suitable for batched VQE optimization, where args[0] is the circuit parameters.

        And if argnums=1, the gradient is like

        .. math::
            g^1_i = \\frac{\\partial \\sum_j f(vargs[0][j], args[1])}{\\partial args[1][i]}

        , which is suitable for quantum machine learning scenarios, where ``f`` is the loss function,
        args[0] corresponds to the input data and args[1] corresponds to the weights in the QML model.

        :param f: [description]
        :type f: Callable[..., Any]
        :param argnums: [description], defaults to 0
        :type argnums: Union[int, Sequence[int]], optional
        :param vectorized_argnums: the args to be vectorized, these arguments should share the same batch shape
            in the fist dimension
        :type vectorized_argnums: Union[int, Sequence[int]], defaults to 0
        :return: [description]
        :rtype: Callable[..., Tuple[Any, Any]]
        """
