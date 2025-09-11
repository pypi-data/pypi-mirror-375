from ...device import DEV_CPU as DEV_CPU, DEV_GPU_0 as DEV_GPU_0
from ...distributed import CommController as CommController, all_grad_all_reduce as all_grad_all_reduce, get_local_rank as get_local_rank, post_grad_all_reduce as post_grad_all_reduce
from ...nn.module import Module as Module
from ...qnn.vqc import QuantumLayerAdjoint as QuantumLayerAdjoint
from ...qnn.vqc.qcircuit import vqc_to_originir_list as vqc_to_originir_list
from ...qnn.vqc.qmachine import QMachine as QMachine
from ...qnn.vqc.qop import QModule as QModule
from ...tensor import QTensor as QTensor
from .utils import init_helper as init_helper, split_data as split_data, split_module as split_module
from _typeshed import Incomplete

class DataParallelVQCLayer(Module):
    '''
    Use data paralled to run vqc naive. `Comm_OP` is used to run create N processes, and data is split into `batch_size/N` in every process.


    :param Comm_OP: A communications controller which setup distributed environment.
    :param vqc_module: vqc_module with forward(), qmachine is correctly set.
    :param name: Name of the module. Default is an empty string.
    :return: DataParallelVQCLayer instance.

    Example::

        #mpirun -n 2 python xxx.py

        import pyvqnet.backends

        from pyvqnet.qnn.vqc import QMachine, cnot, rx, rz, ry, MeasureAll
        from pyvqnet.tensor import tensor

        from pyvqnet.distributed import CommController, DataParallelVQCLayer

        from pyvqnet.qnn import *
        from pyvqnet.qnn.vqc import *
        import pyvqnet
        from pyvqnet.nn import Module, Linear
        from pyvqnet.device import DEV_GPU_0


        class QModel(Module):

            def __init__(self, num_wires, num_layer, dtype, grad_mode=""):
                super(QModel, self).__init__()

                self._num_wires = num_wires
                self._dtype = dtype
                self.qm = QMachine(num_wires, dtype=dtype, grad_mode=grad_mode)

                self.measure = MeasureAll(obs=PauliX)
                self.n = num_wires
                self.l = num_layer

            def forward(self, param, *args, **kwargs):
                n = self.n
                l = self.l
                qm = self.qm
                qm.reset_states(param.shape[0])
                j = 0

                for j in range(l):
                    cnot(qm, wires=[j, (j + 1) % l])
                    for i in range(n):
                        rx(qm, i, param[:, 3 * n * j + i])
                    for i in range(n):
                        rz(qm, i, param[:, 3 * n * j + i + n], i)
                    for i in range(n):
                        rx(qm, i, param[:, 3 * n * j + i + 2 * n], i)

                y = self.measure(qm)
                return y


        n = 4
        b = 4
        l = 2

        input = tensor.ones([b, 3 * n * l])

        Comm = CommController("mpi")
        
        input.requires_grad = True
        qunatum_model = QModel(num_wires=n, num_layer=l, dtype=pyvqnet.kcomplex64)
        
        layer = qunatum_model

        layer = DataParallelVQCLayer(
            Comm,
            qunatum_model,
        )
        y = layer(input)
        y.backward()


    '''
    def __init__(self, Comm_OP: CommController, vqc_module: Module, name: str = '') -> None: ...
    def forward(self, x): ...

class DataParallelVQCAdjointLayer(QuantumLayerAdjoint):
    '''
 
    Using data parallel on data batchsize to create a vqc use adjoint layer.
    If we use N nodes to run this Module,
    In every node, `batch_size/N` data run forward and vqc to calculate gradients.

    :param Comm_OP: A communications controller which setup distributed environment.
    :param vqc_module: QuantumLayerAdjoint with forward(), qmachine is correctly set.
    :param name: Name of the module. Default is an empty string.
    :return: A module that can calculate quantum circuits.

    Example::

        #mpirun -n 2 python test.py

        import sys
        sys.path.insert(0,"../../")
        from pyvqnet.distributed import CommController,DataParallelVQCAdjointLayer,        get_local_rank

        from pyvqnet.qnn import *
        from pyvqnet.qnn.vqc import *
        import pyvqnet
        from pyvqnet.nn import Module, Linear
        from pyvqnet.device import DEV_GPU_0

        bsize = 100


        class QModel(Module):
            def __init__(self, num_wires, dtype, grad_mode="adjoint"):
                super(QModel, self).__init__()

                self._num_wires = num_wires
                self._dtype = dtype
                self.qm = QMachine(num_wires, dtype=dtype, grad_mode=grad_mode)
                self.rx_layer = RX(has_params=True, trainable=False, wires=0)
                self.ry_layer = RY(has_params=True, trainable=False, wires=1)
                self.rz_layer = RZ(has_params=True, trainable=False, wires=1)
                self.u1 = U1(has_params=True, trainable=True, wires=[2])
                self.u2 = U2(has_params=True, trainable=True, wires=[3])
                self.u3 = U3(has_params=True, trainable=True, wires=[1])
                self.i = I(wires=[3])
                self.s = S(wires=[3])
                self.x1 = X1(wires=[3])
                self.y1 = Y1(wires=[3])
                self.z1 = Z1(wires=[3])
                self.x = PauliX(wires=[3])
                self.y = PauliY(wires=[3])
                self.z = PauliZ(wires=[3])
                self.swap = SWAP(wires=[2, 3])
                self.cz = CZ(wires=[2, 3])
                self.cr = CR(has_params=True, trainable=True, wires=[2, 3])
                self.rxx = RXX(has_params=True, trainable=True, wires=[2, 3])
                self.rzz = RYY(has_params=True, trainable=True, wires=[2, 3])
                self.ryy = RZZ(has_params=True, trainable=True, wires=[2, 3])
                self.rzx = RZX(has_params=True, trainable=False, wires=[2, 3])
                self.toffoli = Toffoli(wires=[2, 3, 4], use_dagger=True)

                self.h = Hadamard(wires=[1])

                self.iSWAP = iSWAP(wires=[0, 2])
                self.tlayer = T(wires=1)
                self.cnot = CNOT(wires=[0, 1])
                self.measure = MeasureAll(obs={\'Z0\': 2})

            def forward(self, x, *args, **kwargs):
                self.qm.reset_states(x.shape[0])
                self.i(q_machine=self.qm)
                self.s(q_machine=self.qm)
                self.swap(q_machine=self.qm)
                self.cz(q_machine=self.qm)
                self.x(q_machine=self.qm)
                self.x1(q_machine=self.qm)
                self.y(q_machine=self.qm)
                self.y1(q_machine=self.qm)
                self.z(q_machine=self.qm)
                self.z1(q_machine=self.qm)
                self.ryy(q_machine=self.qm)
                self.rxx(q_machine=self.qm)
                self.rzz(q_machine=self.qm)
                self.rzx(q_machine=self.qm, params=x[:, [1]])

                self.u1(q_machine=self.qm)
                self.u2(q_machine=self.qm)
                self.u3(q_machine=self.qm)
                self.rx_layer(params=x[:, [0]], q_machine=self.qm)
                self.cnot(q_machine=self.qm)
                self.h(q_machine=self.qm)
                self.iSWAP(q_machine=self.qm)
                self.ry_layer(params=x[:, [1]], q_machine=self.qm)
                self.tlayer(q_machine=self.qm)
                self.rz_layer(params=x[:, [2]], q_machine=self.qm)
                self.toffoli(q_machine=self.qm)
                rlt = self.measure(q_machine=self.qm)

                return rlt


        pyvqnet.utils.set_random_seed(42)

        Comm_OP = CommController("mpi")

        input_x = tensor.QTensor([[0.1, 0.2, 0.3]])
        input_x = tensor.broadcast_to(input_x, [bsize, 3])
        input_x.requires_grad = True

        qunatum_model = QModel(num_wires=6, dtype=pyvqnet.kcomplex64)

        l = DataParallelVQCAdjointLayer(
            Comm_OP,
            qunatum_model,
        )

        y = l(input_x)

        y.backward()

 
    '''
    qm: Incomplete
    def __init__(self, Comm_OP: CommController, vqc_module: Module, name: str = '') -> None: ...
    def forward(self, x): ...
