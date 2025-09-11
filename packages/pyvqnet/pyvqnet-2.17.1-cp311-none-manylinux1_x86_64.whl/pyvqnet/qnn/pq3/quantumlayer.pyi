from pyvqnet.nn.module import *
from pyvqnet.utils.initializer import *
from ..quantumlayer import QuantumLayerBase as NQuantumLayerBase, QuantumLayerV2 as pq2_QuantumLayerV2, _check_bsz_of_qlayer_input as _check_bsz_of_qlayer_input, _check_num_of_qlayer_g as _check_num_of_qlayer_g, _check_num_of_qlayer_p as _check_num_of_qlayer_p, _create_x_cat_w_matrix_for_ps_grad as _create_x_cat_w_matrix_for_ps_grad, _get_bsz_num_x_qlayer_bp as _get_bsz_num_x_qlayer_bp, _init_factory_kwargs_and_backend as _init_factory_kwargs_and_backend, _init_param as _init_param, _postprocess_multi_type_outputs as _postprocess_multi_type_outputs, _update_data_for_default_ps as _update_data_for_default_ps, _update_jac_use_default_ps as _update_jac_use_default_ps, _validate_vqnet_grad as _validate_vqnet_grad, _validate_vqnet_input as _validate_vqnet_input
from _typeshed import Incomplete
from typing import Callable

__all__ = ['QuantumLayerBase', 'NoiseQuantumLayer', 'QuantumLayer', 'QuantumLayerV2', 'QuantumBatchAsyncQcloudLayer', 'QuantumBatchAsyncQcloudLayerES', 'QpandaQProgVQCLayer', 'QpandaQCircuitVQCLayer', 'QpandaQCircuitVQCLayerLite', '_init_factory_kwargs_and_backend', '_get_bsz_num_x_qlayer_bp', '_validate_vqnet_grad', '_postprocess_multi_type_outputs', '_update_jac_use_default_ps', '_get_default_ps_irs', '_init_param', '_update_data_for_default_ps', '_create_x_cat_w_matrix_for_ps_grad', '_validate_vqnet_input', '_check_num_of_qlayer_p', '_check_num_of_qlayer_g', '_check_bsz_of_qlayer_input']

class QuantumLayerBase(NQuantumLayerBase): ...

class QuantumBatchAsyncQcloudLayer(QuantumLayerBase):
    '''

    Abstract Calculation module for originqc real chip using pyqpanda3 qcloud. It submit parameterized quantum
    circuits to real chip and get the measurement result.

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
        from pyvqnet.qnn.pq3.quantumlayer import QuantumBatchAsyncQcloudLayer

        
        def qfun2(input,param ):
            
            m_qlist = range(6)
            cir = pq.QCircuit(6)
            cir<<pq.RZ(m_qlist[0],input[0])
            cir<<pq.CNOT(m_qlist[0],m_qlist[1])
            cir<<pq.RY(m_qlist[1],param[0])
            cir<<pq.CNOT(m_qlist[0],m_qlist[2])
            cir<<pq.RZ(m_qlist[1],input[1])
            cir<<pq.RY(m_qlist[2],param[1])
            cir<<pq.H(m_qlist[2])
            m_prog = pq.QProg(cir)


 
            return m_prog
        l = QuantumBatchAsyncQcloudLayer(qfun2,
                "3041020100301306072a8648ce3d020106082a8648ce3d030107042730250201010420301250061f4eda8200b9ad46d10cc5ff305d7814b966e6333fe8987e0c248a2a/12570",
                2,
                pauli_str_dict={\'Z0 X1\':10,\'Y2\':-0.543,"":3333},
                shots = 10,
                initializer=None,
                dtype=None,
                name="",
                diff_method="parameter_shift",
                submit_kwargs={"test_qcloud_fake":True},
                query_kwargs={})
        x = pyvqnet.tensor.QTensor([[0.56,1.2],[0.56,1.2]],requires_grad= True)
        y = l(x)
        print(y)


    '''
    eqc_w_index: int
    def __init__(self, origin_qprog_func: Callable, qcloud_token: str, para_num: int, pauli_str_dict: list[dict] | dict | None = None, shots: int = 1000, initializer: Callable = None, dtype: int | None = None, name: str = '', diff_method: str = 'parameter_shift', submit_kwargs: dict = {}, query_kwargs: dict = {}) -> None: ...
    query_by_taskid_sync_batched: Incomplete
    submit_task_asyn_batched: Incomplete
    calc_split_circuits_exp_asyn_batched: Incomplete
    calc_exp_asyn_batched: Incomplete
    calc_qmeasure_asyn_batched: Incomplete
    def set_dummy(self, is_dummy) -> None: ...
    def forward(self, x, *args, **kwargs): ...
    def _postprocess_multi_type_outputs(self, qcir_offset, output, coffs): ...

class QuantumLayerV2(pq2_QuantumLayerV2):
    def __init__(self, qprog_with_measure: Callable, para_num: int, diff_method: str = 'parameter_shift', delta: float = 0.01, dtype: int | None = None, name: str = '') -> None: ...
QpandaQCircuitVQCLayerLite = QuantumLayerV2
QuantumLayer = QuantumLayerV2

class QuantumLayerV3(QuantumLayerBase):
    '''

    It submit parameterized quantum circuits to pyqpanda3.core.CPUQVM or GPUQVM and train the paramters in circuit.
    It needs input parameterized quantum circuits function returns with qprog.
    It supports batch data and use paramters-shift rules to estimate paramters\' gradients.
    For CRX,CRY,CRZ, this layer use formulas in https://iopscience.iop.org/article/10.1088/1367-2630/ac2cb3

    :param origin_qprog_func: callable quantum circuits function constructed by pyqpanda3.
    :param para_num: `int` - Number of parameters; parameters are one-dimensional.
    :param qvm_type: `str` - type of qvm to use ,`cpu` or `gpu`, default:`cpu`.
    :param pauli_str_dict: `dict|list` - Dictionary or list of dictionary representing the Pauli operators in the quantum circuit. Default is None.
    :param shots: `int` - Number of measurement shots. Default is 1000.
    :param initializer: Initializer for parameter values. Default is None.
    :param dtype: Data type of parameters. Default is None, which uses the default data type.
    :param name: Name of the module. Default is an empty string.

    Note:
        origin_qprog_func is user defines quantum circuits function using pyQPanda3 :
        https://qcloud.originqc.com.cn/document/qpanda-3/dc/d12/tutorial_quantum_program.html.

        This function should contains following input arguments, and return pyQPanda.QProg or originIR.

        origin_qprog_func (input,param,m_machine,qubits,cubits)

            `input`: array_like input 1-dim classic data defined by users.

            `param`: array_like input 1-dim quantum circuit\'s parameters defined by users.

            `m_machine`: simulator created by QuantumLayerV3.

            `qubits`: qubits allocated by QuantumLayerV3

            `cubits`: cubits allocated by QuantumLayerV3.if your circuits does not use cubits,
             you should also reserve this parameter.

    Example::

        import pyqpanda3.core as pq
        import pyvqnet
        from pyvqnet.qnn.pq3.quantumlayer import  QuantumLayerV3


        def qfun(input, param ):
            m_qlist = range(3)
            cubits = range(3)
            measure_qubits = [0,1, 2]
            m_prog = pq.QProg()
            cir = pq.QCircuit(3)

            cir<<pq.RZ(m_qlist[0], input[0])
            cir<<pq.RX(m_qlist[2], input[2])
            
            qcir = pq.RX(m_qlist[1], param[1]).control(m_qlist[0])
        
            cir<<qcir

            qcir = pq.RY(m_qlist[0], param[2]).control(m_qlist[1])
        
            cir<<qcir

            cir<<pq.RY(m_qlist[0], input[1])

            qcir = pq.RZ(m_qlist[0], param[3]).control(m_qlist[1])
        
            cir<<qcir
            m_prog<<cir

            for idx, ele in enumerate(measure_qubits):
                m_prog << pq.measure(m_qlist[ele], cubits[idx])  # pylint: disable=expression-not-assigned
            return m_prog

        from pyvqnet.utils.initializer import ones
        l = QuantumLayerV3(qfun,
                        4,
                        "cpu",
                        pauli_str_dict=None,
                        shots=1000,
                        initializer=ones,
                        name="")
        x = pyvqnet.tensor.QTensor(
            [[2.56, 1.2,-3]],
            requires_grad=True)
        y = l(x)

        y.backward()
        print(l.m_para.grad.to_numpy())
        print(x.grad.to_numpy())

    '''
    bind_dict: Incomplete
    m_machine: Incomplete
    qlists: Incomplete
    clists: Incomplete
    def __init__(self, origin_qprog_func: Callable, para_num: int, qvm_type: str = 'cpu', pauli_str_dict: list[dict] | dict | None = None, shots: int = 1000, initializer: Callable = None, dtype: int | None = None, name: str = '') -> None: ...
    query_by_taskid_sync_batched: Incomplete
    submit_task_asyn_batched: Incomplete
    calc_split_circuits_exp_asyn_batched: Incomplete
    calc_exp_asyn_batched: Incomplete
    calc_qmeasure_asyn_batched: Incomplete
    def set_dummy(self, is_dummy) -> None: ...
    def forward(self, x, *args, **kwargs): ...
    def _get_default_ps_irs(self, prog_func, x_amp_w_preload_all, stride, batchsize, p, num_x, machine, qlists, clists): ...
    def _postprocess_multi_type_outputs(self, qcir_offset, output, coffs): ...
QpandaQProgVQCLayer = QuantumLayerV3

class QuantumLayerAdjoint(pq2_QuantumLayerV2):
    """

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
 
    Examples::

        from pyvqnet.qnn.pq3 import QuantumLayerAdjoint
        from pyvqnet import tensor

        from pyqpanda3.vqcircuit import VQCircuit
        import pyqpanda3 as pq3

        l = 3
        n = 7
        def pqctest(x,param):
            vqc = VQCircuit()
            vqc.set_Param([len(param) +len(x)])
            w_offset = len(x)
            for j in range(len(x)):
                vqc << pq3.core.RX(j, vqc.Param([j  ]))
            for j in range(l):
                for i in range(n - 1):
                    vqc << pq3.core.CNOT(i, i + 1)
                for i in range(n):
                    vqc << pq3.core.RX(i, vqc.Param([w_offset + 3 * n * j + i]))
                        
                    vqc << pq3.core.RZ(i, vqc.Param([w_offset + 3 * n * j + i + n]))
                    vqc << pq3.core.RY(i, vqc.Param([w_offset + 3 * n * j + i + 2 * n]))
            
            return vqc

        Xn_string = ' '.join([f'X{i}' for i in range(n)])
        pauli_dict  = {Xn_string:1.}

        layer = QuantumLayerAdjoint(pqctest,3*l*n,pauli_dict)

        x = tensor.randn([2,5])
        x.requires_grad = True
        y = layer(x)
        y.backward()
        print(layer.m_para.grad)
        print(x.grad)

        Xn_string = ' '.join([f'X{i}' for i in range(n)])
        Zn_string = ' '.join([f'Z{i}' for i in range(n)])
        pauli_dict  = {Xn_string:1.,Zn_string:0.5}

        layer = QuantumLayerAdjoint(pqctest,3*l*n,pauli_dict)

        x = tensor.randn([2,5])
        x.requires_grad = True
        y = layer(x)
        y.backward()
        print(layer.m_para.grad)
        print(x.grad)

        Xn_string = ' '.join([f'X{i}' for i in range(n)])
        Zn_string = ' '.join([f'Z{i}' for i in range(n)])
        pauli_dict  = {Xn_string:1.,Zn_string:0.5}

        layer = QuantumLayerAdjoint(pqctest,3*l*n,pauli_dict)

        x = tensor.randn([1,5])
        x.requires_grad = True
        y = layer(x)
        y.backward()
        print(layer.m_para.grad)
        print(x.grad)

        Xn_string = ' '.join([f'X{i}' for i in range(n)])
        Zn_string = ' '.join([f'Z{i}' for i in range(n)])
        pauli_dict  = [{Xn_string:1.,Zn_string:0.5},{Xn_string:1.,Zn_string:0.5}]

        layer = QuantumLayerAdjoint(pqctest,3*l*n,pauli_dict)

        x = tensor.randn([1,5])
        x.requires_grad = True
        y = layer(x)
        y.backward()
        print(layer.m_para.grad)
        print(x.grad)

        Xn_string = ' '.join([f'X{i}' for i in range(n)])
        Zn_string = ' '.join([f'Z{i}' for i in range(n)])
        pauli_dict  = [{Xn_string:1.,Zn_string:0.5},{Xn_string:1.,Zn_string:0.5}]

        layer = QuantumLayerAdjoint(pqctest,3*l*n,pauli_dict)

        x = tensor.randn([2,5])
        x.requires_grad = True
        y = layer(x)
        y.backward()
        print(layer.m_para.grad)
        print(x.grad)


    """
    pauli_dicts: Incomplete
    def __init__(self, pq3_vqc_circuit, param_num, pauli_dicts, dtype=None, name: str = '') -> None: ...
    def forward(self, x, *args, **kwargs): ...

def _get_default_ps_irs(prog_func, x_amp_w_preload_all, stride, batchsize, p, num_x): ...

# Names in __all__ with no definition:
#   NoiseQuantumLayer
#   QpandaQCircuitVQCLayer
#   QuantumBatchAsyncQcloudLayerES
