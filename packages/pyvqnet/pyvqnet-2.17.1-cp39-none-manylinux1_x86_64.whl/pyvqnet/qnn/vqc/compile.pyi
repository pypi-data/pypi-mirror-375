from ...backends import global_backend as global_backend
from .qcircuit import op_controlled_wires_dict as op_controlled_wires_dict
from .qmachine_utils import find_qmachine as find_qmachine
from .qmeasure import get_measure_name_dict as get_measure_name_dict
from .utils.utils import construct_modules_from_ops as construct_modules_from_ops, stack_broadcasted_single_qubit_rot_angles as stack_broadcasted_single_qubit_rot_angles
from _typeshed import Incomplete
from pyvqnet import tensor as tensor
from pyvqnet.dtype import C_DTYPE as C_DTYPE, float_dtype_to_complex_dtype as float_dtype_to_complex_dtype
from pyvqnet.tensor import cos as cos, sin as sin, stack as stack

def fuse_rot_angles(angles_1, angles_2): ...
def shared_wires(list_of_wires): ...
def find_next_gate(wires, op_list): ...

op_basis_dict: Incomplete

def get_op_basis_from_name(name: str): ...
def get_op_controlled(op: dict): ...
def single_qubit_ops_fuse(operations): ...
def wrapper_single_qubit_op_fuse(f):
    '''
    A decorator to apply single qubit operators fusing to Rot.

    .. Notes::

        f is Module\'s forward function. and should set use_single_qubit_ops_fuse first.


    Example::

        from pyvqnet import tensor
        from pyvqnet.qnn.vqc import QMachine, Operation, apply_gate_operation_impl
        from pyvqnet import kcomplex128
        from pyvqnet.tensor import adjoint
        import numpy as np
        from pyvqnet.qnn.vqc import single_qubit_ops_fuse, wrapper_single_qubit_op_fuse, QModule
        from pyvqnet.qnn.vqc import QMachine, RX, RY, CNOT, PauliX, qmatrix, PauliZ, T, MeasureAll, RZ
        from pyvqnet.tensor import QTensor, tensor
        import pyvqnet
        import numpy as np
        from pyvqnet.utils import set_random_seed

        import time

        set_random_seed(42)

        class QModel(QModule):
            def __init__(self, num_wires, dtype):
                super(QModel, self).__init__()

                self._num_wires = num_wires
                self._dtype = dtype
                self.qm = QMachine(num_wires, dtype=dtype)
                self.rx_layer = RX(has_params=True, trainable=False, wires=0, dtype=dtype)
                self.ry_layer = RY(has_params=True, trainable=False, wires=1, dtype=dtype)
                self.rz_layer = RZ(has_params=True, trainable=False, wires=1, dtype=dtype)
                self.rz_layer2 = RZ(has_params=True, trainable=False, wires=1, dtype=dtype)
                self.tlayer = T(wires=1)
                self.cnot = CNOT(wires=[0, 1])
                self.measure = MeasureAll(obs={
                    "X1":1
                })

            @wrapper_single_qubit_op_fuse
            def forward(self, x, *args, **kwargs):
                self.qm.reset_states(x.shape[0])

                self.rx_layer(params=x[:, [0]], q_machine=self.qm)
                self.cnot(q_machine=self.qm)
                self.ry_layer(params=x[:, [1]], q_machine=self.qm)
                self.tlayer(q_machine=self.qm)
                self.rz_layer(params=x[:, [2]], q_machine=self.qm)
                self.rz_layer2(params=x[:, [3]], q_machine=self.qm)
                rlt = self.measure(q_machine=self.qm)

                return rlt

        input_x = tensor.QTensor([[0.1, 0.2, 0.3, 0.4], [0.1, 0.2, 0.3, 0.4]],
                                dtype=pyvqnet.kfloat64)

        input_xt = tensor.tile(input_x, (100, 1))
        input_xt.requires_grad = True

        qunatum_model = QModel(num_wires=2, dtype=pyvqnet.kcomplex128)
        qunatum_model.use_single_qubit_ops_fuse = True
        batch_y = qunatum_model(input_xt)

    
    '''
def commute_controlled_right(operations):
    """Push commuting single qubit gates to the right of controlled gates.

    """
def commute_controlled_left(operations):
    """Push commuting single qubit gates to the left of controlled gates.

    """
def commute_controlled(op_history, direction: str = 'right'):
    """
    Quantum transform to move commuting gates past control and target qubits of controlled operations.
    Diagonal gates on either side of control qubits do not affect the outcome
    of controlled gates; thus we can push all the single-qubit gates on the
    first qubit together on the right (and fuse them if desired). Similarly, X
    gates commute with the target of ``CNOT`` and ``Toffoli`` (and ``PauliY``
    with ``CRY``). We can use the transform to push single-qubit gates as
    far as possible through the controlled operations.


    """
def wrapper_commute_controlled(f, direction: str = 'right'):
    '''
    Decorator for commute_controlled.
    Quantum transform to move commuting gates past control and target qubits of controlled operations.
    Diagonal gates on either side of control qubits do not affect the outcome
    of controlled gates; thus we can push all the single-qubit gates on the
    first qubit together on the right (and fuse them if desired). Similarly, X
    gates commute with the target of ``CNOT`` and ``Toffoli`` (and ``PauliY``
    with ``CRY``). We can use the transform to push single-qubit gates as
    far as possible through the controlled operations.
    
    :param f: forward function.
    :param direction: move the single qubit gates to left or right, default: "right".

    Examples::

        from pyvqnet import tensor
        from pyvqnet.qnn.vqc import QMachine, Operation, apply_gate_operation_impl, op_history_to_list, operation_derivative, adjoint_grad_calc, QuantumLayerAdjoint
        from pyvqnet import kcomplex128
        from pyvqnet.tensor import adjoint
        import numpy as np
        from pyvqnet.qnn.vqc import wrapper_commute_controlled, pauliy, QModule
        
        from pyvqnet.qnn.vqc import QMachine, RX, RY, CNOT, S, CRY, PauliZ, PauliX, T, MeasureAll, RZ, CZ, PhaseShift, Toffoli, cnot, cry, toffoli
        from pyvqnet.tensor import QTensor, tensor
        import pyvqnet
        import numpy as np
        from pyvqnet.utils import set_random_seed

        import time
        from functools import partial
        set_random_seed(42)

        class QModel(QModule):
            def __init__(self, num_wires, dtype):
                super(QModel, self).__init__()

                self._num_wires = num_wires
                self._dtype = dtype
                self.qm = QMachine(num_wires, dtype=dtype)

                self.cz = CZ(wires=[0, 2])
                self.paulix = PauliX(wires=2)
                self.s = S(wires=0)
                self.ps = PhaseShift(has_params=True, trainable= True, wires=0, dtype=dtype)
                self.t = T(wires=0)
                self.rz = RZ(has_params=True, wires=1, dtype=dtype)
                self.measure = MeasureAll(obs={
                    "Z0":1
                })

            @partial(wrapper_commute_controlled, direction="left")
            def forward(self, x, *args, **kwargs):
                self.qm.reset_states(x.shape[0])
                self.cz(q_machine=self.qm)
                self.paulix(q_machine=self.qm)
                self.s(q_machine=self.qm)
                cnot(q_machine=self.qm, wires=[0, 1])
                pauliy(q_machine=self.qm, wires=1)
                cry(q_machine=self.qm, params=1 / 2, wires=[0, 1])
                self.ps(q_machine=self.qm)
                toffoli(q_machine=self.qm, wires=[0, 1, 2])
                self.t(q_machine=self.qm)
                self.rz(q_machine=self.qm)
                rlt = self.measure(q_machine=self.qm)

                return rlt

        import pyvqnet
        import pyvqnet.tensor as tensor
        input_x = tensor.QTensor([[0.1, 0.2, 0.3, 0.4], [0.1, 0.2, 0.3, 0.4]],
                                    dtype=pyvqnet.kfloat64)

        input_xt = tensor.tile(input_x, (100, 1))
        input_xt.requires_grad = True

        qunatum_model = QModel(num_wires=3, dtype=pyvqnet.kcomplex128)
        qunatum_model.use_commute_controlled = True
        batch_y = qunatum_model(input_xt)

        batch_y.backward()
        flatten_oph_names = []
        for d in qunatum_model.compiled_op_historys:
            if "use_commute_controlled" in d.keys():
                oph = d["op_history"]
                for i in oph:
                    n = i.__class__.__name__
                    flatten_oph_names.append(n)
        print(flatten_oph_names)
        #[\'S\', \'PhaseShift\', \'T\', \'CZ\', \'PauliX\', \'CNOT\', \'PauliY\', \'CRY\', \'RZ\', \'Toffoli\', \'MeasureAll\']
    '''

composable_rotations: Incomplete
composable_rotations_adjoint_params: Incomplete

def merge_rotations(op_history, atol: float = 1e-08):
    """Quantum transform to combine rotation gates of the same type that act sequentially.

    If the combination of two rotation produces an angle that is close to 0,
    neither gate will be applied.

    :param op_history: op history generated from QModule forward function.
    :param atol: absolute tolerance, default: 1e-8.
    :return:
        new op history.
    """
def wrapper_merge_rotations(f):
    '''
    Decorator for merge same type rotation gates including "rx", "ry", "rz", "phaseshift", "crx", "cry", "crz", "controlledphaseshift", "isingxx",
    "isingyy", "isingzz", "rot".

    Example::

        import pyvqnet
        from pyvqnet.tensor import tensor

        from pyvqnet import tensor
        from pyvqnet.qnn.vqc import QMachine, Operation, apply_gate_operation_impl, op_history_to_list, operation_derivative, adjoint_grad_calc, QuantumLayerAdjoint
        from pyvqnet import kcomplex128
        from pyvqnet.tensor import adjoint
        import numpy as np

        
        from pyvqnet.qnn.vqc import *
        from pyvqnet.qnn.vqc import QModule
        from pyvqnet.tensor import QTensor, tensor
        import pyvqnet
        import numpy as np
        from pyvqnet.utils import set_random_seed

        set_random_seed(42)

        class QModel(QModule):
            def __init__(self, num_wires, dtype):
                super(QModel, self).__init__()

                self._num_wires = num_wires
                self._dtype = dtype
                self.qm = QMachine(num_wires, dtype=dtype)

                self.measure = MeasureAll(obs={
                    "Z0":1
                })

            @wrapper_merge_rotations
            def forward(self, x, *args, **kwargs):

                self.qm.reset_states(x.shape[0])
                
                rx(q_machine=self.qm, params=x[:, [1]], wires=(0, ))
                rx(q_machine=self.qm, params=x[:, [1]], wires=(0, ))
                rx(q_machine=self.qm, params=x[:, [1]], wires=(0, ))
                rot(q_machine=self.qm, params=x, wires=(1, ), use_dagger=True)
                rot(q_machine=self.qm, params=x, wires=(1, ), use_dagger=True)
                isingxy(q_machine=self.qm, params=x[:, [2]], wires=(0, 1))
                isingxy(q_machine=self.qm, params=x[:, [0]], wires=(0, 1))
                cnot(q_machine=self.qm, wires=[1, 2])
                ry(q_machine=self.qm, params=x[:, [1]], wires=(1, ))
                hadamard(q_machine=self.qm, wires=(2, ))
                crz(q_machine=self.qm, params=x[:, [2]], wires=(2, 0))
                ry(q_machine=self.qm, params=-x[:, [1]], wires=1)
                return self.measure(q_machine=self.qm)


        input_x = tensor.QTensor([[1, 2, 3], [1, 2, 3]], dtype=pyvqnet.kfloat64)

        input_x.requires_grad = True

        qunatum_model = QModel(num_wires=3, dtype=pyvqnet.kcomplex128)
        qunatum_model.use_merge_rotations = True
        batch_y = qunatum_model(input_x)
        print(qunatum_model.compiled_op_historys)
        batch_y.backward()
        print(input_x.grad)
        print(batch_y)
        # [{\'use_merge_rotations\': True, \'op_history\': [{\'name\': \'rx\', \'wires\': (0,), \'params\': [[6.],
        #  [6.]], \'dtype\': 9, \'use_dagger\': False, \'trainable\': False, \'if_op_within_measure\': False, \'params_with_autograd\': [[6.],
        #  [6.]]}, {\'name\': \'rot\', \'wires\': (1,), \'params\': [[ 1.9005879, 0.776137 ,-2.3825974],
        #  [ 1.9005879, 0.776137 ,-2.3825974]], \'dtype\': 9, \'use_dagger\': False, \'trainable\': False, \'if_op_within_measure\': False, \'params_with_autograd\': [[ 1.9005879, 0.776137 ,-2.3825974],
        #  [ 1.9005879, 0.776137 ,-2.3825974]]}, {\'name\': \'isingxy\', \'wires\': (0, 1), \'params\': [[3.],
        #  [3.]], \'dtype\': 9, \'use_dagger\': False, \'trainable\': False, \'if_op_within_measure\': False, \'params_with_autograd\': [[3.],
        #  [3.]], \'bsz\': 2, \'obs\': None, \'device\': 0}, {\'name\': \'isingxy\', \'wires\': (0, 1), \'params\': [[1.],
        #  [1.]], \'dtype\': 9, \'use_dagger\': False, \'trainable\': False, \'if_op_within_measure\': False, \'params_with_autograd\': [[1.],
        #  [1.]], \'bsz\': 2, \'obs\': None, \'device\': 0}, {\'name\': \'cnot\', \'wires\': (1, 2), \'params\': None, \'dtype\': 8, \'use_dagger\': False, \'trainable\': False, \'if_op_within_measure\': False, \'params_with_autograd\': None, \'bsz\': 2, \'obs\': None, \'device\': 0}, {\'name\': \'hadamard\', \'wires\': (2,), \'params\': None, \'dtype\': 8, \'use_dagger\': False, \'trainable\': False, \'if_op_within_measure\': False, \'params_with_autograd\': None, \'bsz\': 2, \'obs\': None, \'device\': 0}, {\'name\': \'crz\', \'wires\': (2, 0), \'params\': [[3.],
        #  [3.]], \'dtype\': 9, \'use_dagger\': False, \'trainable\': False, \'if_op_within_measure\': False, \'params_with_autograd\': [[3.],
        #  [3.]], \'bsz\': 2, \'obs\': None, \'device\': 0}, {\'name\': \'MeasureAll\', \'wires\': [0], \'params\': None, \'dtype\': None, \'use_dagger\': False, \'trainable\': False, \'if_op_within_measure\': False, \'params_with_autograd\': None, \'bsz\': 2, \'obs\': {\'wires\': [0], \'observables\': [\'z\'], \'coefficient\': [1]}}]}]
        # [[-0.5579891, 0.9568383,-0.5070163],
        #  [-0.5579891, 0.9568383,-0.5070163]]
        # [[0.7025831],
        #  [0.7025831]]



    '''

compiles_rules: Incomplete

def compile(op_history, compile_rules=...): ...
def wrapper_compile(f, compile_rules=...):
    '''
    Use compile rules to optimize QModule\'s circuits.

    :param f: QModule\'s forward function.
    :param compile_rules: compile rules,default:[commute_controlled_right, merge_rotations, single_qubit_ops_fuse]

    Example::

        from functools import partial

        from pyvqnet.qnn.vqc import QModule

        def test_compile_cpu():

            from pyvqnet import tensor
            from pyvqnet.qnn.vqc import QMachine, wrapper_compile
            from pyvqnet import kcomplex128
            from pyvqnet.tensor import adjoint
            import numpy as np
            from pyvqnet.qnn.vqc import single_qubit_ops_fuse, wrapper_single_qubit_op_fuse, pauliy
            
            from pyvqnet.qnn.vqc import QMachine, ry,rz, ControlledPhaseShift,                 rx, S, rot, isingxy,isingzz,isingxx,CSWAP, PauliX, T, MeasureAll, RZ, CZ, PhaseShift, u3, cnot, cry, toffoli, cy
            from pyvqnet.tensor import QTensor, tensor
            import pyvqnet
            import numpy as np
            from pyvqnet.utils import set_random_seed

            import time

            set_random_seed(42)

            class QModel(QModule):
                def __init__(self, num_wires, dtype):
                    super(QModel, self).__init__()

                    self._num_wires = num_wires
                    self._dtype = dtype
                    self.qm = QMachine(num_wires, dtype=dtype)

                    self.cswap = CSWAP(wires=(0, 2, 1))
                    self.cz = CZ(wires=[0, 2])
                    #qml.CZ(wires=[0, 2])
                    self.paulix = PauliX(wires=2)
                    #qml.PauliX(wires=2)
                    self.s = S(wires=0)

                    self.ps = PhaseShift(has_params=True,
                                        trainable=True,
                                        wires=0,
                                        dtype=dtype)

                    self.cps = ControlledPhaseShift(has_params=True,
                                                    trainable=True,
                                                    wires=(1, 0),
                                                    dtype=dtype)
                    self.t = T(wires=0)
                    self.rz = RZ(has_params=True, wires=1, dtype=dtype)

                    self.measure = MeasureAll(obs={
                        "Z0":1
                    })

                @partial(wrapper_compile)
                def forward(self, x, *args, **kwargs):
                    self.qm.reset_states(x.shape[0])
                    self.cz(q_machine=self.qm)
                    self.paulix(q_machine=self.qm)
                    rx(q_machine=self.qm,wires=1,params = x[:,[0]])
                    ry(q_machine=self.qm,wires=1,params = x[:,[1]])
                    rz(q_machine=self.qm,wires=1,params = x[:,[2]])
                    rot(q_machine=self.qm, params=x[:, 0:3], wires=(1, ), use_dagger=True)
                    rot(q_machine=self.qm, params=x[:, 1:4], wires=(1, ), use_dagger=True)
                    isingxy(q_machine=self.qm, params=x[:, [2]], wires=(0, 1))
                    u3(q_machine=self.qm, params=x[:, 0:3], wires=1)
                    self.s(q_machine=self.qm)
                    self.cswap(q_machine=self.qm)
                    cnot(q_machine=self.qm, wires=[0, 1])
                    ry(q_machine=self.qm,wires=2,params = x[:,[1]])
                    pauliy(q_machine=self.qm, wires=1)
                    cry(q_machine=self.qm, params=1 / 2, wires=[0, 1])
                    self.ps(q_machine=self.qm)
                    self.cps(q_machine=self.qm)
                    ry(q_machine=self.qm,wires=2,params = x[:,[1]])
                    rz(q_machine=self.qm,wires=2,params = x[:,[2]])
                    toffoli(q_machine=self.qm, wires=[0, 1, 2])
                    self.t(q_machine=self.qm)

                    cy(q_machine=self.qm, wires=(2, 1))
                    ry(q_machine=self.qm,wires=1,params = x[:,[1]])
                    self.rz(q_machine=self.qm)

                    rlt = self.measure(q_machine=self.qm)

                    return rlt

            import pyvqnet
            import pyvqnet.tensor as tensor
            input_x = tensor.QTensor([[0.1, 0.2, 0.3, 0.4], [0.1, 0.2, 0.3, 0.4]],
                                    dtype=pyvqnet.kfloat64)

            input_x.requires_grad = True

            qunatum_model = QModel(num_wires=3, dtype=pyvqnet.kcomplex128)

            batch_y = qunatum_model(input_x)
            
            batch_y.backward()
            print(batch_y)
            print(input_x.grad)
        # [[0.9985801],
        #  [0.9985801]]
        # [[-0.0058562, 0.       ,-0.0169823,-0.0005782],
        #  [-0.0058562, 0.       ,-0.0169823,-0.0005782]]
    '''
