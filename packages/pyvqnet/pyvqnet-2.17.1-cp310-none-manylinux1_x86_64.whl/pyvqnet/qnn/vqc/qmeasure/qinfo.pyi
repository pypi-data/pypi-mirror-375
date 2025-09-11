from .... import tensor as tensor
from ..qop import Observable as Observable
from ..utils.utils import COMPLEX_2_FLOAT as COMPLEX_2_FLOAT, check_same_device as check_same_device, check_same_dtype as check_same_dtype
from functools import reduce as reduce, wraps as wraps
from pyvqnet.dtype import C_DTYPE as C_DTYPE, dtype_map_from_numpy as dtype_map_from_numpy, kint64 as kint64
from pyvqnet.nn import Module as Module

def vqc_purity(state, qubits_idx, num_wires):
    """
    Computes the purity from a state vector.

    .. math::
        \\gamma = \text{Tr}(\rho^2)

    where :math:`\rho` is the density matrix. The purity of a normalized quantum state satisfies
    :math:`\x0crac{1}{d} \\leq \\gamma \\leq 1`, where :math:`d` is the dimension of the Hilbert space.
    A pure state has a purity of 1.

    :param state: quantum state from pyqpanda get_qstate()
    :param qubits_idx:List of indices in the considered subsystem.
    :param num_wires: number of wires.
    :return:
            purity

    Examples::

        from pyvqnet.qnn.vqc import VQC_Purity, rx, ry, cnot, QMachine
        from pyvqnet.tensor import kfloat64, QTensor
        x = QTensor([[0.7, 0.4], [1.7, 2.4]], requires_grad=True)

        qm = QMachine(3)
        qm.reset_states(2)
        rx(q_machine=qm, wires=0, params=x[:, [0]])
        ry(q_machine=qm, wires=1, params=x[:, [1]])
        ry(q_machine=qm, wires=2, params=x[:, [1]])
        cnot(q_machine=qm, wires=[0, 1])
        cnot(q_machine=qm, wires=[2, 1])
        y = VQC_Purity(qm.states, [0, 1], num_wires=3)
        y.backward()
        print(y)

        # [0.9356751 0.875957 ]
    """
VQC_Purity = vqc_purity

def vqc_partial_trace(state, indices):
    """Compute the partial trace from a state vector.

        :param state: quantum state from QMachine.
        :param indices: - List of indices in the considered subsystem.

        :return: partial trace 
    """
VQC_PartialTrace = vqc_partial_trace

def vqc_meyer_wallach_measure(state):
    """
        Return the values of entanglement capability using meyer-wallach measure.

        :param state: quantum states from QMachine.states
        :return: meyer-wallach measure.
    """
VQC_MeyerWallachMeasure = vqc_meyer_wallach_measure

def vqc_var_measure(q_machine, obs):
    """
    Compute the Variance of the supplied observable from a q_machine.

    :param q_machine: quantum machine
    :param obs: Measure observables. Currently supports Hadamard, I, PauliX, PauliY, PauliZ Observables.
    :return: variance of q_machine ,size= (batch,1)

    Exmaple::

        from pyvqnet.tensor import QTensor
        from pyvqnet.qnn.vqc import VQC_VarMeasure, rx, cnot, hadamard, QMachine,PauliY

        x = QTensor([[0.5]], requires_grad=True)
        qm = QMachine(3)

        rx(q_machine=qm, wires=0, params=x)

        var_result = VQC_VarMeasure(q_machine= qm, obs=PauliY(wires=0))

        var_result.backward()
        print(var_result)

        # [[0.7701511]]
    """
VQC_VarMeasure = vqc_var_measure

def vqc_densitymatrixfromqstate(state, indices):
    """Compute the density matrix from a state vector.

    :param state: batch state vector. This list should of size ``(batch,2,...2)`` for some integer value ``N``.qstate should start from 000 ->111
    :param indices: - List of indices in the considered subsystem.
    :return: Density matrix of size ``(batch_size, 2**len(indices), 2**len(indices))``

    Example::

        from pyvqnet.qnn.vqc import VQC_DensityMatrixFromQstate,rx,ry,cnot,QMachine
        from pyvqnet.tensor import kfloat64, QTensor
        x = QTensor([[0.7,0.4],[1.7,2.4]],requires_grad=True)

        qm = QMachine(3)
        qm.reset_states(2)
        rx(q_machine=qm,wires=0,params=x[:,[0]])
        ry(q_machine=qm,wires=1,params=x[:,[1]])
        ry(q_machine=qm,wires=2,params=x[:,[1]])
        cnot(q_machine=qm,wires=[0,1])
        cnot(q_machine=qm,wires=[2, 1])
        y = VQC_DensityMatrixFromQstate(qm.states,[0,1])
        print(y)

        # [[[0.8155131+0.j        0.1718155+0.j        0.       +0.0627175j
        #   0.       +0.2976855j]
        #  [0.1718155+0.j        0.0669081+0.j        0.       +0.0244234j
        #   0.       +0.0627175j]
        #  [0.       -0.0627175j 0.       -0.0244234j 0.0089152+0.j
        #   0.0228937+0.j       ]
        #  [0.       -0.2976855j 0.       -0.0627175j 0.0228937+0.j
        #   0.1086637+0.j       ]]
        # 
        # [[0.3362115+0.j        0.1471083+0.j        0.       +0.1674582j
        #   0.       +0.3827205j]
        #  [0.1471083+0.j        0.0993662+0.j        0.       +0.1131119j
        #   0.       +0.1674582j]
        #  [0.       -0.1674582j 0.       -0.1131119j 0.1287589+0.j
        #   0.1906232+0.j       ]
        #  [0.       -0.3827205j 0.       -0.1674582j 0.1906232+0.j
        #   0.4356633+0.j       ]]]   

    """
VQC_DensityMatrixFromQstate = vqc_densitymatrixfromqstate

def vqc_density_matrix(q_machine, indices):
    """Compute the density matrix from a state vector.

    :param q_machine: quantum machine.
    :param indices: - List of indices in the considered subsystem.
    :return: Density matrix of size ``(2**len(indices), 2**len(indices))``

    Example::

        from pyvqnet.qnn.vqc import VQC_DensityMatrixFromQstate,rx,ry,cnot,QMachine
        from pyvqnet.tensor import kfloat64, QTensor
        x = QTensor([[0.7,0.4],[1.7,2.4]],requires_grad=True)

        qm = QMachine(3)
        qm.reset_states(2)
        rx(q_machine=qm,wires=0,params=x[:,[0]])
        ry(q_machine=qm,wires=1,params=x[:,[1]])
        ry(q_machine=qm,wires=2,params=x[:,[1]])
        cnot(q_machine=qm,wires=[0,1])
        cnot(q_machine=qm,wires=[2, 1])
        y = VQC_DensityMatrix(qm,[0,1])

    """
VQC_DensityMatrix = vqc_density_matrix

def vqc_mutal_info(q_machine, indices0, indices1, base=None):
    """Compute the mutual information between two subsystems given a state:

    .. math::

        I(A, B) = S(\\rho^A) + S(\\rho^B) - S(\\rho^{AB})

    where :math:`S` is the von Neumann entropy.

    The mutual information is a measure of correlation between two subsystems.
    More specifically, it quantifies the amount of information obtained about
    one system by measuring the other system.

    Each state can be given as a state vector in the computational basis, or
    as a density matrix.

    :param q_machine: quantum machine.
    :param indices0: - List of indices in the first subsystem.
    :param indices1: - List of indices in the second subsystem.
    :param base: Base for the logarithm. If None, the natural logarithm is used.

    :return: Mutual information between the subsystems

    Example::


    """
VQC_Mutal_Info = vqc_mutal_info

def vqc_vn_entropy(q_machine, indices, base=None):
    """Compute the Von Neumann entropy from a state vector or density matrix on a given qubits list.

    .. math::
        S( \\rho ) = -\\text{Tr}( \\rho \\log ( \\rho ))

    :param q_machine: quantum machine.
    :param indices: - List of indices in the considered subsystem.
    :param base: Base for the logarithm. If None, the natural logarithm is used.

    :return: float value of  Von Neumann entropy

    Example::

        from pyvqnet.qnn.vqc import VQC_VN_Entropy, rx, ry, cnot, QMachine
        from pyvqnet.tensor import kfloat64, QTensor

        x = QTensor([[0.2, 0.4], [1.7, 2.4]], requires_grad=True)

        qm = QMachine(3)
        qm.reset_states(2)
        rx(q_machine=qm, wires=0, params=x[:, [0]])
        ry(q_machine=qm, wires=1, params=x[:, [1]])
        ry(q_machine=qm, wires=2, params=x[:, [1]])
        cnot(q_machine=qm, wires=[0, 1])
        cnot(q_machine=qm, wires=[2, 1])
        y = VQC_VN_Entropy(qm, [0, 2])

    """
VQC_VN_Entropy = vqc_vn_entropy
