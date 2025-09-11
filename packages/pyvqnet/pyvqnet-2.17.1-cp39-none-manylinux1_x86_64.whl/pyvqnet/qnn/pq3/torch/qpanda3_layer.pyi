from ....nn.torch import TorchModule as TorchModule
from ....tensor import QTensor as QTensor, to_tensor as to_tensor
from ....torch import unary_operators_preprocess as unary_operators_preprocess
from ...pq3.hybird_vqc_qpanda import HybirdVQCQpandaQVMLayer as NHybirdVQCQpandaQVMLayer, VQCQpandaForwardLayer as NVQCQpandaForwardLayer
from ...pq3.pq_utils import PQ_QCLOUD_UTILS as PQ_QCLOUD_UTILS, pq3_vqc_run as pq3_vqc_run
from ...pq3.quantumlayer import QuantumBatchAsyncQcloudLayer as NQuantumBatchAsyncQcloudLayer, QuantumLayerV2 as NQuantumLayerV2
from .qpanda_layer import TorchQcloudQuantumLayer as NTorchQcloudQuantumLayer, TorchQpandaFunctionHelper as TorchQpandaFunctionHelper, _TorchQuantumLayer
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock
from typing import Callable

class TorchQcloud3QuantumLayer(NQuantumBatchAsyncQcloudLayer, NTorchQcloudQuantumLayer):
    '''

    A torch.nn.module that can use originqc qcloud to do vqc training.
    Abstract Calculation module for originqc real chip using pyqpanda3 QCLOUD. It submit parameterized quantum
    circuits to real chip and get the measurement result.

    .. note::

        This class is for torch backend and pyqpanda3 only!

    :param origin_qprog_func: callable quantum circuits function constructed by QPanda.
    :param qcloud_token: `str` - Either the type of quantum machine or the cloud token for execution.
    :param para_num: `int` - Number of parameters; parameters are one-dimensional.
    :param pauli_str_dict: `dict|list` - Dictionary or list of dictionary representing the Pauli operators in the quantum circuit. Default is None.
    :param shots: `int` - Number of measurement shots. Default is 1000.
    :param initializer: Initializer for parameter values. Default is None.
    :param dtype: Data type of parameters. Default is None, which uses the default data type.
    :param name: Name of the module. Default is an empty string.
    :param diff_method: Differentiation method for gradient computation. Default is "parameter_shift".
    IF diff_method == "random_coordinate_descent", we will random choice single parameters to calculate gradients, other will keep zero. reference: https://arxiv.org/abs/2311.00088
    :param submit_kwargs: Additional keyword arguments for submitting quantum circuits,
    default:{"chip_id":"origin_wukong","is_amend":True,"is_mapping":True,
    "is_optimization": True,"default_task_group_size":200,"test_qcloud_fake":True}.
    :param query_kwargs: Additional keyword arguments for querying quantum results，default:{"timeout":1,"print_query_info":True,"sub_circuits_split_size":1}.
    :return: A module that can calculate quantum circuits.

    Example::

    
        import pyqpanda3.core as pq
        import pyvqnet
        from pyvqnet.qnn.vqc.torch import TorchQcloud3QuantumLayer

        pyvqnet.backends.set_backend("torch")
        def qfun(input,param):

            m_qlist = range(6)
            cubits = range(6)
            measure_qubits = [0,2]
            m_prog = pq.QProg()
            cir = pq.QCircuit()
            cir<<pq.RZ(m_qlist[0],input[0])
            cir<<pq.CNOT(m_qlist[0],m_qlist[1])
            cir<<pq.RY(m_qlist[1],param[0])
            cir<<pq.CNOT(m_qlist[0],m_qlist[2])
            cir<<pq.RZ(m_qlist[1],input[1])
            cir<<pq.RY(m_qlist[2],param[1])
            cir<<pq.H(m_qlist[2])
            m_prog<<cir

            for idx, ele in enumerate(measure_qubits):
                m_prog << pq.measure(m_qlist[ele], cubits[idx])  # pylint: disable=expression-not-assigned
            return m_prog

        l = TorchQcloud3QuantumLayer(qfun,
                        "3047DE8A59764BEDAC9C3282093B16AF1",
                        2,
                        pauli_str_dict=None,
                        shots = 1000,
                        initializer=None,
                        dtype=None,
                        name="",
                        diff_method="parameter_shift",
                        submit_kwargs={"test_qcloud_fake":True},
                        query_kwargs={})
        x = pyvqnet.tensor.QTensor([[0.56,1.2],[0.56,1.2],[0.56,1.2],[0.56,1.2],[0.56,1.2]],requires_grad= True)
        y = l(x)
        print(y)
        y.backward()
        print(l.m_para.grad)
        print(x.grad)

        def qfun2(input,param ):

            m_qlist = range(6)
            cubits = range(6)
            measure_qubits = [0,2]
            m_prog = pq.QProg()
            cir = pq.QCircuit()
            cir<<pq.RZ(m_qlist[0],input[0])
            cir<<pq.CNOT(m_qlist[0],m_qlist[1])
            cir<<pq.RY(m_qlist[1],param[0])
            cir<<pq.CNOT(m_qlist[0],m_qlist[2])
            cir<<pq.RZ(m_qlist[1],input[1])
            cir<<pq.RY(m_qlist[2],param[1])
            cir<<pq.H(m_qlist[2])
            m_prog<<cir

            return m_prog
        l = TorchQcloud3QuantumLayer(qfun2,
                "3047DE8A59764BEDAC9C3282093B16AF",
                2,

                pauli_str_dict={\'Z0 X1\':10,\'\':-0.5,\'Y2\':-0.543},
                shots = 1000,
                initializer=None,
                dtype=None,
                name="",
                diff_method="parameter_shift",
                submit_kwargs={"test_qcloud_fake":True},
                query_kwargs={})
        x = pyvqnet.tensor.QTensor([[0.56,1.2],[0.56,1.2],[0.56,1.2],[0.56,1.2]],requires_grad= True)
        y = l(x)
        print(y)
        y.backward()
        print(l.m_para.grad)
        print(x.grad)

    '''
    eqc_w_index: int
    def __init__(self, origin_qprog_func: Callable, qcloud_token: str, para_num: int, pauli_str_dict: list[dict] | dict | None = None, shots: int = 1000, initializer: Callable = None, dtype: int | None = None, name: str = '', diff_method: str = 'parameter_shift', submit_kwargs: dict = {}, query_kwargs: dict = {}) -> None: ...
    def forward(self, x): ...

class TorchQpanda3QuantumLayer(_TorchQuantumLayer, NQuantumLayerV2):
    '''

    Calculation module for Variational Quantum Layer. It simulate a parameterized quantum
    circuit and get the measurement result. It inherits from Module,so that it can calculate
    gradients of circuits parameters,and trains Variational Quantum Circuits model or embeds
    Variational Quantum Circuits into hybird Quantum and Classic model.

    .. note::

        This class is for torch backend and pyqpanda3 only!


    :param qprog_with_measure: callable quantum circuits functions ,cosntructed by qpanda
    :param para_num: `int` - Number of parameter
    :param diff_method: \'parameter_shift\' or \'finite_diff\'
    :param delta:  delta for diff

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a module can calculate quantum circuits .

    Note:
        qprog_with_measure is quantum circuits function defined in pyQPanda :
         https://qcloud.originqc.com.cn/document/qpanda-3/db/d6c/tutorial_circuit_and_program.html.


        qprog_with_measure (input,param)

            `input`: array_like input 1-dim classic data

            `param`: array_like input 1-dim quantum circuit\'s parameters

    Example::

        import pyqpanda3.core as pq
        from pyvqnet.qnn.pq3 import ProbsMeasure
        import numpy as np
        from pyvqnet.tensor import QTensor
        import pyvqnet
        pyvqnet.backends.set_backend("torch")
        from pyvqnet.qnn.vqc.torch import TorchQpanda3QuantumLayer
        def pqctest (input,param):
            num_of_qubits = 4

            m_machine = pq.CPUQVM()# outside
        
            qubits =range(num_of_qubits)

            circuit = pq.QCircuit()
            circuit<<pq.H(qubits[0])
            circuit<<pq.H(qubits[1])
            circuit<<pq.H(qubits[2])
            circuit<<pq.H(qubits[3])

            circuit<<pq.RZ(qubits[0],input[0])
            circuit<<pq.RZ(qubits[1],input[1])
            circuit<<pq.RZ(qubits[2],input[2])
            circuit<<pq.RZ(qubits[3],input[3])

            circuit<<pq.CNOT(qubits[0],qubits[1])
            circuit<<pq.RZ(qubits[1],param[0])
            circuit<<pq.CNOT(qubits[0],qubits[1])

            circuit<<pq.CNOT(qubits[1],qubits[2])
            circuit<<pq.RZ(qubits[2],param[1])
            circuit<<pq.CNOT(qubits[1],qubits[2])

            circuit<<pq.CNOT(qubits[2],qubits[3])
            circuit<<pq.RZ(qubits[3],param[2])
            circuit<<pq.CNOT(qubits[2],qubits[3])
            #print(circuit)

            prog = pq.QProg()
            prog<<circuit

            rlt_prob = ProbsMeasure(m_machine,prog,[0,2])
            return rlt_prob

        pqc = TorchQpanda3QuantumLayer(pqctest,3)

        #classic data as input
        input = QTensor([[1.0,2,3,4],[4,2,2,3],[3,3,2,2]],requires_grad=True)

        #forward circuits
        rlt = pqc(input)

        print(rlt)

        grad =  QTensor(np.ones(rlt.data.shape)*1000)
        #backward circuits
        rlt.backward(grad)

        print(pqc.m_para.grad)
        print(input.grad)


    '''
    def __init__(self, qprog_with_measure: Callable, para_num: int, diff_method: str = 'parameter_shift', delta: float = 0.01, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...

class HybirdVQCQpanda3QVMLayer(TorchModule, NHybirdVQCQpandaQVMLayer):
    '''
    Torch backend api for HybirdVQCQpandaQVMLayer.
    
    Hybird vqc and qpanda QVM layer.use qpanda qvm to run forward and use vqc to calculate gradients.

    :param vqc_module: vqc_module with forward(), qmachine is correctly set.
    :param qcloud_token: `str` - Either the type of quantum machine or the cloud token for execution.
    :param pauli_str_dict: `dict|list` - Dictionary or list of dictionary representing the Pauli operators in the quantum circuit. Default is None.
    :param shots: `int` - Number of measurement shots. Default is 1000.
    :param name: Name of the module. Default is an empty string.
    :param submit_kwargs: Additional keyword arguments for submitting quantum circuits,
    default:{"chip_id":"origin_wukong","is_amend":True,"is_mapping":True,
    "is_optimization": True,"default_task_group_size":200,"test_qcloud_fake":True}.
    :param query_kwargs: Additional keyword arguments for querying quantum results，default:{"timeout":1,"print_query_info":True,"sub_circuits_split_size":1}.
    :return: A module that can calculate quantum circuits.

    .. note::
        pauli_str_dict should not be None, and it should be same as obs in vqc_module measure function.
        vqc_module should have attribute with type of QMachine, QMachine should set save_ir=True

    .. note::

        This class is for torch backend and pyqpanda3 only!

    Example::

        import pyvqnet.backends
        import numpy as np
        from pyvqnet.qnn.vqc.torch import QMachine,QModule,RX,RY,        RZ,U1,U2,U3,I,S,X1,PauliX,PauliY,PauliZ,SWAP,CZ,        RXX,RYY,RZX,RZZ,CR,Toffoli,Hadamard,T,CNOT,MeasureAll
        from pyvqnet.qnn.vqc.torch import HybirdVQCQpanda3QVMLayer
        import pyvqnet

        from pyvqnet import tensor

        import pyvqnet.utils
        pyvqnet.backends.set_backend("torch")
        pyvqnet.utils.set_random_seed(42)

        class QModel(QModule):
            def __init__(self, num_wires, dtype,grad_mode=""):
                super(QModel, self).__init__()

                self._num_wires = num_wires
                self._dtype = dtype
                self.qm = QMachine(num_wires, dtype=dtype,grad_mode=grad_mode,save_ir=True)
                self.rx_layer = RX(has_params=True, trainable=False, wires=0)
                self.ry_layer = RY(has_params=True, trainable=False, wires=1)
                self.rz_layer = RZ(has_params=True, trainable=False, wires=1)
                self.u1 = U1(has_params=True,trainable=True,wires=[2])
                self.u2 = U2(has_params=True,trainable=True,wires=[3])
                self.u3 = U3(has_params=True,trainable=True,wires=[1])
                self.i = I(wires=[3])
                self.s = S(wires=[3])
                self.x1 = X1(wires=[3])
                
                self.x = PauliX(wires=[3])
                self.y = PauliY(wires=[3])
                self.z = PauliZ(wires=[3])
                self.swap = SWAP(wires=[2,3])
                self.cz = CZ(wires=[2,3])
                self.cr = CR(has_params=True,trainable=True,wires=[2,3])
                self.rxx = RXX(has_params=True,trainable=True,wires=[2,3])
                self.rzz = RYY(has_params=True,trainable=True,wires=[2,3])
                self.ryy = RZZ(has_params=True,trainable=True,wires=[2,3])
                self.rzx = RZX(has_params=True,trainable=False, wires=[2,3])
                self.toffoli = Toffoli(wires=[2,3,4],use_dagger=True)
                self.h =Hadamard(wires=[1])


                self.tlayer = T(wires=1)
                self.cnot = CNOT(wires=[0, 1])
                self.measure = MeasureAll(obs={\'Z0\':2,\'Y3\':3} 
            )

            def forward(self, x, *args, **kwargs):
                self.qm.reset_states(x.shape[0])
                self.i(q_machine=self.qm)
                self.s(q_machine=self.qm)
                self.swap(q_machine=self.qm)
                self.cz(q_machine=self.qm)
                self.x(q_machine=self.qm)
                self.x1(q_machine=self.qm)
                self.y(q_machine=self.qm)

                self.z(q_machine=self.qm)

                self.ryy(q_machine=self.qm)
                self.rxx(q_machine=self.qm)
                self.rzz(q_machine=self.qm)
                self.rzx(q_machine=self.qm,params = x[:,[1]])
                self.cr(q_machine=self.qm)
                self.u1(q_machine=self.qm)
                self.u2(q_machine=self.qm)
                self.u3(q_machine=self.qm)
                self.rx_layer(params = x[:,[0]], q_machine=self.qm)
                self.cnot(q_machine=self.qm)
                self.h(q_machine=self.qm)

                self.ry_layer(params = x[:,[1]], q_machine=self.qm)
                self.tlayer(q_machine=self.qm)
                self.rz_layer(params = x[:,[2]], q_machine=self.qm)
                self.toffoli(q_machine=self.qm)
                rlt = self.measure(q_machine=self.qm)

                return rlt
            

        input_x = tensor.QTensor([[0.1, 0.2, 0.3]])

        input_x = tensor.broadcast_to(input_x,[2,3])

        input_x.requires_grad = True

        qunatum_model = QModel(num_wires=6, dtype=pyvqnet.kcomplex64)

        l = HybirdVQCQpanda3QVMLayer(qunatum_model,
                                "3047DE8A59764BEDAC9C3282093B16AF1",

                    pauli_str_dict={\'Z0\':2,\'Y3\':3},
                    shots = 1000,
                    name="",
            submit_kwargs={"test_qcloud_fake":True},
                    query_kwargs={})

        y = l(input_x)
        print(y)

        y.backward()
        print(input_x.grad)
    '''
    def __init__(self, vqc_module, qcloud_token: str, pauli_str_dict: list[dict] | dict | None = None, shots: int = 1000, name: str = '', diff_method: str = '', submit_kwargs: dict = {}, query_kwargs: dict = {}) -> None: ...

class VQCQpandaForwardLayer(NVQCQpandaForwardLayer):
    '''
 
    This class performs only forward computation (no backward propagation).
    It converts a Variational Quantum Circuit (VQC) module to a QPanda quantum program (QProg)
    and executes it on either QCloud or a local CPU quantum virtual machine (CPUQVM).

    :param vqc_module: A QModule quantum module representing the variational quantum circuit.
    :type vqc_module: Module

    :param qcloud_token: Authentication token for accessing QCloud services.
    :type qcloud_token: str

    :param pauli_str_dict: A dictionary or list of dictionaries defining the Hamiltonian in Pauli representation.
                        This is used for expectation value calculations.
    :type pauli_str_dict: Union[List[Dict], Dict, None], optional

    :param shots: Number of measurement shots used in quantum computation. Default is 1000.
    :type shots: int, optional

    :param name: An optional name identifier for the quantum circuit execution.
    :type name: str, optional

    :param submit_kwargs: Additional keyword arguments for submitting tasks to QCloud.
    :type submit_kwargs: Dict, optional

    :param query_kwargs: Additional keyword arguments for querying execution results from QCloud.
    :type query_kwargs: Dict, optional

    Example::

        from pyvqnet.qnn.vqc.torch  import *
        
        from pyvqnet.qnn.vqc.torch import TorchVQCQpandaForwardLayer
        import pyvqnet
        from pyvqnet import tensor
        
        pyvqnet.backends.set_backend("torch")

        class QModel(QModule):
            def __init__(self, num_wires, dtype,grad_mode=""):
                super(QModel, self).__init__()

                self._num_wires = num_wires
                self._dtype = dtype
                
                self.qm = QMachine(num_wires, dtype=dtype,grad_mode=grad_mode,save_ir=True)
                self.qm.set_just_defined(True)
                self.T = T(wires=[3])
                self.rx_layer = RX(has_params=True, trainable=False, wires=0)
                self.ry_layer = RY(has_params=True, trainable=False, wires=1)
                self.rz_layer = RZ(has_params=True, trainable=False, wires=1)
                self.u1 = U1(has_params=True,trainable=True,wires=[2])
                self.u2 = U2(has_params=True,trainable=True,wires=[3])
                self.u3 = U3(has_params=True,trainable=True,wires=[1])
                self.i = I(wires=[3])
                self.s = S(wires=[3])
                self.x1 = X1(wires=[3])
                self.y1 = Y1(wires=[3])
                self.z1 = Z1(wires=[3])
                self.x = PauliX(wires=[3])
                self.y = PauliY(wires=[3])
                self.z = PauliZ(wires=[3])
                self.swap = SWAP(wires=[2,3])
                self.cz = CZ(wires=[2,3])
                self.cr = CR(has_params=True,trainable=True,wires=[2,3])
                self.rxx = RXX(has_params=True,trainable=True,wires=[2,3])
                self.rzz = RYY(has_params=True,trainable=True,wires=[2,3])
                self.ryy = RZZ(has_params=True,trainable=True,wires=[2,3])
                self.rzx = RZX(has_params=True,trainable=False, wires=[2,3])
                self.toffoli = Toffoli(wires=[2,3,4],use_dagger=True)
                    
                self.h =Hadamard(wires=[1])
                self.rot = VQC_HardwareEfficientAnsatz(6, ["rx", "RY", "rz"],
                                                    entangle_gate="cnot",
                                                    entangle_rules="linear",
                                                    depth=5)
                
                self.iSWAP =iSWAP(wires=[0,2])
                self.tlayer = T(wires=1)
                self.cnot = CNOT(wires=[0, 1])
                self.measure = MeasureAll(obs = {f"Z{i}": 1 for i in range(num_wires)})

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
                self.rzx(q_machine=self.qm,params = x[:,[1]])
                self.cr(q_machine=self.qm)
                self.u1(q_machine=self.qm)
                self.u2(q_machine=self.qm)
                self.u3(q_machine=self.qm)
                self.rx_layer(params = x[:,[0]], q_machine=self.qm)
                self.cnot(q_machine=self.qm)
                self.h(q_machine=self.qm)
                self.iSWAP(q_machine=self.qm)
                self.ry_layer(params = x[:,[1]], q_machine=self.qm)
                self.tlayer(q_machine=self.qm)
                self.rz_layer(params = x[:,[2]], q_machine=self.qm)
                self.toffoli(q_machine=self.qm)
                #rlt = self.measure(q_machine=self.qm)

                return x
            

        input_x = tensor.QTensor([[0.1, 0.2, 0.3]])

        input_x = tensor.broadcast_to(input_x,[2,3])

        input_x.requires_grad = True

        qunatum_model = QModel(num_wires=5, dtype=pyvqnet.kcomplex64)

        num_wires =5
        d = {}
        dl = []
        for f in range(num_wires):
            d["Z"+str(f)]=1
            dl.append(d)
        fw = TorchVQCQpandaForwardLayer(qunatum_model,"fake",pauli_str_dict=dl,submit_kwargs={"test_qcloud_fake":True})
        y = fw(input_x)

    '''
    def __init__(self, vqc_module, qcloud_token: str, pauli_str_dict: list[dict] | dict | None = None, shots: int = 1000, name: str = '', submit_kwargs: dict = {}, query_kwargs: dict = {}) -> None: ...
TorchVQCQpandaForwardLayer = VQCQpandaForwardLayer
TorchHybirdVQCQpanda3QVMLayer = HybirdVQCQpanda3QVMLayer

class TorchQpandaVQCFunctionHelper(TorchQpandaFunctionHelper):
    @staticmethod
    def forward(ctx, x, weights, qlayer): ...
    @staticmethod
    def backward(ctx, grad_output): ...

class TorchQpanda3AdjointQuantumLayer(TorchQpanda3QuantumLayer):
    '''
    This class uses the VQCircuit interface https://qcloud.originqc.com.cn/document/qpanda-3/d8/d94/tutorial_variational_quantum_circuit.html of pyqpanda3 and the adjoint method to calculate the gradient of parameters in quantum circuits relative to the Hamiltonian. It supports batch input and multiple Hamiltonian outputs.
        
        .. note::

            When using this interface, you must use the logic gates under VQCircuit to build the circuit. 
            
            Currently, the supported logic gates are limited and an exception will be thrown if they are not supported.
            
            The input parameter ``pq3_vqc_circuit`` must only contain two parameters `x` and `param`, which are one-dimensional arrays or lists. 
            
            In the ``pq3_vqc_circuit`` function, the user must customize how to handle input and parameters using ``pyqpanda3.vqcircuit.VQCircuit().set_Param``.
            
            In addition, the number of parameters needs to be pre-entered by the user into ``param_num``. This interface will initialize a parameter ``m_para`` with a length of `param_num`.
            
            Please refer to the example below.


        :param pq3_vqc_circuit: Customized pyqpanda3 VQCircuit circuit.
        :param param_num: number of parameters.
        :param pauli_dicts: expected observations, can be a list.
        :param dtype: parameter type, kfloat32 or kfloat64, default: None, use kfloat32.
        :param name: name of this interface.

        Example::

            from pyvqnet.qnn.vqc.torch  import Qpanda3AdjointGradientQuantumLayer
            from pyvqnet import tensor
            from pyvqnet.qnn.pq3.torch import TorchQpanda3QuantumLayer as QuantumLayer
            from pyvqnet.qnn.pq3 import expval
            from pyqpanda3.vqcircuit import VQCircuit
            import pyqpanda3 as pq3

            import pyvqnet
            pyvqnet.backends.set_backend("torch")

            l = 1
            n = 5
            Xn_string = \' \'.join([f\'X{i}\' for i in range(n)])
            pauli_dict  = {Xn_string:1.}

            def pqctest(x,param):
                vqc = VQCircuit()
                vqc.set_Param([len(param) +len(x)])
                w_offset = len(x)
                for j in range(len(x)):
                    vqc << pq3.core.RX(j, vqc.Param([j]))
                for j in range(l):
                    for i in range(n - 1):
                        vqc << pq3.core.CNOT(i, i + 1)
                    for i in range(n):
                        vqc << pq3.core.RX(i, vqc.Param([w_offset + 3 * n * j + i]))
                        
                        vqc << pq3.core.RZ(i, vqc.Param([w_offset + 3 * n * j + i + n]))
                        vqc << pq3.core.RY(i, vqc.Param([w_offset + 3 * n * j + i + 2 * n]))
                
                return vqc


            pyvqnet.utils.set_random_seed(42)
            layer = Qpanda3AdjointGradientQuantumLayer(pqctest,3*l*n,pauli_dict)

            x = tensor.randn([2,5])
            x.requires_grad = True

            
            y = layer(x)
        
            y.backward()
        
            pq3_p_grad = layer.m_para.grad.numpy()
            pq3_x_grad = x.grad.numpy()

    '''
    pauli_dicts: Incomplete
    def __init__(self, qprog_with_measure: Callable, para_num: int, pauli_dicts, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...
Qpanda3AdjointGradientQuantumLayer = TorchQpanda3AdjointQuantumLayer
