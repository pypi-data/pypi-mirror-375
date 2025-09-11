import torch
from ....device import DEV_CPU as DEV_CPU
from ....nn.torch import TorchModule as TorchModule
from ....tensor import QTensor as QTensor, to_tensor as to_tensor
from ....torch import unary_operators_preprocess as unary_operators_preprocess
from ....utils.initializer import quantum_uniform as quantum_uniform
from ...pq_utils import PQ_QCLOUD_UTILS as PQ_QCLOUD_UTILS
from ...quantumlayer import QuantumBatchAsyncQcloudLayer as NQuantumBatchAsyncQcloudLayer, QuantumLayerV2 as NQuantumLayerV2
from _typeshed import Incomplete
from collections import defaultdict as defaultdict, deque as deque
from pyvqnet.backends_mock import TorchMock as TorchMock
from typing import Callable

class _TorchQuantumLayer(TorchModule): ...

class TorchQcloudQuantumLayer(_TorchQuantumLayer, NQuantumBatchAsyncQcloudLayer):
    '''

    A torch.nn.module that can use originqc qcloud to do vqc training.
    Abstract Calculation module for originqc real chip using pyqpanda QCLOUD from version 3.8.2.2. It submit parameterized quantum
    circuits to real chip and get the measurement result.

    :param origin_qprog_func: callable quantum circuits function constructed by QPanda.
    :param qcloud_token: `str` - Either the type of quantum machine or the cloud token for execution.
    :param para_num: `int` - Number of parameters; parameters are one-dimensional.
    :param num_qubits: `int` - Number of qubits in the quantum circuit.
    :param num_cubits: `int` - Number of classical bits for measurement in the quantum circuit.
    :param pauli_str_dict: `dict|list` - Dictionary or list of dictionary representing the Pauli operators in the quantum circuit. Default is None.
    :param shots: `int` - Number of measurement shots. Default is 1000.
    :param initializer: Initializer for parameter values. Default is None.
    :param dtype: Data type of parameters. Default is None, which uses the default data type.
    :param name: Name of the module. Default is an empty string.
    :param diff_method: Differentiation method for gradient computation. Default is "parameter_shift".
    IF diff_method == "random_coordinate_descent", we will random choice single parameters to calculate gradients, other will keep zero. reference: https://arxiv.org/abs/2311.00088
    :param submit_kwargs: Additional keyword arguments for submitting quantum circuits,
    default:{"chip_id":pyqpanda.real_chip_type.origin_72,"is_amend":True,"is_mapping":True,
    "is_optimization": True,"default_task_group_size":200,"test_qcloud_fake":True}.
    :param query_kwargs: Additional keyword arguments for querying quantum results，default:{"timeout":1,"print_query_info":True,"sub_circuits_split_size":1}.
    :return: A module that can calculate quantum circuits.
    Example::

    
        import pyqpanda as pq
        import pyvqnet
        from pyvqnet.qnn.vqc.torch import TorchQcloudQuantumLayer

        pyvqnet.backends.set_backend("torch")
        def qfun(input,param, m_machine, m_qlist,cubits):
            measure_qubits = [0,2]
            m_prog = pq.QProg()
            cir = pq.QCircuit()
            cir.insert(pq.RZ(m_qlist[0],input[0]))
            cir.insert(pq.CNOT(m_qlist[0],m_qlist[1]))
            cir.insert(pq.RY(m_qlist[1],param[0]))
            cir.insert(pq.CNOT(m_qlist[0],m_qlist[2]))
            cir.insert(pq.RZ(m_qlist[1],input[1]))
            cir.insert(pq.RY(m_qlist[2],param[1]))
            cir.insert(pq.H(m_qlist[2]))
            m_prog.insert(cir)

            for idx, ele in enumerate(measure_qubits):
                m_prog << pq.Measure(m_qlist[ele], cubits[idx])  # pylint: disable=expression-not-assigned
            return m_prog

        l = TorchQcloudQuantumLayer(qfun,
                        "3047DE8A59764BEDAC9C3282093B16AF1",
                        2,
                        6,
                        6,
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

        def qfun2(input,param, m_machine, m_qlist,cubits):
            measure_qubits = [0,2]
            m_prog = pq.QProg()
            cir = pq.QCircuit()
            cir.insert(pq.RZ(m_qlist[0],input[0]))
            cir.insert(pq.CNOT(m_qlist[0],m_qlist[1]))
            cir.insert(pq.RY(m_qlist[1],param[0]))
            cir.insert(pq.CNOT(m_qlist[0],m_qlist[2]))
            cir.insert(pq.RZ(m_qlist[1],input[1]))
            cir.insert(pq.RY(m_qlist[2],param[1]))
            cir.insert(pq.H(m_qlist[2]))
            m_prog.insert(cir)

            return m_prog
        l = TorchQcloudQuantumLayer(qfun2,
                "3047DE8A59764BEDAC9C3282093B16AF",
                2,
                6,
                6,
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
    m_machine: Incomplete
    qlists: Incomplete
    clists: Incomplete
    def __init__(self, origin_qprog_func: Callable, qcloud_token: str, para_num: int, num_qubits: int, num_cubits: int, pauli_str_dict: list[dict] | dict | None = None, shots: int = 1000, initializer: Callable = None, dtype: int | None = None, name: str = '', diff_method: str = 'parameter_shift', submit_kwargs: dict = {}, query_kwargs: dict = {}) -> None: ...
    def forward(self, x): ...

class TorchQcloudFunctionHelper(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, weights, qlayer): ...
    @staticmethod
    def backward(ctx, grad_output): ...

class TorchQpandaQuantumLayer(_TorchQuantumLayer, NQuantumLayerV2):
    '''
    torch api for quantumlayerv2

    Calculation module for Variational Quantum Layer. It simulate a parameterized quantum
    circuit and get the measurement result. It inherits from Module,so that it can calculate
    gradients of circuits parameters,and trains Variational Quantum Circuits model or embeds
    Variational Quantum Circuits into hybird Quantum and Classic model.

    You need to allocated simulation machine and qubits by yourself.

    :param qprog_with_measure: callable quantum circuits functions ,cosntructed by qpanda
    :param para_num: `int` - Number of parameter
    :param diff_method: \'parameter_shift\' or \'finite_diff\'
    :param delta:  delta for diff

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a module can calculate quantum circuits .

    Note:
        qprog_with_measure is quantum circuits function defined in pyQPanda :
         https://pyqpanda-toturial.readthedocs.io/zh/latest/QCircuit.html.

        This function should contains following parameters,otherwise it can not run
         properly in TorchQpandaQuantumLayer.

        Compare to QuantumLayer.you should allocate qubits and simulator:
         https://pyqpanda-toturial.readthedocs.io/zh/latest/QuantumMachine.html,

        you may also need to allocate cubits if qprog_with_measure needs quantum
         measure:https://pyqpanda-toturial.readthedocs.io/zh/latest/Measure.html

        qprog_with_measure (input,param)

            `input`: array_like input 1-dim classic data

            `param`: array_like input 1-dim quantum circuit\'s parameters

    Example::

        import pyqpanda as pq
        from pyvqnet.qnn import ProbsMeasure
        import numpy as np
        from pyvqnet.tensor import QTensor
        import pyvqnet
        pyvqnet.backends.set_backend("torch")
        from pyvqnet.qnn.vqc.torch import TorchQpandaQuantumLayer
        def pqctest (input,param):
            num_of_qubits = 4

            m_machine = pq.CPUQVM()# outside
            m_machine.init_qvm()# outside
            qubits = m_machine.qAlloc_many(num_of_qubits)

            circuit = pq.QCircuit()
            circuit.insert(pq.H(qubits[0]))
            circuit.insert(pq.H(qubits[1]))
            circuit.insert(pq.H(qubits[2]))
            circuit.insert(pq.H(qubits[3]))

            circuit.insert(pq.RZ(qubits[0],input[0]))
            circuit.insert(pq.RZ(qubits[1],input[1]))
            circuit.insert(pq.RZ(qubits[2],input[2]))
            circuit.insert(pq.RZ(qubits[3],input[3]))

            circuit.insert(pq.CNOT(qubits[0],qubits[1]))
            circuit.insert(pq.RZ(qubits[1],param[0]))
            circuit.insert(pq.CNOT(qubits[0],qubits[1]))

            circuit.insert(pq.CNOT(qubits[1],qubits[2]))
            circuit.insert(pq.RZ(qubits[2],param[1]))
            circuit.insert(pq.CNOT(qubits[1],qubits[2]))

            circuit.insert(pq.CNOT(qubits[2],qubits[3]))
            circuit.insert(pq.RZ(qubits[3],param[2]))
            circuit.insert(pq.CNOT(qubits[2],qubits[3]))
            #print(circuit)

            prog = pq.QProg()
            prog.insert(circuit)

            rlt_prob = ProbsMeasure([0,2],prog,m_machine,qubits)
            return rlt_prob

        pqc = TorchQpandaQuantumLayer(pqctest,3)

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

class TorchQpandaFunctionHelper(torch.autograd.Function):
    @staticmethod
    def preprocess(ctx, x, weights, qlayer): ...
    @staticmethod
    def post_process(ctx, x, weights, batch_exp, qlayer): ...
    @staticmethod
    def forward(ctx, x, weights, qlayer): ...
    @staticmethod
    def backward(ctx, grad_output): ...
