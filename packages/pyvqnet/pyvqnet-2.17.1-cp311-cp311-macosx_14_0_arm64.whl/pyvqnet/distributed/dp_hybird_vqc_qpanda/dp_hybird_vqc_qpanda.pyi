from ...qnn.pq_utils import *
from ...qnn.quantumlayer import *
from ...distributed import CommController as CommController
from ...nn.module import Module as Module
from ...qnn.vqc.qcircuit import vqc_to_originir_list as vqc_to_originir_list
from ...tensor import QTensor as QTensor
from .utils import init_helper as init_helper, split_data as split_data
from _typeshed import Incomplete

class DataParallelHybirdVQCQpandaQVMLayer(QuantumLayerBase):
    '''
 
    Using data parallel on data batchsize to create a Hybird vqc and qpanda QVM layer.
    If we use N nodes to run this Module,
    In every node, `batch_size/N` data are use pyQPanda qvm to run forward and vqc to calculate gradients.

    :param Comm_OP: A communications controller which setup distributed environment.
    :param vqc_module: vqc_module with forward(), qmachine is correctly set.
    :param qcloud_token: `str` - Either the type of quantum machine or the cloud token for execution.
    :param num_qubits: `int` - Number of qubits in the quantum circuit.
    :param num_cubits: `int` - Number of classical bits for measurement in the quantum circuit.
    :param pauli_str_dict: `dict|list` - Dictionary or list of dictionary representing the Pauli operators in the quantum circuit. Default is None.
    :param shots: `int` - Number of measurement shots. Default is 1000.
    :param name: Name of the module. Default is an empty string.
    :param submit_kwargs: Additional keyword arguments for submitting quantum circuits,
    default:{"chip_id":pyqpanda.real_chip_type.origin_72,"is_amend":True,"is_mapping":True,
    "is_optimization": True,"default_task_group_size":200,"test_qcloud_fake":True}.
    :param query_kwargs: Additional keyword arguments for querying quantum results，default:{"timeout":1,"print_query_info":True,"sub_circuits_split_size":1}.
    :return: A module that can calculate quantum circuits.

    .. note::
        pauli_str_dict should not be None, and it should be same as obs in vqc_module measure function.
        vqc_module should have attribute with type of QMachine, QMachine should set save_ir=True

    Example::

        #mpirun -n 2 python hybird_qpanda_vqc_demo_mpi.py
        import sys
        sys.path.insert(0,"../../")
        from pyvqnet.distributed import *

        Comm_OP = CommController("mpi")
        from pyvqnet.qnn import *
        from pyvqnet.qnn.vqc import *
        import pyvqnet
        from pyvqnet.nn import Module, Linear
        from pyvqnet.device import DEV_GPU_0
        pyvqnet.utils.set_random_seed(42)


        class Hybird(Module):
            def __init__(self):
                self.cl1 = Linear(3, 3)
                self.ql = QModel(num_wires=6, dtype=pyvqnet.kcomplex64)
                self.cl2 = Linear(1, 2)

            def forward(self, x):
                x = self.cl1(x)
                x = self.ql(x)
                x = self.cl2(x)
                return x


        class QModel(Module):
            def __init__(self, num_wires, dtype, grad_mode=""):
                super(QModel, self).__init__()

                self._num_wires = num_wires
                self._dtype = dtype
                self.qm = QMachine(num_wires,
                                dtype=dtype,
                                grad_mode=grad_mode,
                                save_ir=True)
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
                self.measure = MeasureAll(obs={\'Z0\': 2, \'Y3\': 3})

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
                self.cr(q_machine=self.qm)
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


        input_x = tensor.QTensor([[0.1, 0.2, 0.3]])
        input_x = tensor.broadcast_to(input_x, [20, 3])
        input_x.requires_grad = True



        qunatum_model = QModel(num_wires=6, dtype=pyvqnet.kcomplex64)

        l = DataParallelHybirdVQCQpandaQVMLayer(
            Comm_OP,
            qunatum_model,
            "3047DE8A59764BEDAC9C3282093B16AF1",

            num_qubits=6,
            num_cubits=6,
            pauli_str_dict={
                \'Z0\': 2,
                \'Y3\': 3
            },
            shots=1000,
            name="",
            submit_kwargs={"test_qcloud_fake": True},
            query_kwargs={})

        y = l(input_x)
        print(y)
        y.backward()
        for p in qunatum_model.parameters():
            print(p.grad)

 
    '''
    pauli_str_dict: Incomplete
    pq_utils: Incomplete
    submit_kwargs: Incomplete
    query_kwargs: Incomplete
    shots: Incomplete
    m_machine: Incomplete
    qlists: Incomplete
    clists: Incomplete
    def __init__(self, Comm_OP: CommController, vqc_module: Module, qcloud_token: str, num_qubits: int, num_cubits: int, pauli_str_dict: list[dict] | dict | None = None, shots: int = 1000, name: str = '', diff_method: str = '', submit_kwargs: dict = {}, query_kwargs: dict = {}) -> None: ...
    query_by_taskid_sync_batched: Incomplete
    submit_task_asyn_batched: Incomplete
    calc_exp_asyn_batched: Incomplete
    calc_qmeasure_asyn_batched: Incomplete
    calc_split_circuits_exp_asyn_batched: Incomplete
    def set_dummy(self, is_dummy) -> None: ...
    def forward(self, x): ...
