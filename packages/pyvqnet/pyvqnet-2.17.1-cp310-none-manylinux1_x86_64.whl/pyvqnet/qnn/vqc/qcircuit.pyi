from ...backends import check_not_default_backend as check_not_default_backend, global_backend as global_backend
from ...device import DEV_CPU as DEV_CPU
from ...dtype import C_DTYPE as C_DTYPE, D_DTYPE as D_DTYPE, F_DTYPE as F_DTYPE, HC_DTYPE as HC_DTYPE, Z_DTYPE as Z_DTYPE, complex_dtype_to_float_dtype as complex_dtype_to_float_dtype, float_dtype_to_complex_dtype as float_dtype_to_complex_dtype, kcomplex128 as kcomplex128, kcomplex32 as kcomplex32, kcomplex64 as kcomplex64, kfloat16 as kfloat16, kfloat32 as kfloat32, kfloat64 as kfloat64, may_be_c_dtype as may_be_c_dtype, may_be_hc_dtype as may_be_hc_dtype, may_be_z_dtype as may_be_z_dtype, vqnet_complex_dtypes as vqnet_complex_dtypes, vqnet_float_dtypes as vqnet_float_dtypes
from ...nn import Module as Module, ModuleList as ModuleList
from ...tensor import QTensor as QTensor, no_grad as no_grad, tensor as tensor, to_tensor as to_tensor
from ...types import _generic_wires_type, _multi_wires_type
from .qmachine import QMachine as QMachine
from .qmatrix import basic_state_projector_matrix as basic_state_projector_matrix, ccz_matrix as ccz_matrix, ch_matrix as ch_matrix, cnot_matrix as cnot_matrix, controlledphaseshift_matrix as controlledphaseshift_matrix, crot_matrix as crot_matrix, crx_matrix as crx_matrix, cry_matrix as cry_matrix, crz_matrix as crz_matrix, cswap_matrix as cswap_matrix, cu1_matrix as cu1_matrix, cy_matrix as cy_matrix, cz_matrix as cz_matrix, double_excitation_matrix as double_excitation_matrix, double_mat_dict as double_mat_dict, float_mat_dict as float_mat_dict, hadamard_matrix as hadamard_matrix, half_float_mat_dict as half_float_mat_dict, identity_matrix as identity_matrix, isingxx_matrix as isingxx_matrix, isingxy_matrix as isingxy_matrix, isingyy_matrix as isingyy_matrix, isingzz_matrix as isingzz_matrix, iswap_matrix as iswap_matrix, multirz_matrix as multirz_matrix, paulix_matrix as paulix_matrix, pauliy_matrix as pauliy_matrix, pauliz_matrix as pauliz_matrix, phaseshift_matrix as phaseshift_matrix, rot_matrix as rot_matrix, rx_matrix as rx_matrix, rxx_matrix as rxx_matrix, ry_matrix as ry_matrix, ryy_matrix as ryy_matrix, rz_matrix as rz_matrix, rzx_matrix as rzx_matrix, rzz_matrix as rzz_matrix, s_matrix as s_matrix, sdg_matrix as sdg_matrix, single_excitation_matrix as single_excitation_matrix, swap_matrix as swap_matrix, t_matrix as t_matrix, tdg_matrix as tdg_matrix, toffoli_matrix as toffoli_matrix, u1_matrix as u1_matrix, u2_matrix as u2_matrix, u3_matrix as u3_matrix, x1_matrix as x1_matrix, y1_matrix as y1_matrix, z1_matrix as z1_matrix
from .qop import DiagonalOperation as DiagonalOperation, Observable as Observable, Operation as Operation, Operator as Operator, QModule as QModule, StateEncoder as StateEncoder
from .utils import expand_matrix as expand_matrix
from .utils.parser import OriginIR_BaseParser as OriginIR_BaseParser
from .utils.utils import CNOT_BLOCK_SIZE as CNOT_BLOCK_SIZE, all_wires as all_wires, apply_diagonal_unitary as apply_diagonal_unitary, apply_gate_operation_impl as apply_gate_operation_impl, check_same_device as check_same_device, check_wires as check_wires, check_wires_valid as check_wires_valid, create_op_originir as create_op_originir, get_prod_mat as get_prod_mat, max_wires_for_diagonal_unitary as max_wires_for_diagonal_unitary, maybe_reshape_param_to_valid as maybe_reshape_param_to_valid, op_name_dict as op_name_dict, qgate_op_creator as qgate_op_creator, save_op_history as save_op_history
from _typeshed import Incomplete
from abc import ABCMeta
from enum import IntEnum
from functools import lru_cache
from typing import Callable

class WiresEnum(IntEnum):
    """Integer enumeration class
    to represent the number of wires
    an operation acts on"""
    AnyWires = -1
    AllWires = -2

AnyWires: Incomplete
special_ops_name: Incomplete

def qft(qmachine, wires, mat=None, use_dagger: bool = False) -> None:
    """
    qft function
    """
def unitary(q_machine: QMachine, wires: _generic_wires_type, mat, use_dagger: bool = False):
    """
    arbitrary unitary matrix function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param mat: unitary to apply.

    :param use_dagger: if use dagger, default: False.
    """

class QUnitary(Operation, metaclass=ABCMeta):
    num_params: int
    num_wires = AnyWires
    func: Incomplete

def cy(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    cy gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.
    :param use_dagger: if use dagger, default: False.

    Example::

        # from pyvqnet.qnn.vqc import cy,QMachine
        # qm = QMachine(4)
        # cy(q_machine=qm,wires=(1,0))

    """
def i(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    i gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.
    :param use_dagger: if use dagger, default: False.

    Example::

        # from pyvqnet.qnn.vqc import i,QMachine
        # qm = QMachine(4)
        # i(q_machine=qm,wires=1)
        # print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]

        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]


        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]

        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def pauliz(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    pauliz gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        qm = QMachine(4)
        vqc.pauliz(q_machine=qm,wires=1)
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def hadamard(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    hadamard gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        qm = QMachine(4)
        vqc.hadamard(q_machine=qm,wires=1)
        print(qm.states)

        # [[[[[0.7071068+0.j 0.       +0.j]
        #     [0.       +0.j 0.       +0.j]]
        # 
        #    [[0.7071068+0.j 0.       +0.j]
        #     [0.       +0.j 0.       +0.j]]]
        # 
        # 
        #   [[[0.       +0.j 0.       +0.j]
        #     [0.       +0.j 0.       +0.j]]
        # 
        #    [[0.       +0.j 0.       +0.j]
        #     [0.       +0.j 0.       +0.j]]]]]
    """
def x(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    x gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        qm = QMachine(4)
        vqc.x(q_machine=qm,wires=1)
        print(qm.states)
    """
def paulix(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    paulix gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        qm = QMachine(4)
        vqc.paulix(q_machine=qm,wires=1)
        print(qm.states)

        # [[[[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def rx(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    rotate x gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.rx(q_machine=qm,wires=1, params=QTensor([0.5]))
        print(qm.states)

        # [[[[[0.9689124+0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]
        # 
        #    [[0.       -0.247404j 0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]]
        # 
        # 
        #   [[[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]
        # 
        #    [[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]]]]
    """
def s(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    s gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.s(q_machine=qm,wires=1)
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]       
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def ry(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    rotate y gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.ry(q_machine=qm,wires=1, params=QTensor([0.5]))
        print(qm.states)

        # [[[[[0.9689124+0.j 0.       +0.j]
        #     [0.       +0.j 0.       +0.j]]
        # 
        #    [[0.247404 +0.j 0.       +0.j]
        #     [0.       +0.j 0.       +0.j]]]
        # 
        # 
        #   [[[0.       +0.j 0.       +0.j]
        #     [0.       +0.j 0.       +0.j]]
        # 
        #    [[0.       +0.j 0.       +0.j]
        #     [0.       +0.j 0.       +0.j]]]]]
    """
def rz_eigvals(theta=None): ...
def rz(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    rotate y gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.rz(q_machine=qm,wires=1, params=QTensor([0.5]))
        print(qm.states)

        # [[[[[0.9689124-0.247404j 0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]
        # 
        #    [[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]]
        # 
        # 
        #   [[[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]
        # 
        #    [[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]]]]
    """
def cry(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    controlled-rotate y gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.cry(q_machine=qm,wires=[0,2], params=QTensor([0.5]))
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def crz(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    controlled-rotate x gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.crz(q_machine=qm,wires=[0,2], params=QTensor([0.5]))
        print(qm.states)
        
        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def multi_control_rz(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False): ...
def crx(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    controlled-rotate x gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.crx(q_machine=qm,wires=[0,2], params=QTensor([0.5]))
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def rxx(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    rotate xx gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.rxx(q_machine=qm,wires=[1,0],params= QTensor([0.2]))
        print(qm.states)

        # [[[[[0.9950042+0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]
        # 
        # 
        #   [[[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.       -0.0998334j 0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]]]
    """
def ryy(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    rotate yy gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.ryy(q_machine=qm,wires=[1,0],params= QTensor([0.2]))
        print(qm.states)

        # [[[[[0.9950042+0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]
        # 
        # 
        #   [[[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.       +0.0998334j 0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]]]
    """
def rzz(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    rotate zz gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.rzz(q_machine=qm,wires=[1,0],params= QTensor([0.2]))
        print(qm.states)

        # [[[[[0.9950042-0.0998334j 0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]
        # 
        # 
        #   [[[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]]]
    """
def rzx(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    rotate zx gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.rzx(q_machine=qm,wires=[1,0],params= QTensor([0.2]))
        print(qm.states)

        # [[[[[0.9950042+0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]
        # 
        # 
        #   [[[0.       -0.0998334j 0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]]]
    """
def pauliy(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    pauli y gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        qm = QMachine(4)
        vqc.pauliy(q_machine=qm,wires=1)
        print(qm.states)

        # [[[[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+1.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]

    """
def ring_cnot(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False): ...
def cnot(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    cnot gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.cnot(q_machine=qm,wires=[1,0])
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def x1(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    x1 function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.x1(q_machine=qm,wires=2)
        print(qm.states)

        # [[[[[0.7071068+0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.       -0.7071068j 0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]
        # 
        # 
        #   [[[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]]]
    """
def y1(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    y1 gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.y1(q_machine=qm,wires=2)
        print(qm.states)

        # [[[[[0.7071068+0.j 0.       +0.j]
        #     [0.       +0.j 0.       +0.j]]
        # 
        #    [[0.7071068+0.j 0.       +0.j]
        #     [0.       +0.j 0.       +0.j]]]
        # 
        # 
        #   [[[0.       +0.j 0.       +0.j]
        #     [0.       +0.j 0.       +0.j]]
        # 
        #    [[0.       +0.j 0.       +0.j]
        #     [0.       +0.j 0.       +0.j]]]]]
    """
def z1(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    z1 gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.z1(q_machine=qm,wires=2)
        print(qm.states)

        # [[[[[0.7071068-0.7071068j 0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]
        # 
        # 
        #   [[[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]]]
    """
def t(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    t gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.t(q_machine=qm,wires=2)
        print(qm.states)

         # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]       
    """
def swap(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    swap gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.swap(q_machine=qm,wires=[1,0])
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def p(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    p gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.p(q_machine=qm,wires=1,params= QTensor([24.0]))
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def u1(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    u1 gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.u1(q_machine=qm,wires=1, params= QTensor([24.0]))
        print(qm.states)

        # [[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]
    """
def u2(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    u2 gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, should be size of (batch,2), default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.u2(q_machine=qm,wires=1, params= QTensor([[24.0,-3]]))
        print(qm.states)

        # [[[[[0.7071068+0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.2999398-0.6403406j 0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]
        # 
        # 
        #   [[[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]]]
    """
def u3(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    u3 gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate should be size of (batch,3) QTensor, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.u3(q_machine=qm,wires=1, params= QTensor([[24.0,-3,1]]))
        print(qm.states)

        # [[[[[0.843854 +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.5312032+0.0757212j 0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]
        # 
        # 
        #   [[[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]
        # 
        #    [[0.       +0.j        0.       +0.j       ]
        #     [0.       +0.j        0.       +0.j       ]]]]]
    """
def rot(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    rot gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate should be size of (batch,3) QTensor, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.rot(q_machine=qm,wires=1, params= QTensor([[24.0,-3,1,2]]))
        print(qm.states)


    """
def cr(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    cr gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.cr(q_machine=qm,wires=[0,1],params= QTensor([1.2]))
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def cz(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    control z gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        qm = QMachine(4)
        vqc.cz(q_machine=qm,wires=[0,2])
        print(qm.states)
        # [[[[[1.+0.j,0.+0.j],
        #     [0.+0.j,0.+0.j]],

        #    [[0.+0.j,0.+0.j],
        #     [0.+0.j,0.+0.j]]],


        #   [[[0.+0.j,0.+0.j],
        #     [0.+0.j,0.+0.j]],

        #    [[0.+0.j,0.+0.j],
        #     [0.+0.j,0.+0.j]]]]]
    """
def cswap(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    control swap gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.cswap(q_machine=qm,wires=[0,1,2])
        print(qm.states)

    """
def toffoli(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    toffoli gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.cz(q_machine=qm,wires=[0,1,2])
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def iswap(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    iswap gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::
    
        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.iswap(q_machine=qm,wires=[0,1])
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def isingxx(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    isingxx gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::
    
        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.isingxx(q_machine=qm,wires=[0,1], params = QTensor([0.5]))
        print(qm.states)

        # [[[[[0.9689124+0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]
        # 
        #    [[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]]
        # 
        # 
        #   [[[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]
        # 
        #    [[0.       -0.247404j 0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]]]]
    """
def isingyy(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    isingyy gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::
    
        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.isingyy(q_machine=qm,wires=[0,1], params = QTensor([0.5]))
        print(qm.states)

        # [[[[[0.9689124+0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]
        # 
        #    [[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]]
        # 
        # 
        #   [[[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]
        # 
        #    [[0.       +0.247404j 0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]]]]
    """
def isingzz(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    isingzz gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::
    
        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.isingzz(q_machine=qm,wires=[0,1], params = QTensor([0.5]))
        print(qm.states)

        # [[[[[0.9689124-0.247404j 0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]
        # 
        #    [[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]]
        # 
        # 
        #   [[[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]
        # 
        #    [[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]]]]
    """
def isingxy(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    isingxy gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::
    
        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.isingxy(q_machine=qm,wires=[0,1], params = QTensor([0.5]))
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def phaseshift(q_machine, wires, params=None, use_dagger: bool = False) -> None:
    """
    phaseshift gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.
    :param use_dagger: if use dagger, default: False.

    Example::
    
        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.phaseshift(q_machine=qm,wires=[0], params = QTensor([0.5]))
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def multirz(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    multirz gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::
    
        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.multirz(q_machine=qm,wires=[0, 1], params = QTensor([0.5]))
        print(qm.states)

        # [[[[[0.9689124-0.247404j 0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]
        # 
        #    [[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]]
        # 
        # 
        #   [[[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]
        # 
        #    [[0.       +0.j       0.       +0.j      ]
        #     [0.       +0.j       0.       +0.j      ]]]]]
    """
def sdg(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    sdg gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::
    
        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.sdg(q_machine=qm,wires=[0])
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def tdg(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False):
    """
    tdg gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::
    
        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.tdg(q_machine=qm,wires=[0])
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def controlledphaseshift(q_machine, wires, params=None, use_dagger: bool = False) -> None:
    """
    controlledphaseshift gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.

    :param use_dagger: if use dagger, default: False.

    Example::
    
        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        for i in range(4):
            vqc.hadamard(q_machine=qm, wires=i)
        vqc.controlledphaseshift(q_machine=qm,params=QTensor([0.5]),wires=[0,1])
        print(qm.states)

        # [[[[[0.25     +0.j        0.25     +0.j       ]
        #     [0.25     +0.j        0.25     +0.j       ]]
        # 
        #    [[0.25     +0.j        0.25     +0.j       ]
        #     [0.25     +0.j        0.25     +0.j       ]]]
        # 
        # 
        #   [[[0.25     +0.j        0.25     +0.j       ]
        #     [0.25     +0.j        0.25     +0.j       ]]
        # 
        #    [[0.2193956+0.1198564j 0.2193956+0.1198564j]
        #     [0.2193956+0.1198564j 0.2193956+0.1198564j]]]]]
    """
def single_excitation(q_machine: QMachine, wires: _generic_wires_type, params, use_dagger: bool = False):
    """
    single_excitation gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate,should be 1d or [*,1] QTensor.
    :param use_dagger: if use dagger, default: False.

    Example::
    
        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        vqc.single_excitation(q_machine=qm, wires=[0, 1], params=QTensor([0.5]))
        print(qm.states)

        # [[[[[1.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]
        # 
        # 
        #   [[[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]
        # 
        #    [[0.+0.j 0.+0.j]
        #     [0.+0.j 0.+0.j]]]]]
    """
def double_excitation(q_machine: QMachine, wires: _generic_wires_type, params, use_dagger: bool = False):
    """
    double_excitation gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to, should have 4 wires. 
    :param params: parameters for this gate,should be 1d or [*,1] QTensor.
    :param use_dagger: if use dagger, default: False.

    Example::
    
        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        for i in range(4):
            vqc.hadamard(q_machine=qm, wires=i)
        vqc.isingzz(q_machine=qm, params=QTensor([0.55]), wires=[1,0])
        vqc.double_excitation(q_machine=qm, params=QTensor([0.55]), wires=[0,1,2,3])
        print(qm.states)

        # [[[[[0.2406063-0.0678867j 0.2406063-0.0678867j]
        #     [0.2406063-0.0678867j 0.1662296-0.0469015j]]
        # 
        #    [[0.2406063+0.0678867j 0.2406063+0.0678867j]
        #     [0.2406063+0.0678867j 0.2406063+0.0678867j]]]
        # 
        # 
        #   [[[0.2406063+0.0678867j 0.2406063+0.0678867j]
        #     [0.2406063+0.0678867j 0.2406063+0.0678867j]]
        # 
        #    [[0.2969014-0.0837703j 0.2406063-0.0678867j]
        #     [0.2406063-0.0678867j 0.2406063-0.0678867j]]]]]
    """
def multicontrolledx(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False, control_values: list[int] | None = None):
    """
    multi-controlled x gate function.

    :param q_machine: quantum machine defined by pyvqnet.qnn.vqc.QMachine.
    :param wires: the qubits applied to. 
    :param params: parameters for this gate, default: None.
    :param use_dagger: if use dagger, default: False.
    :param control_values: control values, default: None.


    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor
        qm = QMachine(4)
        for i in range(4):
            vqc.hadamard(q_machine=qm, wires=i)
        vqc.phaseshift(q_machine=qm,wires=[0], params = QTensor([0.5]))
        vqc.phaseshift(q_machine=qm,wires=[1], params = QTensor([2]))
        vqc.phaseshift(q_machine=qm,wires=[3], params = QTensor([3]))
        vqc.multicontrolledx(qm, wires=[0, 1, 3, 2])
        print(qm.states)

        # [[[[[ 0.25     +0.j       ,-0.2474981+0.03528j  ],
        #     [ 0.25     +0.j       ,-0.2474981+0.03528j  ]],

        #    [[-0.1040367+0.2273243j, 0.0709155-0.239731j ],
        #     [-0.1040367+0.2273243j, 0.0709155-0.239731j ]]],


        #   [[[ 0.2193956+0.1198564j,-0.2341141-0.0876958j],
        #     [ 0.2193956+0.1198564j,-0.2341141-0.0876958j]],

        #    [[-0.2002859+0.149618j , 0.1771674-0.176385j ],
        #     [-0.2002859+0.149618j , 0.1771674-0.176385j ]]]]]


    """
def adjoint_gen_helper(gen, use_dagger): ...

class MultiControlledX(Operation, metaclass=ABCMeta):
    """Class for MultiControlledX Gate.
    
    
    Example::

        from pyvqnet.qnn.vqc import QMachine
        import pyvqnet.qnn.vqc as vqc
        from pyvqnet.tensor import QTensor,kcomplex64
        #pyvqnet
        qm = QMachine(4,dtype=kcomplex64)
        qm.reset_states(2)
        for i in range(4):
            vqc.hadamard(q_machine=qm, wires=i)
        vqc.isingzz(q_machine=qm, params=QTensor([0.25]), wires=[1,0])
        vqc.double_excitation(q_machine=qm, params=QTensor([0.55]), wires=[0,1,2,3])

        mcx = vqc.MultiControlledX( 
                        init_params=None,
                        wires=[2,3,0,1],
                        dtype=kcomplex64,
                        use_dagger=False,control_values=[1,0,0])
        y = mcx(q_machine = qm)
        print(qm.states.flatten())
        sss = qm.states.flatten().to_numpy()
        import numpy as np
        assert np.allclose([0.24804942-0.03116868j, 0.24804942-0.03116868j, 0.24804942+0.03116868j,
                            0.17137195-0.02153377j, 0.24804942+0.03116868j, 0.24804942+0.03116868j,
                            0.24804942-0.03116868j, 0.24804942+0.03116868j, 0.24804942+0.03116868j,
                            0.24804942+0.03116868j, 0.24804942+0.03116868j, 0.24804942+0.03116868j,
                            0.30608607-0.03846129j, 0.24804942-0.03116868j, 0.24804942-0.03116868j,
                            0.24804942-0.03116868j,0.24804942-0.03116868j, 0.24804942-0.03116868j, 0.24804942+0.03116868j,
                            0.17137195-0.02153377j, 0.24804942+0.03116868j, 0.24804942+0.03116868j,
                            0.24804942-0.03116868j, 0.24804942+0.03116868j, 0.24804942+0.03116868j,
                            0.24804942+0.03116868j, 0.24804942+0.03116868j, 0.24804942+0.03116868j,
                            0.30608607-0.03846129j, 0.24804942-0.03116868j, 0.24804942-0.03116868j,
                            0.24804942-0.03116868j],sss)

    """
    num_params: int
    num_wires = AnyWires
    basis: str
    func: Incomplete
    @property
    def control_wires(self): ...

class ExpressiveEntanglingAnsatz(Module):
    '''
    19 different ansatzes from paper: https://arxiv.org/pdf/1905.10876.pdf.

    :param type: circuit type from 1 to 19.
    :param num_wires: number of wires.
    :param depth: circuit depth.
    :param dtype: data type for the paramters, default:None
    :param name: name
    :return:
        a ExpressiveEntanglingAnsatz instance

    Example::

        from pyvqnet.qnn.vqc  import *
        import pyvqnet
        pyvqnet.utils.set_random_seed(42)
        from pyvqnet.nn import Module
        class QModel(Module):
            def __init__(self, num_wires, dtype,grad_mode=""):
                super(QModel, self).__init__()

                self._num_wires = num_wires
                self._dtype = dtype
                self.qm = QMachine(num_wires, dtype=dtype,grad_mode=grad_mode,save_ir=True)
                self.c1 = ExpressiveEntanglingAnsatz(13,3,2)
                self.measure = MeasureAll(obs={
                    "Z1":1
                })

            def forward(self, x, *args, **kwargs):
                self.qm.reset_states(x.shape[0])
                self.c1(q_machine = self.qm)
                rlt = self.measure(q_machine=self.qm)
                return rlt
            

        input_x = tensor.QTensor([[0.1, 0.2, 0.3]])

        #input_x = tensor.broadcast_to(input_x,[2,3])

        input_x.requires_grad = True

        qunatum_model = QModel(num_wires=3, dtype=pyvqnet.kcomplex64)

        batch_y = qunatum_model(input_x)
        z = vqc_to_originir_list(qunatum_model)
        for zi in z:
            print(zi)
        batch_y.backward()
        print(batch_y)

    '''
    model: Incomplete
    def __init__(self, type: int, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...
    def __call__(self, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_1(Module):
    """
    Circuit 1  from https://arxiv.org/pdf/1905.10876.pdf,
    has depth*num_wires*2 parameters.

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_2(Module):
    """
    Circuit 2  from https://arxiv.org/pdf/1905.10876.pdf,
    has depth*num_wires*2 parameters.

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_3(Module):
    """
    Circuit 3  from https://arxiv.org/pdf/1905.10876.pdf,
    has depth*(num_wires*3-1) parameters.

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_4(Module):
    """
    Circuit 4  from https://arxiv.org/pdf/1905.10876.pdf,
    has depth*(num_wires*3-1) parameters.

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_5(Module):
    """
    Circuit 5  from https://arxiv.org/pdf/1905.10876.pdf,
    has depth*(num_wires*(num_wires-1+4)) parameters.

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_6(Module):
    """
    Circuit 6  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_7(Module):
    """
    Circuit 7  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_8(Module):
    """
    Circuit 8  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_9(Module):
    """
    Circuit 9  from https://arxiv.org/pdf/1905.10876.pdf,


    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_10(Module):
    """
    Circuit 10  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_11(Module):
    """
    Circuit 11  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_12(Module):
    """
    Circuit 12  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_13(Module):
    """
    Circuit 13  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_14(Module):
    """
    Circuit 14  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_15(Module):
    """
    Circuit 15  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_16(Module):
    """
    Circuit 16  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_17(Module):
    """
    Circuit 17  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_18(Module):
    """
    Circuit 18  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

class ExpressiveEntanglingAnsatz_19(Module):
    """
    Circuit 19  from https://arxiv.org/pdf/1905.10876.pdf,

    """
    depth: Incomplete
    num_wires: Incomplete
    def __init__(self, num_wires: int, depth: int, dtype=None, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine, *args, **kwargs): ...

def basic_state_projector(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False): ...

class Projector(Observable, Operation, metaclass=ABCMeta):
    num_params: int
    num_wires = AnyWires
    func: Incomplete
    def diagonalizing_gates(self): ...

dtype_mat_callable_dict: Incomplete

class T(DiagonalOperation, metaclass=ABCMeta):
    """Class for T Gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete

class iSWAP(Operation, metaclass=ABCMeta):
    """Class for ISWAP gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class IsingXX(DiagonalOperation, metaclass=ABCMeta):
    """Class for IsingXX gate."""
    num_params: int
    num_wires: int
    func: Incomplete
    def generator(self): ...

class IsingYY(DiagonalOperation, metaclass=ABCMeta):
    """Class for IsingYY gate."""
    num_params: int
    num_wires: int
    func: Incomplete
    def generator(self): ...

class IsingZZ(DiagonalOperation, metaclass=ABCMeta):
    """Class for IsingZZ gate."""
    num_params: int
    num_wires: int
    func: Incomplete
    def generator(self): ...

class IsingXY(DiagonalOperation, metaclass=ABCMeta):
    """Class for IsingXY gate."""
    num_params: int
    num_wires: int
    func: Incomplete
    def generator(self): ...

class PhaseShift(DiagonalOperation, metaclass=ABCMeta):
    """Class for PhaseShift gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete
    def generator(self): ...

class MultiRZ(DiagonalOperation, metaclass=ABCMeta):
    """Class for MultiRZ gate."""
    num_params: int
    num_wires = AnyWires
    func: Incomplete
    def generator(self) -> None: ...

class SDG(Operation, metaclass=ABCMeta):
    """Class for SDG Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class TDG(Operation, metaclass=ABCMeta):
    """Class for TDG Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class ControlledPhaseShift(Operation, metaclass=ABCMeta):
    """Class for ControlledPhaseShift Gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete
    @property
    def control_wires(self): ...
    def generator(self) -> None:
        """this op should be decomposed"""

class SingleExcitation(Operation, metaclass=ABCMeta):
    """Class for SingleExcitation Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class DoubleExcitation(Operation, metaclass=ABCMeta):
    """Class for DoubleExcitation Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class CR(DiagonalOperation, metaclass=ABCMeta):
    """Class for CR gate."""
    num_params: int
    num_wires: int
    func: Incomplete
    def generator(self): ...

class U2(Operation, metaclass=ABCMeta):
    """Class for U2 gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class Rot(Operation, metaclass=ABCMeta):
    """Class for Rotation Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class U3(Operation, metaclass=ABCMeta):
    """Class for U3 gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class QFT(Operation, metaclass=ABCMeta):
    num_params: int
    num_wires = AnyWires
    func: Incomplete

class Toffoli(Operation, metaclass=ABCMeta):
    """Class for Toffoli Gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete
    @property
    def control_wires(self): ...

class CSWAP(Operation, metaclass=ABCMeta):
    """Class for CSWAP Gate."""
    num_params: int
    num_wires: int
    func: Incomplete
    @property
    def control_wires(self): ...

class SWAP(Operation, metaclass=ABCMeta):
    """Class for SWAP Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class Hadamard(Observable, metaclass=ABCMeta):
    """Class for Hadamard Gate."""
    num_params: int
    num_wires: int
    func: Incomplete
    def diagonalizing_gates(self): ...

class CNOT(Operation, metaclass=ABCMeta):
    """Class for CNOT Gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete
    @property
    def control_wires(self): ...

def ring_cnot_mat_and_wires(wires, dtype, device): ...

class RING_CNOT(Operation, metaclass=ABCMeta):
    num_params: int
    num_wires = AnyWires
    basis: str
    func: Incomplete

class I(Observable, metaclass=ABCMeta):
    """Class for Identity Gate."""
    num_params: int
    num_wires: int
    func: Incomplete
    def __eq__(self, other): ...
    def __hash__(self): ...
    def diagonalizing_gates(self): ...

class RX(Operation, metaclass=ABCMeta):
    """Class for RX Gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete
    def generator(self): ...

class RY(Operation, metaclass=ABCMeta):
    """Class for RY Gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete
    def generator(self): ...

class RZ(DiagonalOperation, metaclass=ABCMeta):
    """Class for RZ Gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete
    def generator(self): ...

class CRX(Operation, metaclass=ABCMeta):
    """Class for Controlled Rotation X gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete
    @property
    def control_wires(self): ...

class CRY(Operation, metaclass=ABCMeta):
    """Class for Controlled Rotation Y gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete
    @property
    def control_wires(self): ...

class CRZ(Operation, metaclass=ABCMeta):
    """Class for Controlled Rotation Z gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete
    @property
    def control_wires(self): ...

class RYY(Operation, metaclass=ABCMeta):
    """Class for RYY Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class RZZ(Operation, metaclass=ABCMeta):
    """Class for RZZ Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class RXX(Operation, metaclass=ABCMeta):
    """Class for RXX Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class RZX(Operation, metaclass=ABCMeta):
    """Class for RZX Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class PauliZ(Observable, metaclass=ABCMeta):
    """Class for Pauli Z Gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete
    def __eq__(self, other): ...
    def __hash__(self): ...
    def diagonalizing_gates(self): ...

class PauliX(Observable, metaclass=ABCMeta):
    """Class for Pauli X Gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete
    def __eq__(self, other): ...
    def __hash__(self): ...
    def diagonalizing_gates(self): ...

class PauliY(Observable, metaclass=ABCMeta):
    """Class for Pauli Y Gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete
    def __eq__(self, other): ...
    def __hash__(self): ...
    def diagonalizing_gates(self): ...

class S(DiagonalOperation, metaclass=ABCMeta):
    """Class for S Gate."""
    num_params: int
    num_wires: int
    basis: str
    func: Incomplete

class X1(Operation, metaclass=ABCMeta):
    """Class for X1 Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class Y1(Operation, metaclass=ABCMeta):
    """Class for Y1 Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class Z1(Operation, metaclass=ABCMeta):
    """Class for Y1 Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class U1(DiagonalOperation, metaclass=ABCMeta):
    """Class for U1.
    """
    num_params: int
    num_wires: int
    func: Incomplete
    def generator(self): ...
P = U1

class CZ(DiagonalOperation, metaclass=ABCMeta):
    """Class for CZ Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

class CY(Operation, metaclass=ABCMeta):
    """Class for CY Gate."""
    num_params: int
    num_wires: int
    func: Incomplete
    basis: str

def quantum_gate_op(name: str, mat: Callable | QTensor, q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False, hyper_parameters: dict = {}): ...
def vqc_to_originir_list(vqc_model: Module):
    """
    Convert VQNet vqc module to `originir<https://pyqpanda-toturial.readthedocs.io/zh/latest/9.%E9%87%8F%E5%AD%90%E7%BA%BF%E8%B7%AF%E8%BD%AC%E8%AF%91/index.html>`_
    vqc_model should run forward function before this function to get input data.
    If input data is batched data. It will return with several IR strings for each input.

    :param vqc_model: VQNet vqc module, should run forward first.

    :return: originIR string or list of originIR string.

    """
def originir_to_vqc(originir: str, tmp: str = 'code_tmp.py', verbose: bool = False) -> str:
    '''
    parse originir to vqc model code.
    the code create a vqc Module without `Measure`,return qstates [b,2,...,2] instead.
    the function will return a generate_code file in "./origin_ir_gen_code/" + tmp + ".py"
    
    :param originir: origin ir.
    :param tmp: code file name, default= code_tmp.py.
    :param verbose: if show generate code, default = False
    :return:
        python code.
    
    Example::

        from pyvqnet.qnn.vqc import originir_to_vqc
        ss = "QINIT 3
CREG 3
H q[1]"
        Z = originir_to_vqc(ss,verbose=True)

        exec(Z)
        m =Exported_Model()
        print(m(2))

        # from pyvqnet.nn import Module
        # from pyvqnet.tensor import QTensor
        # from pyvqnet.qnn.vqc import *
        # class Exported_Model(Module):
        #         def __init__(self, name=""):
        #                 super().__init__(name)

        #                 self.q_machine = QMachine(num_wires=3)
        #                 self.H_0 = Hadamard(wires=1, use_dagger = False)

        #         def forward(self, x, *args, **kwargs):
        #                 x = self.H_0(q_machine=self.q_machine)
        #                 return self.q_machine.states

        # [[[[0.7071068+0.j 0.       +0.j]
        #    [0.7071068+0.j 0.       +0.j]]

        #   [[0.       +0.j 0.       +0.j]
        #    [0.       +0.j 0.       +0.j]]]]
    '''

generator_dict: Incomplete
op_controlled_wires_dict: Incomplete

def helper_get_geneartor_from_dict(op: dict): ...
def op_history_to_list(op_history, op_class_dict, use_param_with_autograd: bool = False):
    """
    Load quantum operator history except obs.
    """
def op_history_summary(op_history, num_qubits=None):
    """
    Print summaray infomation for op history generated from vqc forward function
    or compiled vqc modules.

    :param op_history: op history generated from vqc module,when set qmachine set_save_op_history_flag(True).
    :param num_qubits: number of qubits, default: None, use max_wires in op history.
    :return:
        string
    
    """
def summary(vqc_module: Module):
    """
    return summary of a vqc module,including gates numbers and paramters numbers.

    Example::

        from pyvqnet.qnn.vqc import QMachine, RX, RY, CNOT, PauliX, qmatrix, PauliZ,MeasureAll
        from pyvqnet.tensor import QTensor, tensor,kcomplex64
        import pyvqnet
        import numpy as np
        import pyqpanda as pq

        import time

        class QModel(pyvqnet.nn.Module):
            def __init__(self, num_wires, dtype):
                super(QModel, self).__init__()

                self._num_wires = num_wires
                self._dtype = dtype
                self.qm = QMachine(num_wires, dtype=dtype)
                self.rx_layer1 = RX(has_params=True,
                                    trainable=True,
                                    wires=1,
                                    init_params=tensor.QTensor([0.5]))
                self.ry_layer2 = RY(has_params=True,
                                    trainable=True,
                                    wires=0,
                                    init_params=tensor.QTensor([-0.5]))
                self.xlayer = PauliX(wires=0)
                self.cnot = CNOT(wires=[0, 1])
                self.measure = MeasureAll(obs=PauliZ)

            def forward(self, x, *args, **kwargs):
                return super().forward(x, *args, **kwargs)
        Z = QModel(4,kcomplex64)
        from pyvqnet.qnn.vqc import summary
        print(summary(Z))

    """

class VQC_HardwareEfficientAnsatz(QModule):
    '''
    A implementation of Hardware Efficient Ansatz introduced by thesis: Hardware-efficient Variational Quantum Eigensolver for Small Molecules and
    Quantum Magnets https://arxiv.org/pdf/1704.05018.pdf.

    :param n_qubits: Number of qubits.
    :param single_rot_gate_list: A single qubit rotation gate list is constructed by one or several rotation gate that act on every qubit.Currently
    support Rx, Ry, Rz.
    :param entangle_gate: The non parameterized entanglement gate.CNOT,CZ is supported.default:CNOT.
    :param entangle_rules: How entanglement gate is used in the circuit. \'linear\' means the entanglement gate will be act on every neighboring qubits. \'all\' means
            the entanglment gate will be act on any two qbuits. Default:linear.
    :param depth: The depth of ansatz, default:1.
    :param initial: initial one same value for paramaters,default:None,this module will initialize parameters randomly.
    :param dtype: data dtype of parameters.
    :return a VQC_HardwareEfficientAnsatz instance.

    Example::


        from pyvqnet.nn import Module,Linear,ModuleList
        from pyvqnet.qnn.vqc.qcircuit import VQC_HardwareEfficientAnsatz,RZZ,RZ
        from pyvqnet.qnn.vqc import Probability,QMachine
        from pyvqnet import tensor

        class QM(Module):
            def __init__(self, name=""):
                super().__init__(name)
                self.linearx = Linear(4,2)
                self.ansatz = VQC_HardwareEfficientAnsatz(4, ["rx", "RY", "rz"],
                                            entangle_gate="cnot",
                                            entangle_rules="linear",
                                            depth=2)
                self.encode1 = RZ(wires=0)
                self.encode2 = RZ(wires=1)
                self.measure = Probability(wires=[0,2])
                self.device = QMachine(4)
            def forward(self, x, *args, **kwargs):
                self.device.reset_states(x.shape[0])
                y = self.linearx(x)
                self.encode1(params = y[:, [0]],q_machine = self.device,)
                self.encode2(params = y[:, [1]],q_machine = self.device,)
                self.ansatz(q_machine =self.device)
                return self.measure(q_machine =self.device)

        bz =3
        inputx = tensor.arange(1.0,bz*4+1).reshape([bz,4])
        inputx.requires_grad= True
        qlayer = QM()
        y = qlayer(inputx)
        y.backward()
        print(y)

        # [[0.3075959 0.2315064 0.2491432 0.2117545]
        #  [0.3075958 0.2315062 0.2491433 0.2117546]
        #  [0.3075958 0.2315062 0.2491432 0.2117545]]
    '''
    n_qubits: Incomplete
    qcir: Incomplete
    dtype: Incomplete
    def __init__(self, n_qubits, single_rot_gate_list, entangle_gate: str = 'CNOT', entangle_rules: str = 'linear', depth: int = 1, initial=None, dtype: int | None = ...) -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine: QMachine): ...
    def create_ansatz(self, initial, dtype):
        """
        create ansatz use weights in parameterized gates
        :param weights: varational parameters in the ansatz.
        :return: a pyqpanda Hardware Efficient Ansatz instance .
    
        """

class VQC_BasicEntanglerTemplate(QModule):
    '''
    Layers consisting of one-parameter single-qubit rotations on each qubit, followed by a closed chain or *ring* of
     CNOT gates.
     
    The ring of CNOT gates connects every qubit with its neighbour, with the last qubit being considered as a neighbour to the first qubit.


    :param num_layers: number of repeat layers, default: 1.
    :param num_qubits: number of qubits, default: 1.
    :param rotation: one-parameter single-qubit gate to use, default: `RX`
    :param initial: initialized same value for all paramters. default:None,parameters will be initialized randomly.
    :param dtype: data type of parameter, default:None,use float32.
    :return: A VQC_BasicEntanglerTemplate instance

    Example::

    
        from pyvqnet.nn import Module, Linear, ModuleList
        from pyvqnet.qnn.vqc.qcircuit import BasicEntanglerTemplate, RZZ, RZ
        from pyvqnet.qnn.vqc import Probability, QMachine
        from pyvqnet import tensor


        class QM(Module):
            def __init__(self, name=""):
                super().__init__(name)

                self.ansatz = BasicEntanglerTemplate(2,
                                                    4,
                                                    "rz",
                                                    initial=tensor.ones([1, 1]))

                self.measure = Probability(wires=[0, 2])
                self.device = QMachine(4)

            def forward(self,x, *args, **kwargs):

                self.ansatz(q_machine=self.device)
                return self.measure(q_machine=self.device)

        bz = 1
        inputx = tensor.arange(1.0, bz * 4 + 1).reshape([bz, 4])
        qlayer = QM()
        y = qlayer(inputx)
        y.backward()
        print(y)

        # [[1.0000002 0.        0.        0.       ]]
    '''
    n_layers: Incomplete
    num_qubits: Incomplete
    rotation: Incomplete
    vqc: Incomplete
    def __init__(self, num_layers: int = 1, num_qubits: int = 1, rotation: str = 'RX', initial=None, dtype: int | None = None) -> None: ...
    def Rot(self, gate, initial, dtype):
        """
        :param qubits: quantum bits

        :return: quantum circuit
        """
    def create_circuit(self, initial, dtype): ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine): ...

class VQC_StronglyEntanglingTemplate(QModule):
    '''
    Layers consisting of single qubit rotations and entanglers, inspired by the `circuit-centric classifier design
     <https://arxiv.org/abs/1804.00633>`__ .


    :param num_layers: number of repeat layers, default: 1.
    :param num_qubits: number of qubits, default: 1.
    :param ranges: sequence determining the range hyperparameter for each subsequent layer; default: None
                                using :math: `r=l \\mod M` for the :math:`l` th layer and :math:`M` qubits.
    :param initial: initial value for all parameters.default: None,initialized randomly.
    :param dtype: data type of parameter, default:None,use float32.

    Example::

        from pyvqnet.nn import Module
        from pyvqnet.qnn.vqc.qcircuit import VQC_StronglyEntanglingTemplate
        from pyvqnet.qnn.vqc import Probability, QMachine
        from pyvqnet import tensor


        class QM(Module):
            def __init__(self, name=""):
                super().__init__(name)

                self.ansatz = VQC_StronglyEntanglingTemplate(2,
                                                    4,
                                                    None,
                                                    initial=tensor.ones([1, 1]))

                self.measure = Probability(wires=[0, 1])
                self.device = QMachine(4)

            def forward(self,x, *args, **kwargs):

                self.ansatz(q_machine=self.device)
                return self.measure(q_machine=self.device)

        bz = 1
        inputx = tensor.arange(1.0, bz * 4 + 1).reshape([bz, 4])
        qlayer = QM()
        y = qlayer(inputx)
        y.backward()
        print(y)

        # [[0.3745951 0.154298  0.059156  0.4119509]]
    '''
    n_layers: Incomplete
    num_qubits: Incomplete
    ranges: Incomplete
    imprimitive: Incomplete
    vqc: Incomplete
    dtype: Incomplete
    def __init__(self, num_layers: int = 1, num_qubits: int = 1, ranges: list | None = None, initial=None, dtype: int | None = None) -> None: ...
    def Rot(self, l, initial, dtype): ...
    def create_circuit(self, initial, dtype): ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine): ...

class VQC_QuantumEmbedding(QModule):
    '''
    use RZ,RY,RZ to create a Variational Quantum Circuit to encode classic data into quantum state.

    Quantum embeddings for machine learning
    Seth Lloyd, Maria Schuld, Aroosa Ijaz, Josh Izaac, Nathan Killoran
    https://arxiv.org/abs/2001.03622

    :param num_repetitions_input: number of repeat times to encode input in a submodule.
    :param depth_input: number of input dimension .
    :param num_unitary_layers: number of repeat times of variational quantum gates.
    :param num_repetitions: number of repeat times of submodule.
    :param initial: initial all parameters with same value, this argument must be QTensor with only one element, default:None.
    :param dtype: data type of parameter, default:None,use float32.
    :param name: name of this module.
    :return: A VQC_QuantumEmbedding instance.

    Example::

        from pyvqnet.nn import Module
        from pyvqnet.qnn.vqc.qcircuit import VQC_QuantumEmbedding
        from pyvqnet.qnn.vqc import  QMachine,MeasureAll
        from pyvqnet import tensor
        import pyvqnet
        depth_input = 2
        num_repetitions = 2
        num_repetitions_input = 2
        num_unitary_layers = 2
        nq = depth_input * num_repetitions_input
        bz = 12

        class QM(Module):
            def __init__(self, name=""):
                super().__init__(name)

                self.ansatz = VQC_QuantumEmbedding(num_repetitions_input, depth_input,
                                                num_unitary_layers,
                                                num_repetitions, 
                                                initial=tensor.full([1],12.0),dtype=pyvqnet.kfloat64)

                self.measure = MeasureAll(obs={f"Z{nq-1}":1})
                self.device = QMachine(nq,dtype=pyvqnet.kcomplex128)

            def forward(self, x, *args, **kwargs):
                self.device.reset_states(x.shape[0])
                self.ansatz(x,q_machine=self.device)
                return self.measure(q_machine=self.device)

        inputx = tensor.arange(1.0, bz * depth_input + 1,
                                dtype=pyvqnet.kfloat64).reshape([bz, depth_input])
        qlayer = QM()
        y = qlayer(inputx)
        y.backward()
        print(y)

        # [[-0.2539548]
        #  [-0.1604787]
        #  [ 0.1492931]
        #  [-0.1711956]
        #  [-0.1577133]
        #  [ 0.1396999]
        #  [ 0.016864 ]
        #  [-0.0893069]
        #  [ 0.1897014]
        #  [ 0.0941301]
        #  [ 0.0550722]
        #  [ 0.2408579]]
    '''
    param_num: Incomplete
    dtype: Incomplete
    vqc: Incomplete
    def __init__(self, num_repetitions_input: int, depth_input: int, num_unitary_layers: int, num_repetitions: int, initial=None, dtype: int | None = None, name: str = '') -> None: ...
    def create_circuit(self, initial): ...
    def __call__(self, x, *args, **kwargs): ...
    def forward(self, x, q_machine): ...

def vqc_rotcircuit(q_machine: QMachine, wire: int | tuple[int, ...] | list[int], params):
    '''

    Arbitrary single qubit rotation.Number of qlist should be 1,and number of parameters should
    be 3

    .. math::

        R(\\phi,\\theta,\\omega) = RZ(\\omega)RY(\\theta)RZ(\\phi)= \\begin{bmatrix}
        e^{-i(\\phi+\\omega)/2}\\cos(\\theta/2) & -e^{i(\\phi-\\omega)/2}\\sin(\\theta/2) \\\\\n        e^{-i(\\phi-\\omega)/2}\\sin(\\theta/2) & e^{i(\\phi+\\omega)/2}\\cos(\\theta/2)
        \\end{bmatrix}.

    :param q_machine: quantum device.
    :param wire: which wire to act on
    :param para which represents paramters [\\phi, \\theta, \\omega]
.

    Example::

        from pyvqnet.qnn.vqc import qcircuit, qmeasure
        from pyvqnet.qnn.vqc import QMachine, RY, CNOT, PauliX, VQC_RotCircuit
        from pyvqnet.tensor import tensor
        import pyvqnet
        from pyvqnet.nn import Parameter

        class QModel(pyvqnet.nn.Module):
            def __init__(self, num_wires, dtype):
                super(QModel, self).__init__()
                self.rot_param = Parameter((3, ))
                self.rot_param.copy_value_from(tensor.QTensor([-0.5, 1, 2.3]))
                self._num_wires = num_wires
                self._dtype = dtype
                self.qm = QMachine(num_wires, dtype=dtype)
                self.rx_layer1 = VQC_RotCircuit
                self.ry_layer2 = RY(has_params=True,
                                    trainable=True,
                                    wires=0,
                                    init_params=tensor.QTensor([-0.5]))
                self.xlayer = PauliX(wires=0)
                self.cnot = CNOT(wires=[0, 1])
                self.measure = qmeasure.MeasureAll(obs={
                    "Y1":-3.5,"X0":0.23
                  
                })

            def forward(self, x, *args, **kwargs):
                self.qm.reset_states(x.shape[0])

                qcircuit.rx(q_machine=self.qm, wires=0, params=x[:, [1]])
                qcircuit.ry(q_machine=self.qm, wires=1, params=x[:, [0]])
                self.xlayer(q_machine=self.qm)
                self.rx_layer1(self.rot_param, wire=1, q_machine=self.qm)
                self.ry_layer2(q_machine=self.qm)
                self.cnot(q_machine=self.qm)
                rlt = self.measure(q_machine=self.qm)

                return rlt

        bsz = 12
        input_x = tensor.arange(1, bsz * 2 + 1,
                                dtype=pyvqnet.kfloat32).reshape([bsz, 2])
        input_x.requires_grad = True

        qunatum_model = QModel(num_wires=2, dtype=pyvqnet.kcomplex64)

        batch_y = qunatum_model(input_x)
        batch_y.backward()

        print(batch_y)


    '''
VQC_RotCircuit = vqc_rotcircuit

def vqc_crot_circuit(para, control_wire: int, rot_wire: int, q_machine: QMachine):
    '''

    The controlled-Rot operator

    .. math:: CR(\\phi, \\theta, \\omega) = \\begin{bmatrix}
            1 & 0 & 0 & 0 \\\\\n            0 & 1 & 0 & 0\\\\\n            0 & 0 & e^{-i(\\phi+\\omega)/2}\\cos(\\theta/2) & -e^{i(\\phi-\\omega)/2}\\sin(\\theta/2)\\\\\n            0 & 0 & e^{-i(\\phi-\\omega)/2}\\sin(\\theta/2) & e^{i(\\phi+\\omega)/2}\\cos(\\theta/2)
        \\end{bmatrix}.

    :param para which represents paramters [\\phi, \\theta, \\omega]
    :param control_wire: control qubit idx
    :param rot_wire: Rot qubit idx

    Example::

        from pyvqnet.tensor import QTensor
        from pyvqnet.qnn.vqc.qcircuit import VQC_CRotCircuit
        from pyvqnet.qnn.vqc import QMachine, MeasureAll
        p = QTensor([2, 3, 4.0])
        qm = QMachine(2)
        VQC_CRotCircuit(p, 0, 1, qm)
        m = MeasureAll(obs={"Z0": 1})
        exp = m(q_machine=qm)
        print(exp)

        # [[0.9999999]]
    '''
VQC_CRotCircuit = vqc_crot_circuit

def vqc_complexentangledcircuit(para, wires: list[int] | tuple[int, ...], depth: int, q_machine: QMachine):
    '''
    A layer of strongly entangled circuits composed of single-qubit spinner gates and CNOT gates.

    .. note::

       The mathematical representation of this circuit layer is a complex-valued unitary matrix. This circuit layer comes from the paper https://arxiv.org/abs/1804.00633.

    :param para: A Paramter or QTensor with shape of [depth,num_of_qubits,3] for this circuit. 
    :param wires: The qubits that the circuit acts on.
    :param depth: The depth of the circuit layer.
    :param q_machine: QMachine contains states.

    Example::

        from pyvqnet.tensor import QTensor,randu
        from pyvqnet.qnn.vqc.qcircuit import VQC_ComplexEntangledCircuit
        from pyvqnet.qnn.vqc import QMachine, MeasureAll
        p = randu([4,3,3])

        qm = QMachine(3)

        VQC_ComplexEntangledCircuit(p,range(3), 4,qm)
        m = MeasureAll(obs={"Z0": 1})
        exp = m(q_machine=qm)
        print(exp)
        #[[0.4673064]]
    '''
VQC_ComplexEntangledCircuit = vqc_complexentangledcircuit

def vqc_cswapcircuit(wires: list[int] | tuple[int, ...], q_machine: QMachine):
    '''
    The controlled-swap circuit

    .. math:: CSWAP = \\begin{bmatrix}
            1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\\\\n            0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\\\\n            0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\\\\n            0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\\\\n            0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 \\\\\n            0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 \\\\\n            0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 \\\\\n            0 & 0 & 0 & 0 & 0 & 0 & 0 & 1
        \\end{bmatrix}.

    .. note:: The first qubits provided corresponds to the **control qubit**.

    :param qlists: list of qubits idx. the
    first qubits is control qubit.Length of qlists have to be 3.
    :param q_machine: QMachine to run the circuit.

    Example::

        from pyvqnet.tensor import QTensor
        from pyvqnet.qnn.vqc.qcircuit import VQC_CSWAPcircuit
        from pyvqnet.qnn.vqc import QMachine, MeasureAll
        p = QTensor([0.2, 3, 4.0])

        qm = QMachine(3)

        VQC_CSWAPcircuit([1, 0, 2], qm)
        m = MeasureAll(obs={"Z0": 1})
        exp = m(q_machine=qm)

        # [[1.]]
    '''
VQC_CSWAPcircuit = vqc_cswapcircuit

def vqc_controlled_hadamard(wires: list[int] | tuple[int, ...], q_machine: QMachine):
    '''
    The controlled-Hadamard gates

    .. math:: CH = \\begin{bmatrix}
            1 & 0 & 0 & 0 \\\\\n            0 & 1 & 0 & 0 \\\\\n            0 & 0 & \\frac{1}{\\sqrt{2}} & \\frac{1}{\\sqrt{2}} \\\\\n            0 & 0 & \\frac{1}{\\sqrt{2}} & -\\frac{1}{\\sqrt{2}}
        \\end{bmatrix}.

    :param wires: qubits idx. first qubits is control qubit.Length of qlists have to be 2.
    :param q_machine: QMachine to run the circuit.

    Examples::

        from pyvqnet.tensor import QTensor
        from pyvqnet.qnn.vqc.qcircuit import VQC_Controlled_Hadamard
        from pyvqnet.qnn.vqc import QMachine, MeasureAll
        p = QTensor([0.2, 3, 4.0])

        qm = QMachine(3)

        VQC_Controlled_Hadamard([1, 0], qm)
        m = MeasureAll(obs={"Z0": 1})
        exp = m(q_machine=qm)
        print(exp)

        # [[1.]]
    '''
VQC_Controlled_Hadamard = vqc_controlled_hadamard

def vqc_ccz(wires: list[int] | tuple[int, ...], q_machine: QMachine):
    '''
    CCZ (controlled-controlled-Z) gate.

    .. math::

        CCZ =
        \\begin{pmatrix}
        1 & 0 & 0 & 0 & 0 & 0 & 0 & 0\\\\\n        0 & 1 & 0 & 0 & 0 & 0 & 0 & 0\\\\\n        0 & 0 & 1 & 0 & 0 & 0 & 0 & 0\\\\\n        0 & 0 & 0 & 1 & 0 & 0 & 0 & 0\\\\\n        0 & 0 & 0 & 0 & 1 & 0 & 0 & 0\\\\\n        0 & 0 & 0 & 0 & 0 & 1 & 0 & 0\\\\\n        0 & 0 & 0 & 0 & 0 & 0 & 1 & 0\\\\\n        0 & 0 & 0 & 0 & 0 & 0 & 0 & -1
        \\end{pmatrix}
    
    :param wires: qubits idx.first qubits is control qubit.Length of qlists have to be 3.
    :param q_machine: quantum machine.

    :return:
            pyqpanda QCircuit
    
    Examples::

        from pyvqnet.tensor import QTensor
        from pyvqnet.qnn.vqc.qcircuit import VQC_CCZ
        from pyvqnet.qnn.vqc import QMachine, MeasureAll
        p = QTensor([0.2, 3, 4.0])

        qm = QMachine(3)

        VQC_CCZ([1, 0, 2], qm)
        m = MeasureAll(obs={"Z0": 1})
        exp = m(q_machine=qm)

        # [[0.9999999]]     
    '''
VQC_CCZ = vqc_ccz

def vqc_fermionic_single_excitation(weight, wires: list[int] | tuple[int, ...], q_machine: QMachine):
    '''Circuit to exponentiate the tensor product of Pauli matrices representing the
    single-excitation operator entering the Unitary Coupled-Cluster Singles
    and Doubles (UCCSD) ansatz. UCCSD is a VQE ansatz commonly used to run quantum
    chemistry simulations.

    The Coupled-Cluster single-excitation operator is given by

    .. math::

        \\hat{U}_{pr}(\\theta) = \\mathrm{exp} \\{ \\theta_{pr} (\\hat{c}_p^\\dagger \\hat{c}_r
        -\\mathrm{H.c.}) \\},

    :param weight: input paramter acts on qubits p. should only have single element.
    :param wires: Wires that the template acts on. The wires represent the subset of orbitals in the interval [r, p]. Must be of minimum length 2. The first wire is interpreted as r and the last wire as p.
                Wires in between are acted on with CNOT gates to compute the parity of the set of qubits.
    :param q_machine: quantum q_machine.

    Examples::

        from pyvqnet.tensor import QTensor
        from pyvqnet.qnn.vqc.qcircuit import VQC_FermionicSingleExcitation
        from pyvqnet.qnn.vqc import QMachine, MeasureAll
        qm = QMachine(3)
        p0 = QTensor([0.5])

        VQC_FermionicSingleExcitation(p0, [1, 0, 2], qm)
        m = MeasureAll(obs={"Z0": 1})
        exp = m(q_machine=qm)

        # [[0.9999998]]
    '''
VQC_FermionicSingleExcitation = vqc_fermionic_single_excitation

def vqc_fermionic_double_excitation(weight, wires1: list[int] | tuple[int, ...], wires2: list[int] | tuple[int, ...], q_machine: QMachine):
    '''Circuit to exponentiate the tensor product of Pauli matrices representing the
    double-excitation operator entering the Unitary Coupled-Cluster Singles
    and Doubles (UCCSD) ansatz. UCCSD is a VQE ansatz commonly used to run quantum
    chemistry simulations.

    The CC double-excitation operator is given by

    .. math::

        \\hat{U}_{pqrs}(\\theta) = \\mathrm{exp} \\{ \\theta (\\hat{c}_p^\\dagger \\hat{c}_q^\\dagger
        \\hat{c}_r \\hat{c}_s - \\mathrm{H.c.}) \\},

    where :math:`\\hat{c}` and :math:`\\hat{c}^\\dagger` are the fermionic annihilation and
    creation operators and the indices :math:`r, s` and :math:`p, q` run over the occupied and
    unoccupied molecular orbitals, respectively. Using the `Jordan-Wigner transformation
    <https://arxiv.org/abs/1208.5986>`_ the fermionic operator defined above can be written
    in terms of Pauli matrices (for more details see
    `arXiv:1805.04340 <https://arxiv.org/abs/1805.04340>`_):

    .. math::

        \\hat{U}_{pqrs}(\\theta) = \\mathrm{exp} \\Big\\{
        \\frac{i\\theta}{8} \\bigotimes_{b=s+1}^{r-1} \\hat{Z}_b \\bigotimes_{a=q+1}^{p-1}
        \\hat{Z}_a (\\hat{X}_s \\hat{X}_r \\hat{Y}_q \\hat{X}_p +
        \\hat{Y}_s \\hat{X}_r \\hat{Y}_q \\hat{Y}_p + \\hat{X}_s \\hat{Y}_r \\hat{Y}_q \\hat{Y}_p +
        \\hat{X}_s \\hat{X}_r \\hat{X}_q \\hat{Y}_p - \\mathrm{H.c.}  ) \\Big\\}

    :param weight: input parameter,should only have single element.
    :param wires1: index list of the qubits representing
    the subset of occupied orbitals in the interval [s, r]. The first wire is interpreted as s and the last wire as r. Wires in between are acted on with CNOT gates to compute the parity of the set of qubits.
    :param wires2: index list of the qubits representing 
    the subset of unoccupied orbitals in the interval [q, p]. The first wire is interpreted as q and the last wire is interpreted as p. Wires in between are acted on with CNOT gates to compute the parity of the set of qubits.
    :param q_machine: quantum machine.


    Examples::

        from pyvqnet.tensor import QTensor
        from pyvqnet.qnn.vqc.qcircuit import VQC_FermionicDoubleExcitation
        from pyvqnet.qnn.vqc import QMachine, MeasureAll
        qm = QMachine(5)
        p0 = QTensor([0.5])

        VQC_FermionicDoubleExcitation(p0, [0, 1], [2, 3], qm)
        m = MeasureAll(obs={"Z0": 1})
        exp = m(q_machine=qm)

        # [[0.9999998]]

    '''
VQC_FermionicDoubleExcitation = vqc_fermionic_double_excitation

def vqc_basis_embedding(basis_state, q_machine: QMachine, wires=None):
    """
    Prepares a basis state on the given wires using a sequence of Pauli-X gates.

    :param basis_state: basis state to encoded.
    :param q_machine: quantum machine.
    :param wires: wires that the template acts on.If None,use all qubits of q_machine.
    
    Example::

        from pyvqnet.qnn.vqc import VQC_BasisEmbedding,QMachine
        qm  = QMachine(3)
        VQC_BasisEmbedding(basis_state=[1,1,0],q_machine=qm)
        print(qm.states)

        # [[[[0.+0.j 0.+0.j]
        #    [0.+0.j 0.+0.j]]
        # 
        #   [[0.+0.j 0.+0.j]
        #    [1.+0.j 0.+0.j]]]]

    """
VQC_BasisEmbedding = vqc_basis_embedding

def vqc_basisstate(basis_state, wires: _generic_wires_type, q_machine: QMachine):
    """
    Prepares a basis state on the given wires using a sequence of Pauli-X gates.

    :param wires: wires that the template acts on.
    :param q_machine: quantum machine.

    """
VQC_BasisState = vqc_basisstate

def vqc_uccsd(weights, wires: _multi_wires_type, s_wires: _generic_wires_type, d_wires: _generic_wires_type, init_state, q_machine: QMachine):
    '''
    
    Implements the Unitary Coupled-Cluster Singles and Doubles (UCCSD) ansatz.

    The UCCSD ansatz calls the
     `FermionicSingleExcitation` and `FermionicDoubleExcitation`
    templates to exponentiate the coupled-cluster excitation operator. UCCSD is a VQE ansatz
    commonly used to run quantum chemistry simulations.

    The UCCSD unitary, within the first-order Trotter approximation, is given by:

    .. math::

        \\hat{U}(\\vec{\\theta}) =
        \\prod_{p > r} \\mathrm{exp} \\Big\\{\\theta_{pr}
        (\\hat{c}_p^\\dagger \\hat{c}_r-\\mathrm{H.c.}) \\Big\\}
        \\prod_{p > q > r > s} \\mathrm{exp} \\Big\\{\\theta_{pqrs}
        (\\hat{c}_p^\\dagger \\hat{c}_q^\\dagger \\hat{c}_r \\hat{c}_s-\\mathrm{H.c.}) \\Big\\}

    where :math:`\\hat{c}` and :math:`\\hat{c}^\\dagger` are the fermionic annihilation and
    creation operators and the indices :math:`r, s` and :math:`p, q` run over the occupied and
    unoccupied molecular orbitals, respectively. Using the `Jordan-Wigner transformation
    <https://arxiv.org/abs/1208.5986>`_ the UCCSD unitary defined above can be written in terms
    of Pauli matrices as follows (for more details see
    `arXiv:1805.04340 <https://arxiv.org/abs/1805.04340>`_):

    .. math::

        \\hat{U}(\\vec{\\theta}) = && \\prod_{p > r} \\mathrm{exp} \\Big\\{ \\frac{i\\theta_{pr}}{2}
        \\bigotimes_{a=r+1}^{p-1} \\hat{Z}_a (\\hat{Y}_r \\hat{X}_p - \\mathrm{H.c.}) \\Big\\} \\\\\n        && \\times \\prod_{p > q > r > s} \\mathrm{exp} \\Big\\{ \\frac{i\\theta_{pqrs}}{8}
        \\bigotimes_{b=s+1}^{r-1} \\hat{Z}_b \\bigotimes_{a=q+1}^{p-1}
        \\hat{Z}_a (\\hat{X}_s \\hat{X}_r \\hat{Y}_q \\hat{X}_p +
        \\hat{Y}_s \\hat{X}_r \\hat{Y}_q \\hat{Y}_p +
        \\hat{X}_s \\hat{Y}_r \\hat{Y}_q \\hat{Y}_p +
        \\hat{X}_s \\hat{X}_r \\hat{X}_q \\hat{Y}_p -
        \\{\\mathrm{H.c.}\\}) \\Big\\}.


    :param weights : Size ``(len(s_wires) + len(d_wires),)`` tensor containing the parameters
        :math:`\\theta_{pr}` and :math:`\\theta_{pqrs}` entering the Z rotation in
        `FermionicSingleExcitation` and `FermionicDoubleExcitation`.
    :param wires: wires that the template acts on
    :param s_wires: Sequence of lists containing the wires ``[r,...,p]``
        resulting from the single excitation
        :math:`\\vert r, p \\rangle = \\hat{c}_p^\\dagger \\hat{c}_r \\vert \\mathrm{HF} \\rangle`,
        where :math:`\\vert \\mathrm{HF} \\rangle` denotes the Hartee-Fock reference state.
    :param d_wires: Sequence of lists, each containing two lists that
        specify the indices ``[s, ...,r]`` and ``[q,..., p]`` defining the double excitation
        :math:`\\vert s, r, q, p \\rangle = \\hat{c}_p^\\dagger \\hat{c}_q^\\dagger \\hat{c}_r
        \\hat{c}_s \\vert \\mathrm{HF} \\rangle`.
    :param init_state: Length ``len(wires)`` occupation-number vector representing the
        HF state. ``init_state`` is used to initialize the wires.
    :param q_machine: quantum machine.

    Examples::

        from pyvqnet.qnn.vqc import VQC_UCCSD, QMachine, MeasureAll
        from pyvqnet.tensor import QTensor
        p0 = QTensor([2, 0.5, -0.2, 0.3, -2, 1, 3, 0])
        s_wires = [[0, 1, 2], [0, 1, 2, 3, 4], [1, 2, 3], [1, 2, 3, 4, 5]]
        d_wires = [[[0, 1], [2, 3]], [[0, 1], [2, 3, 4, 5]], [[0, 1], [3, 4]],
                [[0, 1], [4, 5]]]
        qm = QMachine(6)

        VQC_UCCSD(p0, range(6), s_wires, d_wires, QTensor([1.0, 1, 0, 0, 0, 0]), qm)
        m = MeasureAll(obs={"Z1": 1})
        exp = m(q_machine=qm)
        print(exp)

        # [[0.963802]]
    '''
VQC_UCCSD = vqc_uccsd

def vqc_quantumpooling_circuit(ignored_wires: _generic_wires_type, sinks_wires: _generic_wires_type, params, q_machine: QMachine):
    """
        A quantum circuit to down samples the data.
        To ‘artificially’ reduce the number of qubits in our circuit, we first begin by creating pairs of the qubits in our system.
        After initially pairing all the qubits, we apply our generalized 2 qubit unitary to each pair.
        After applying this two qubit unitary, we then ignore one qubit from each pair of qubits for the remainder of the neural network.

        :param ignored_wires: source qubits index which will be ignored.
        :param sinks_wires: target qubits index which will be reserverd.
        :param params: input parameters.
        :param q_machine: quantum machine.

    Exmaple::

        from pyvqnet.qnn.vqc import VQC_QuantumPoolingCircuit, QMachine
        import pyqpanda as pq
        from pyvqnet import tensor
        machine = pq.CPUQVM()
        machine.init_qvm()
        qlists = machine.qAlloc_many(4)
        p = tensor.full([6], 0.35)
        qm = QMachine(4)
        VQC_QuantumPoolingCircuit(q_machine=qm,
                                ignored_wires=[0, 1],
                                sinks_wires=[2, 3],
                                params=p)

    """
VQC_QuantumPoolingCircuit = vqc_quantumpooling_circuit

def vqc_angle_embedding(input_feat, wires: _generic_wires_type, q_machine: QMachine, rotation: str = 'X'):
    """

    Encodes :math:`N` features into the rotation angles of :math:`n` qubits, where :math:`N \\leq n`.

    The rotations can be chosen as either : 'X' , 'Y' , 'Z',
    as defined by the ``rotation`` parameter:

    * ``rotation='X'`` uses the features as angles of RX rotations

    * ``rotation='Y'`` uses the features as angles of RY rotations

    * ``rotation='Z'`` uses the features as angles of RZ rotations

    The length of ``features`` has to be smaller or equal to the number of qubits.
    If there are fewer entries in ``features`` than qlists, the circuit does
    not apply the remaining rotation gates.

    :param input_feat: numpy array which represents paramters
    :param wires: wires that the template acts on.
    :param q_machine: quantum machine.
    :param rotation: rotation string.

    Example::

        from pyvqnet.qnn.vqc import VQC_AngleEmbedding, QMachine
        from pyvqnet.tensor import QTensor
        qm  = QMachine(2)

        VQC_AngleEmbedding([2.2, 1], [0, 1], q_machine=qm, rotation='X')
        print(qm.states)

        # [[[ 0.398068 +0.j         0.       -0.2174655j]
        #   [ 0.       -0.7821081j -0.4272676+0.j       ]]]

        VQC_AngleEmbedding([2.2, 1], [0, 1], q_machine=qm, rotation='Y')
        print(qm.states)

        # [[[-0.0240995+0.6589843j  0.4207355+0.2476033j]
        #   [ 0.4042482-0.2184162j  0.       -0.3401631j]]]

        VQC_AngleEmbedding([2.2, 1], [0, 1], q_machine=qm, rotation='Z')
        print(qm.states)

        # [[[0.659407 +0.0048471j 0.4870554-0.0332093j]
        #   [0.4569675+0.047989j  0.340018 +0.0099326j]]]        
    """
VQC_AngleEmbedding = vqc_angle_embedding

def vqc_amplitude_embedding(input_feature, q_machine: QMachine):
    """
    Encodes :math:`2^n` features into the amplitude vector of :math:`N` qubits.
    if N > n, the input will pad zero to :math:`2^n`.

    :param input_feature: numpy array which represents paramters.
            When QMachine's dtype is kcomplex128, input's dtype must be kfloat64,
            When QMachine's dtype is kcomplex64, input's dtype must be kfloat32.
            QMachine's device should be same as input's device.
    :param q_machine: quantum machine.

    Example::

        from pyvqnet.qnn.vqc import VQC_AmplitudeEmbedding,QMachine
        from pyvqnet.tensor import QTensor
        qm  = QMachine(3)
        p = QTensor( [3.2,-2,-2,0.3,12,0.1,2,-1])
        VQC_AmplitudeEmbedding(p,q_machine=qm)
        print(qm.states)

        # [[[[ 0.2473717+0.j -0.1546073+0.j]
        #    [-0.1546073+0.j  0.0231911+0.j]]
        # 
        #   [[ 0.9276441+0.j  0.0077304+0.j]
        #    [ 0.1546073+0.j -0.0773037+0.j]]]]
    """
VQC_AmplitudeEmbedding = vqc_amplitude_embedding

def vqc_iqp_embedding(input_feat, q_machine: QMachine, rep: int = 1):
    """

    Encodes :math:`n` features into :math:`n` qubits using diagonal gates of an IQP circuit.

    The embedding was proposed by `Havlicek et al. (2018) <https://arxiv.org/pdf/1804.11326.pdf>`_.

    The basic IQP circuit can be repeated by specifying ``n_repeats``.

    :param input_feat: numpy array which represents paramters
    :param q_machine: quantum machine.
    :param rep: repeat circuits block
    :return: quantum circuits

    Example::

        from pyvqnet.qnn.vqc import VQC_IQPEmbedding, QMachine
        from pyvqnet.tensor import QTensor
        qm  = QMachine(3)
        VQC_IQPEmbedding(QTensor([3.2,-2,-2]), q_machine=qm)
        print(qm.states)        
        
        # [[[[ 0.0309356-0.3521973j  0.3256442+0.1376801j]
        #    [ 0.3256442+0.1376801j  0.2983474+0.1897071j]]
        # 
        #   [[ 0.0309356+0.3521973j -0.3170519-0.1564546j]
        #    [-0.3170519-0.1564546j -0.2310978-0.2675701j]]]]

    """
VQC_IQPEmbedding = vqc_iqp_embedding

def vqc_zfeaturemap(input_feat, q_machine: QMachine, data_map_func: Callable | None = None, rep: int = 2):
    """

    The first order Pauli Z-evolution circuit.

    On 3 qubits and with 2 repetitions the circuit is represented by:

    .. parsed-literal::

        ┌───┐┌──────────────┐┌───┐┌──────────────┐
        ┤ H ├┤ U1(2.0*x[0]) ├┤ H ├┤ U1(2.0*x[0]) ├
        ├───┤├──────────────┤├───┤├──────────────┤
        ┤ H ├┤ U1(2.0*x[1]) ├┤ H ├┤ U1(2.0*x[1]) ├
        ├───┤├──────────────┤├───┤├──────────────┤
        ┤ H ├┤ U1(2.0*x[2]) ├┤ H ├┤ U1(2.0*x[2]) ├
        └───┘└──────────────┘└───┘└──────────────┘
    
    The Pauli strings are fixed as `['Z']`. As a result the first order expansion will be a circuit without entangling gates.
    
    :param input_feat: numpy array which represents paramters
    :param q_machine: quantum machine.
    :param data_map_func: A mapping function for data.
    :param rep: repeat circuits block

    Example::

        from pyvqnet.qnn.vqc import VQC_ZFeatureMap, QMachine, hadamard
        from pyvqnet.tensor import QTensor
        qm = QMachine(3)
        for i in range(3):
            hadamard(q_machine=qm, wires=[i])
        VQC_ZFeatureMap(input_feat=QTensor([[0.1,0.2,0.3]]),q_machine = qm)
        print(qm.states)
        
        # [[[[0.3535534+0.j        0.2918002+0.1996312j]
        #    [0.3256442+0.1376801j 0.1910257+0.2975049j]]
        # 
        #   [[0.3465058+0.0702402j 0.246323 +0.2536236j]
        #    [0.2918002+0.1996312j 0.1281128+0.3295255j]]]]

    """
VQC_ZFeatureMap = vqc_zfeaturemap

def vqc_zzfeaturemap(input_feat, q_machine: QMachine, data_map_func: Callable | None = None, entanglement: str | list[list[int]] | Callable[[int], list[int]] = 'full', rep: int = 2):
    """
    Second-order Pauli-Z evolution circuit.

    For 3 qubits and 1 repetition and linear entanglement the circuit is represented by:

    .. parsed-literal::

        ┌───┐┌─────────────────┐
        ┤ H ├┤ U1(2.0*φ(x[0])) ├──■────────────────────────────■────────────────────────────────────
        ├───┤├─────────────────┤┌─┴─┐┌──────────────────────┐┌─┴─┐
        ┤ H ├┤ U1(2.0*φ(x[1])) ├┤ X ├┤ U1(2.0*φ(x[0],x[1])) ├┤ X ├──■────────────────────────────■──
        ├───┤├─────────────────┤└───┘└──────────────────────┘└───┘┌─┴─┐┌──────────────────────┐┌─┴─┐
        ┤ H ├┤ U1(2.0*φ(x[2])) ├──────────────────────────────────┤ X ├┤ U1(2.0*φ(x[1],x[2])) ├┤ X ├
        └───┘└─────────────────┘                                  └───┘└──────────────────────┘└───┘

    where ``φ`` is a classical non-linear function, which defaults to ``φ(x) = x`` if and
    ``φ(x,y) = (pi - x)(pi - y)``.


    :param input_feat: numpy array which represents paramters
    :param q_machine: quantum machine.
    :param data_map_func: A mapping function for data.
    :param entanglement: Specifies the entanglement structure. 
    :param rep: repeat circuits block

    Example::

        from pyvqnet.qnn.vqc import VQC_ZZFeatureMap, QMachine
        from pyvqnet.tensor import QTensor
        qm = QMachine(3)
        VQC_ZZFeatureMap(q_machine=qm, input_feat=QTensor([[0.1,0.2,0.3]]))
        print(qm.states)

        # [[[[-0.4234843-0.0480578j -0.144067 +0.1220178j]
        #    [-0.0800646+0.0484439j -0.5512857-0.2947832j]]
        # 
        #   [[ 0.0084012-0.0050071j -0.2593993-0.2717131j]
        #    [-0.1961917-0.3470543j  0.2786197+0.0732045j]]]]

    """
VQC_ZZFeatureMap = vqc_zzfeaturemap

def vqc_allsinglesdoubles(weights, q_machine: QMachine, hf_state, wires: _multi_wires_type, singles: _generic_wires_type | None = None, doubles: _generic_wires_type | None = None):
    """In this case, we have four single and double excitations that preserve the total-spin
        projection of the Hartree-Fock state. The :class:`~.vqc.qcircuit.single_excitation` gate
        :math:`G` act on the qubits ``[0, 2], [0, 4], [1, 3], [1, 5]`` as indicated by the
        squares, while the :class:`~.vqc.qcircuit.double_excitation` operation :math:`G^{(2)}` is
        applied to the qubits ``[0, 1, 2, 3], [0, 1, 2, 5], [0, 1, 2, 4], [0, 1, 4, 5]``.

    The resulting unitary conserves the number of particles and prepares the
    :math:`n`-qubit system in a superposition of the initial Hartree-Fock state and
    other states encoding multiply-excited configurations.

    :param weights: size ``(len(singles) + len(doubles),)`` tensor containing the angles entering the :class:`vqc.qcircuit.single_excitation` and
            :class:`vqc.qcircuit.double_excitation` operations, in that order
    :param q_machine: quantum machine.
    :param hf_state:  Length ``len(wires)`` occupation-number vector representing the Hartree-Fock state. ``hf_state`` is used to initialize the wires.
    :param wires: wires that the template acts on.
    :param singles: sequence of lists with the indices of the two qubits the :class:`vqc.qcircuit.single_excitation` operations act on.
    :param doubles: sequence of lists with the indices of the four qubits the :class:`vqc.qcircuit.double_excitation` operations act on.

    Example::

        from pyvqnet.qnn.vqc import VQC_AllSinglesDoubles, QMachine
        from pyvqnet.tensor import QTensor
        qm = QMachine(qubits)

        VQC_AllSinglesDoubles(q_machine=qm, weights=QTensor([0.55, 0.11, 0.53]), 
                              hf_state = QTensor([1,1,0,0]), singles=[[0, 2], [1, 3]], doubles=[[0, 1, 2, 3]], wires=[0,1,2,3])
        print(qm.states)
        
        # [ 0.        +0.j  0.        +0.j  0.        +0.j -0.23728043+0.j
        #   0.        +0.j  0.        +0.j -0.27552837+0.j  0.        +0.j
        #   0.        +0.j -0.12207296+0.j  0.        +0.j  0.        +0.j
        #   0.9235152 +0.j  0.        +0.j  0.        +0.j  0.        +0.j]

    """
VQC_AllSinglesDoubles = vqc_allsinglesdoubles

def vqc_basisrotation(q_machine: QMachine, wires: _generic_wires_type, unitary_matrix, check: bool = False):
    """

    Implement a circuit that provides a unitary that can be used to do an exact single-body basis rotation.

    The :class:`~.vqc.qcircuit.VQC_BasisRotation` template performs the following unitary transformation :math:`U(u)` determined by the single-particle fermionic
    generators as given in `arXiv:1711.04789 <https://arxiv.org/abs/1711.04789>`_\\ :

    .. math::

        U(u) = \\exp{\\left( \\sum_{pq} \\left[\\log u \\right]_{pq} (a_p^\\dagger a_q - a_q^\\dagger a_p) \\right)}.

    The unitary :math:`U(u)` is implemented efficiently by performing its Givens decomposition into a sequence of
    :class:`~vqc.qcircuit.phaseshift` and :class:`~vqc.qcircuit.single_excitation` gates using the construction scheme given in
    `Optica, 3, 1460 (2016) <https://opg.optica.org/optica/fulltext.cfm?uri=optica-3-12-1460&id=355743>`_\\ .
    
    :param q_machine: quantum machine.
    :param wires: wires that the operator acts on.
    :param unitary_matrix: matrix specifying the basis transformation.
    :param check: test unitarity of the provided `unitary_matrix`.
    
    Example::

        from pyvqnet.qnn.vqc import VQC_BasisRotation, QMachine, hadamard, isingzz
        from pyvqnet.tensor import QTensor
        V = np.array([[0.73678+0.27511j, -0.5095 +0.10704j, -0.06847+0.32515j],
                      [0.73678+0.27511j, -0.5095 +0.10704j, -0.06847+0.32515j],
                      [-0.21271+0.34938j, -0.38853+0.36497j,  0.61467-0.41317j]])
        eigen_vals, eigen_vecs = np.linalg.eigh(V)
        umat = eigen_vecs.T
        wires = range(len(umat))
        
        qm = QMachine(len(umat))

        for i in range(len(umat)):
            hadamard(q_machine=qm, wires=i)
        isingzz(q_machine=qm, params=QTensor([0.55]), wires=[0,2])
        VQC_BasisRotation(q_machine=qm, wires=wires,unitary_matrix=QTensor(umat,dtype=qm.state.dtype))
        
        print(qm.states)
        
        # [[[[ 0.3402686-0.0960063j  0.4140436-0.3069579j]
        #    [ 0.1206574+0.1982292j  0.5662895-0.0949503j]]
        # 
        #   [[-0.1715559-0.1614315j  0.1624039-0.0598041j]
        #    [ 0.0608986-0.1078906j -0.305845 +0.1773662j]]]]

    """
VQC_BasisRotation = vqc_basisrotation

class _entangle(Module):
    vqc: Incomplete
    def __init__(self, entangle_gate, entangle_rules, dtype, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine): ...

class _single_rot(Module):
    n_qubits: Incomplete
    single_rot_gate_list: Incomplete
    vqc: Incomplete
    def __init__(self, single_rot_gate_list, n_qubits, initial, dtype, name: str = '') -> None: ...
    def __call__(self, *args, **kwargs): ...
    def forward(self, q_machine): ...

def givens_decomposition(unitary):
    """Decompose a unitary into a sequence of Givens rotation gates with phase shifts and a diagonal phase matrix.

    This decomposition is based on the construction scheme given in `Optica, 3, 1460 (2016) <https://opg.optica.org/optica/fulltext.cfm?uri=optica-3-12-1460&id=355743>`_\\ ,
    which allows one to write any unitary matrix :math:`U` as:

    .. math::

        U = D \\left(\\prod_{(m, n) \\in G} T_{m, n}(\\theta, \\phi)\\right),

    where :math:`D` is a diagonal phase matrix, :math:`T(\\theta, \\phi)` is the Givens rotation gates with phase shifts and :math:`G` defines the
    specific ordered sequence of the Givens rotation gates acting on wires :math:`(m, n)`. The unitary for the :math:`T(\\theta, \\phi)` gates
    appearing in the decomposition is of the following form:

    .. math:: T(\\theta, \\phi) = \\begin{bmatrix}
                                    1 & 0 & 0 & 0 \\\\\n                                    0 & e^{i \\phi} \\cos(\\theta) & -\\sin(\\theta) & 0 \\\\\n                                    0 & e^{i \\phi} \\sin(\\theta) & \\cos(\\theta) & 0 \\\\\n                                    0 & 0 & 0 & 1
                                \\end{bmatrix},

    where :math:`\\theta \\in [0, \\pi/2]` is the angle of rotation in the :math:`\\{|01\\rangle, |10\\rangle \\}` subspace
    and :math:`\\phi \\in [0, 2 \\pi]` represents the phase shift at the first wire.

    

    """
def vqc_controlled_hadamard_wrapper(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False): ...

class CH(Operation, metaclass=ABCMeta):
    """Class for CH Gate."""
    num_params: int
    num_wires: int
    func: Incomplete
    @property
    def control_wires(self): ...

def vqc_ccz_wrapper(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False): ...

class CCZ(Operation, metaclass=ABCMeta):
    """Class for CCZ Gate."""
    num_params: int
    num_wires: int
    func: Incomplete
    @property
    def control_wires(self): ...

def CRot_wrapper(q_machine: QMachine, wires: _generic_wires_type, params=None, use_dagger: bool = False): ...

class CRot(Operation, metaclass=ABCMeta):
    """Class for CRot Gate."""
    num_params: int
    num_wires: int
    func: Incomplete

@lru_cache
def check_gate_param_dtype(gate_dtype, params_dtype) -> None: ...
