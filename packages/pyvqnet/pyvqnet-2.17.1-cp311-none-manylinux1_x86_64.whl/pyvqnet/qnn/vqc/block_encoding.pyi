from ...device import DEV_GPU as DEV_GPU
from ...dtype import float_dtype_to_complex_dtype as float_dtype_to_complex_dtype, kcomplex128 as kcomplex128, kcomplex64 as kcomplex64, kfloat32 as kfloat32, kfloat64 as kfloat64
from ...nn import ModuleList as ModuleList
from ...tensor import QTensor as QTensor, tensor as tensor
from .qcircuit import CNOT as CNOT, Hadamard as Hadamard, RY as RY, SWAP as SWAP, unitary as unitary
from .qmatrix import double_mat_dict as double_mat_dict, float_mat_dict as float_mat_dict
from .qop import QModule as QModule
from .utils.utils import expand_matrix as expand_matrix
from _typeshed import Incomplete
from functools import reduce as reduce

def gray_code(rank):
    """Generates the Gray code of given rank.

    Args:
        rank (int): rank of the Gray code (i.e. number of bits)
    """
def compute_theta(alpha):
    """Maps the angles alpha of the multi-controlled rotations decomposition of a uniformly controlled rotation
     to the rotation angles used in the Gray code implementation.

    Args:
        alpha (tensor_like): alpha parameters

    Returns:
        (tensor_like): rotation angles theta
    """

class VQC_BlockEncoding(QModule):
    vqc: Incomplete
    wires: Incomplete
    def __init__(self, wires=...) -> None: ...
    def create_circuit(self, *args, **kwargs) -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine) -> None: ...

class VQC_FABLE(VQC_BlockEncoding):
    """
    Construct a VQC based QCircuit with the fast approximate block encoding method.

    The FABLE method allows to simplify block encoding circuits without reducing accuracy,
    for matrices of specific structure [`arXiv:2205.00081 <https://arxiv.org/abs/2205.00081>`_].

    :param wires (Any or Iterable[Any]): qlist index that the operator acts on.

    Raises:
        ValueError: if the number of wires doesn't fit the dimensions of the matrix

    Examples::

        from pyvqnet.qnn.vqc import VQC_FABLE
        from pyvqnet.qnn.vqc import QMachine
        from pyvqnet.dtype import float_dtype_to_complex_dtype
        import numpy as np
        from pyvqnet import QTensor
        
        A = QTensor(np.array([[0.1, 0.2 ], [0.3, 0.4 ]]) )
        qf = VQC_FABLE(list(range(3)))
        qm = QMachine(3,dtype=float_dtype_to_complex_dtype(A.dtype))
        qm.reset_states(1)
        z1 = qf(qm,A,0.001)
    """
    vqc: Incomplete
    wires: Incomplete
    def __init__(self, wires=...) -> None: ...
    input_matrix: Incomplete
    def create_circuit(self, input_matrix, tol): ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine, input_matrix, tol: int = 0): ...

class VQC_LCU(VQC_BlockEncoding):
    """
    Construct a VQC based QCircuit with the Linear Combination of Unitaries (LCU), `Hamiltonian Simulation by Qubitization <https://arxiv.org/abs/1610.06546>`_.
    Input dtype can be kfloat32, kfloat64,kcomplex64,kcomplex128
    Input should be Hermitian.

    :param wires (Any or Iterable[Any]): qlist index that the operator acts on, may need ancillary qubits.
    :param check_hermitian; check if input is Hermitian, defulat: True.

    Examples::

        from pyvqnet.qnn.vqc import VQC_LCU
        from pyvqnet.qnn.vqc import QMachine
        from pyvqnet.dtype import float_dtype_to_complex_dtype,kfloat64

        from pyvqnet import QTensor

        A = QTensor([[0.25,0,0,0.75],[0,-0.25,0.75,0],[0,0.75,0.25,0],[0.75,0,0,-0.25]],device=1001,dtype=kfloat64)
        qf = VQC_LCU(list(range(3)))
        qm = QMachine(3,dtype=float_dtype_to_complex_dtype(A.dtype))
        qm.reset_states(2)
        z1 = qf(qm,A)
        print(z1)
        

    """
    vqc: Incomplete
    wires: Incomplete
    check_hermitian: Incomplete
    def __init__(self, wires: list | tuple | None = None, check_hermitian: bool = True) -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine, input_matrix): ...

def pauli_decompose(matrix): ...
def compute_max_log2(N): ...
def kron_product(matrices, dtype, device): ...
def normalize_coefficients(coefficients): ...
def construct_V(v1): ...
def prep(data): ...
def select(LCU_ops, dtype, device): ...
def lcu(H): ...
def vqnet_sqrt_matrix(density_matrix): ...

class VQC_QSVT_BlockEncoding(VQC_BlockEncoding):
    """
    :param A: input matrix need to be encode.
    :param wires: which qubits index A acts on.
    """
    wires: Incomplete
    subspace: Incomplete
    A: Incomplete
    def __init__(self, A, wires) -> None: ...
    def adjoint(self) -> None: ...
    def compute_matrix(self): ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine):
        """
        :param q_machine: vqc quantum machine simulator.
        """

class PCPhase:
    phi: Incomplete
    hyperparameters: Incomplete
    wires: Incomplete
    def __init__(self, phi, dim, wires) -> None: ...
    def compute_matrix(self): ...

def qsvt(A, angles, wires, return_ops: bool = False): ...

class VQC_QSVT(QModule):
    """
    Implements the
    `quantum singular value transformation <https://arxiv.org/abs/1806.01838>`__ (QSVT) circuit by VQNet vqc operators.
    
    Given an :class:`~.Operator` :math:`U`, which block encodes the matrix :math:`A`, and a list of
    projector-controlled phase shift operations :math:`\x0bec{\\Pi}_\\phi`, this template applies a
    circuit for the quantum singular value transformation as follows.

    When the number of projector-controlled phase shifts is even (:math:`d` is odd), the QSVT
    circuit is defined as:

    .. math::

        U_{QSVT} = \tilde{\\Pi}_{\\phi_1}U\\left[\\prod^{(d-1)/2}_{k=1}\\Pi_{\\phi_{2k}}U^\\dagger
        \tilde{\\Pi}_{\\phi_{2k+1}}U\right]\\Pi_{\\phi_{d+1}}.


    And when the number of projector-controlled phase shifts is odd (:math:`d` is even):

    .. math::

        U_{QSVT} = \\left[\\prod^{d/2}_{k=1}\\Pi_{\\phi_{2k-1}}U^\\dagger\tilde{\\Pi}_{\\phi_{2k}}U\right]
        \\Pi_{\\phi_{d+1}}.

    This circuit applies a polynomial transformation (:math:`Poly^{SV}`) to the singular values of
    the block encoded matrix:

    .. math::

        \x08egin{align}
             U_{QSVT}(A, \x0bec{\\phi}) &=
             \x08egin{bmatrix}
                Poly^{SV}(A) & \\cdot \\\n                \\cdot & \\cdot
            \\end{bmatrix}.
        \\end{align}


    :param A: a general :math:`(n \times m)` matrix to be encoded.
    :param angles: a list of angles by which to shift to obtain the desired polynomial.
    :param wires: the qubits index the A acts on.

    Example::

        from pyvqnet import DEV_GPU
        from pyvqnet.qnn.vqc import QMachine,VQC_QSVT
        from pyvqnet.dtype import float_dtype_to_complex_dtype,kfloat64
        import numpy as np
        from pyvqnet import QTensor

        A = QTensor([[0.1, 0.2], [0.3, 0.4]])
        angles = QTensor([0.1, 0.2, 0.3])
        qm = QMachine(4,dtype=float_dtype_to_complex_dtype(A.dtype))
        qm.reset_states(1)
        qf = VQC_QSVT(A,angles,wires=[2,1,3])
        z1 = qf(qm)
        print(z1)
 
    """
    A: Incomplete
    angles: Incomplete
    wires: Incomplete
    def __init__(self, A, angles, wires) -> None: ...
    def compute_matrix(self): ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine):
        """
        :param q_machine: vqc quantum machine simulator.
        """
