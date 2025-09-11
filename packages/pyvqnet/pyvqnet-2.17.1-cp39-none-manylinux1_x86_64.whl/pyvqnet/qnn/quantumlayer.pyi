from pyvqnet.utils.initializer import *
from _typeshed import Incomplete
from pyvqnet.nn import Module
from typing import Callable

__all__ = ['QuantumLayerBase', 'NoiseQuantumLayer', 'QuantumLayer', 'QuantumLayerV2', 'QuantumLayerMultiProcess', 'QuantumBatchAsyncQcloudLayer', 'QuantumBatchAsyncQcloudLayerES', 'QpandaQProgVQCLayer', 'QpandaQCircuitVQCLayer', 'QpandaQCircuitVQCLayerLite', '_init_factory_kwargs_and_backend', '_get_bsz_num_x_qlayer_bp', '_validate_vqnet_grad', '_postprocess_multi_type_outputs', '_update_jac_use_default_ps', '_get_default_ps_irs', '_init_param', '_update_data_for_default_ps', '_create_x_cat_w_matrix_for_ps_grad', '_validate_vqnet_input', '_check_num_of_qlayer_p', '_check_num_of_qlayer_g', '_check_bsz_of_qlayer_input']

class QuantumLayerBase(Module):
    history_expectation: Incomplete
    history_g: Incomplete
    grad_have_calc_ed: int
    w_grad_have_calc: int
    x_grad_have_calc: int
    backend: int
    calc_split_circuits_exp_asyn_batched: Incomplete
    calc_exp_asyn_batched: Incomplete
    calc_qmeasure_asyn_batched: Incomplete
    def __init__(self, name: str = '') -> None: ...
    def reset_jac_exp(self) -> None: ...
    def reset_grad_calc_status(self) -> None: ...
    def _check_bsz_of_qlayer_input(self, x): ...
    def _check_num_of_qlayer_g(self, g): ...
    def _validate_vqnet_input(self, x): ...
    def _validate_vqnet_grad(self, g): ...
    def _check_num_of_qlayer_p(self, p): ...
    def _create_x_cat_w_matrix_for_ps_grad(self, x, param, batchsize): ...
    def _init_factory_kwargs_and_backend(self, device, dtype): ...
    def _get_bsz_num_x_qlayer_bp(self, xdata): ...
    def _check_num_of_qlayer_g(self, g): ...
    def check_diff_method(self, diff_method) -> None: ...
    def _init_param(self, para_num, initializer, factory_kwargs): ...

class NoiseQuantumLayer(QuantumLayerBase):
    '''
    Abstract Calculation module for Variational Quantum Layer. It simulate a parameterized quantum
    circuit and get the measurement result. It inherits from Module,so that it can calculate
    gradients of circuits parameters,and trains Variational Quantum Circuits model or embeds
    Variational Quantum Circuits into hybird Quantum and Classic model.

    :param qprog_with_measure: callable quantum circuits functions ,cosntructed by qpanda
    :param para_num: `int` - Number of para_num
    :param machine_type: qpanda machine type
    :param num_of_qubits: num of qubits
    :param num_of_cbits: num of cubits
    :param diff_method: \'parameter_shift\' or \'finite_diff\'
    :param delta:  delta for diff
    :param noise_set_config: noise set function

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a module can calculate quantum circuits with noise model.

    Note:
        qprog_with_measure is quantum circuits function defined in pyQPanda :
        https://pyqpanda-toturial.readthedocs.io/zh/latest/QCircuit.html.

        This function should contains following parameters,otherwise it can not run properly
         in NoiseQuantumLayer.

        qprog_with_measure (input,param,qubits,cubits,m_machine)

            `input`: array_like input 1-dim classic data

            `param`: array_like input 1-dim quantum circuit\'s parameters

            `qubits`: qubits allocated by NoiseQuantumLayer

            `cubits`: cubits allocated by NoiseQuantumLayer.if your circuits does not use
             cubits,you should also reserve this parameter.

            `m_machine`: simulator created by NoiseQuantumLayer

    Example::

        def circuit(weights,param,qubits,cbits,machine):

            circuit = pq.QCircuit()

            circuit.insert(pq.H(qubits[0]))
            circuit.insert(pq.RY(qubits[0], weights[0]))
            circuit.insert(pq.RY(qubits[0], param[0]))
            prog = pq.QProg()
            prog.insert(circuit)
            prog << measure_all(qubits, cbits)

            result = machine.run_with_configuration(prog, cbits, 100)

            counts = np.array(list(result.values()))
            states = np.array(list(result.keys())).astype(float)
            # Compute probabilities for each state
            probabilities = counts / 100
            # Get state expectation
            expectation = np.sum(states * probabilities)
            return expectation


        def default_noise_config(qvm,q):

            p = 0.01
            qvm.set_noise_model(NoiseModel.BITFLIP_KRAUS_OPERATOR, GateType.PAULI_X_GATE, p)
            qvm.set_noise_model(NoiseModel.BITFLIP_KRAUS_OPERATOR, GateType.PAULI_Y_GATE, p)
            qvm.set_noise_model(NoiseModel.BITFLIP_KRAUS_OPERATOR, GateType.PAULI_Z_GATE, p)
            qvm.set_noise_model(NoiseModel.BITFLIP_KRAUS_OPERATOR, GateType.RX_GATE, p)
            qvm.set_noise_model(NoiseModel.BITFLIP_KRAUS_OPERATOR, GateType.RY_GATE, p)
            qvm.set_noise_model(NoiseModel.BITFLIP_KRAUS_OPERATOR, GateType.RZ_GATE, p)
            qvm.set_noise_model(NoiseModel.BITFLIP_KRAUS_OPERATOR, GateType.RY_GATE, p)
            qvm.set_noise_model(NoiseModel.BITFLIP_KRAUS_OPERATOR, GateType.HADAMARD_GATE, p)
            qves =[]
            for i in range(len(q)-1):
                qves.append([q[i],q[i+1]])#
            qves.append([q[len(q)-1],q[0]])
            qvm.set_noise_model(NoiseModel.DAMPING_KRAUS_OPERATOR, GateType.CNOT_GATE, p, qves)

            return qvm

        qvc = NoiseQuantumLayer(circuit,24,"noise",1,1,diff_method= "parameter_shift", delta=0.01,
                                noise_set_config = default_noise_config)
        input = QTensor([
            [0.0000000000, 1.0000000000, 1.0000000000, 1.0000000000],

            [0.0000000000, 0.0000000000, 1.0000000000, 1.0000000000],

            [1.0000000000, 0.0000000000, 1.0000000000, 1.0000000000]
            ] )
        rlt = qvc(input)
        print(rlt)
        grad =  QTensor(np.ones(rlt.data.shape)*1000)

        rlt.backward(grad)
        print(qvc.m_para.grad)

    '''
    m_prog_func: Incomplete
    m_machine: Incomplete
    m_qubits: Incomplete
    m_cubits: Incomplete
    delta: Incomplete
    def __init__(self, qprog_with_measure, para_num, machine_type, num_of_qubits: int, num_of_cbits: int = 1, diff_method: str = 'parameter_shift', delta: float = 0.01, noise_set_config=None, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...

class QuantumBatchAsyncQcloudLayer(QuantumLayerBase):
    '''

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

        import numpy as np
        import pyqpanda as pq
        import pyvqnet
        from pyvqnet.qnn import QuantumLayer,QuantumBatchAsyncQcloudLayer
        from pyvqnet.qnn import expval_qcloud

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

        l = QuantumBatchAsyncQcloudLayer(qfun,
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
                        submit_kwargs={},
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
    l = QuantumBatchAsyncQcloudLayer(qfun2,
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
                submit_kwargs={},
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
    query_by_taskid_sync_batched: Incomplete
    submit_task_asyn_batched: Incomplete
    calc_split_circuits_exp_asyn_batched: Incomplete
    calc_exp_asyn_batched: Incomplete
    calc_qmeasure_asyn_batched: Incomplete
    def set_dummy(self, is_dummy) -> None: ...
    def forward(self, x, *args, **kwargs): ...
    def _postprocess_multi_type_outputs(self, qcir_offset, output, coffs): ...

class QuantumBatchAsyncQcloudLayerES(QuantumLayerBase):
    '''

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
    :param submit_kwargs: Additional keyword arguments for submitting quantum circuits,
    default:{"chip_id":pyqpanda.real_chip_type.origin_72,"is_amend":True,"is_mapping":True,
    "is_optimization": True,"default_task_group_size":200,"test_qcloud_fake":True}.
    :param query_kwargs: Additional keyword arguments for querying quantum results, default:{"timeout":1,"print_query_info":True,"sub_circuits_split_size":1}.
    :param sigma: Sampling variance of a multivariate nontrivial distribution.
    :return: A module that can calculate quantum circuits.

    Example::

        import numpy as np
        import pyqpanda as pq
        import pyvqnet
        from pyvqnet.qnn import QuantumLayer,QuantumBatchAsyncQcloudLayerES
        from pyvqnet.qnn import expval_qcloud

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

        l = QuantumBatchAsyncQcloudLayerES(qfun,
                        "3047DE8A59764BEDAC9C3282093B16AF1",
                        2,
                        6,
                        6,
                        pauli_str_dict=None,
                        shots = 1000,
                        initializer=None,
                        dtype=None,
                        name="",
                        submit_kwargs={},
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
    l = QuantumBatchAsyncQcloudLayerES(qfun2,
                "3047DE8A59764BEDAC9C3282093B16AF",
                2,
                6,
                6,
                pauli_str_dict={\'Z0 X1\':10,\'\':-0.5,\'Y2\':-0.543},
                shots = 1000,
                initializer=None,
                dtype=None,
                name="",
                submit_kwargs={},
                query_kwargs={})
    x = pyvqnet.tensor.QTensor([[0.56,1.2],[0.56,1.2],[0.56,1.2],[0.56,1.2]],requires_grad= True)
    y = l(x)
    print(y)
    y.backward()
    print(l.m_para.grad)
    print(x.grad)


    '''
    m_prog_func: Incomplete
    pauli_str_dict: Incomplete
    pq_utils: Incomplete
    submit_kwargs: Incomplete
    query_kwargs: Incomplete
    sigma: Incomplete
    shots: Incomplete
    m_machine: Incomplete
    qlists: Incomplete
    clists: Incomplete
    def __init__(self, origin_qprog_func: Callable, qcloud_token: str, para_num: int, num_qubits: int, num_cubits: int, pauli_str_dict: list[dict] | dict | None = None, shots: int = 1000, initializer: Callable = None, dtype: int | None = None, name: str = '', submit_kwargs: dict = {}, query_kwargs: dict = {}, sigma=...) -> None: ...
    query_by_taskid_sync_batched: Incomplete
    submit_task_asyn_batched: Incomplete
    calc_exp_asyn_batched: Incomplete
    calc_qmeasure_asyn_batched: Incomplete
    calc_split_circuits_exp_asyn_batched: Incomplete
    def set_dummy(self, is_dummy) -> None: ...
    def forward(self, x, *args, **kwargs): ...
    def _postprocess_multi_type_outputs(self, qcir_offset, output, coffs): ...

class QuantumLayer(QuantumLayerBase):
    '''
    Abstract Calculation module for Variational Quantum Layer. It simulate a parameterized quantum
    circuit and get the measurement result. It inherits from Module,so that it can calculate
    gradients of circuits parameters,and trains Variational Quantum Circuits model or embeds
    Variational Quantum Circuits into hybird Quantum and Classic model.


    :param qprog_with_measure: callable quantum circuits functions ,cosntructed by qpanda
    :param para_num: `int` - Number of parameter
    :param machine_type_or_cloud_token: qpanda machine type or pyQPANDA QCLOUD token :
     https://pyqpanda-toturial.readthedocs.io/zh/latest/Realchip.html
    :param num_of_qubits: num of qubits
    :param num_of_cbits: num of classic bits
    :param diff_method: \'parameter_shift\' or \'finite_diff\'
    :param delta:  delta for diff

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a module can calculate quantum circuits .

    Note:
        qprog_with_measure is quantum circuits function defined in pyQPanda :
        https://pyqpanda-toturial.readthedocs.io/zh/latest/QCircuit.html.

        This function should contains following parameters,otherwise it can not run properly
         in QuantumLayer.

        qprog_with_measure (input,param,qubits,cubits,m_machine)

            `input`: array_like input 1-dim classic data

            `param`: array_like input 1-dim quantum circuit\'s parameters

            `qubits`: qubits allocated by QuantumLayer

            `cubits`: cubits allocated by QuantumLayer.if your circuits does not use cubits,
             you should also reserve this parameter.

            `m_machine`: simulator created by QuantumLayer

    Example::

        def pqctest (input,param,qubits,cubits,m_machine):
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


        pqc = QuantumLayer(pqctest,3,"cpu",4,1)

        #classic data as input
        input = QTensor([[1,2,3,4],[4,2,2,3],[3,3,2,2]] )

        #forward circuits
        rlt = pqc(input)

        print(rlt)

        grad =  QTensor(np.ones(rlt.data.shape)*1000)
        #backward circuits
        rlt.backward(grad)

        print(pqc.m_para.grad)

    '''
    m_prog_func: Incomplete
    m_machine: Incomplete
    m_qubits: Incomplete
    m_cubits: Incomplete
    delta: Incomplete
    def __init__(self, qprog_with_measure: Callable, para_num: int, machine_type_or_cloud_token: str, num_of_qubits: int, num_of_cbits: int = 1, diff_method: str = 'parameter_shift', delta: float = 0.01, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...
    def __del__(self) -> None: ...
QpandaQCircuitVQCLayer = QuantumLayer

class QuantumLayerWithQProg(QuantumLayerBase):
    '''
    Abstract Calculation module for Variational Quantum Layer. It simulate a parameterized quantum
    circuit and get the measurement result. It inherits from Module,so that it can calculate
    gradients of circuits parameters,and trains Variational Quantum Circuits model or embeds
    Variational Quantum Circuits into hybird Quantum and Classic model.

    This Module need additional return QProg for future use.

    :param qprog_with_measure: callable quantum circuits functions ,cosntructed by qpanda
    :param para_num: `int` - Number of parameter
    :param machine_type_or_cloud_token: qpanda machine type or pyQPANDA QCLOUD token :
     https://pyqpanda-toturial.readthedocs.io/zh/latest/Realchip.html
    :param num_of_qubits: num of qubits
    :param num_of_cbits: num of classic bits
    :param diff_method: \'parameter_shift\' or \'finite_diff\'
    :param delta:  delta for diff

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a module can calculate quantum circuits .

    Note:
        qprog_with_measure is quantum circuits function defined in pyQPanda :
        https://pyqpanda-toturial.readthedocs.io/zh/latest/QCircuit.html.

        This function should contains following parameters, and return QProg, otherwise it can not run properly
         in QuantumLayerWithQProg.

        qprog_with_measure (input,param,qubits,cubits,m_machine)

            `input`: array_like input 1-dim classic data

            `param`: array_like input 1-dim quantum circuit\'s parameters

            `qubits`: qubits allocated by QuantumLayerWithQProg

            `cubits`: cubits allocated by QuantumLayerWithQProg.if your circuits does not use cubits,
             you should also reserve this parameter.

            `m_machine`: simulator created by QuantumLayerWithQProg
        
        return :
            y, Qprog

    Example::

        from pyvqnet.tensor import QTensor
        import pyqpanda as pq
        import numpy as np
        from pyvqnet.qnn import ProbsMeasure,QuantumLayerWithQProg

        def pqctest (input,param,qubits,cubits,m_machine):
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
            return rlt_prob,prog


        pqc = QuantumLayerWithQProg(pqctest,3,"cpu",4,1)

        #classic data as input
        input = QTensor([[1,2,3,4],[4,2,2,3],[3,3,2,2]] )
        input.requires_grad = True
        #forward circuits
        rlt = pqc(input)

        print(rlt)

        grad =  QTensor(np.ones(rlt.data.shape)*1000)
        #backward circuits
        rlt.backward(grad)

        print(pqc.m_para.grad)
        print(input.grad)

    '''
    m_prog_func: Incomplete
    m_machine: Incomplete
    m_qubits: Incomplete
    m_cubits: Incomplete
    delta: Incomplete
    def __init__(self, qprog_with_measure, para_num, machine_type_or_cloud_token, num_of_qubits: int, num_of_cbits: int = 1, diff_method: str = 'parameter_shift', delta: float = 0.01, dtype: int | None = None, name: str = '') -> None: ...
    def forward_dummy(self, x): ...
    def forward(self, x): ...
    def __del__(self) -> None: ...

class QuantumLayerV2(QuantumLayerBase):
    '''
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
         properly in QuantumLayerV2.

        Compare to QuantumLayer.you should allocate qubits and simulator:
         https://pyqpanda-toturial.readthedocs.io/zh/latest/QuantumMachine.html,

        you may also need to allocate cubits if qprog_with_measure needs quantum
         measure:https://pyqpanda-toturial.readthedocs.io/zh/latest/Measure.html

        qprog_with_measure (input,param)

            `input`: array_like input 1-dim classic data

            `param`: array_like input 1-dim quantum circuit\'s parameters


    Example::

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

        pqc = QuantumLayerV2(pqctest,3)

        #classic data as input
        input = QTensor([[1,2,3,4],[4,2,2,3],[3,3,2,2]] )

        #forward circuits
        rlt = pqc(input)

        print(rlt)

        grad =  QTensor(np.ones(rlt.data.shape)*1000)
        #backward circuits
        rlt.backward(grad)

        print(pqc.m_para.grad)

    '''
    m_prog_func: Incomplete
    delta: Incomplete
    def __init__(self, qprog_with_measure: Callable, para_num: int, diff_method: str = 'parameter_shift', delta: float = 0.01, dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x): ...
QpandaQCircuitVQCLayerLite = QuantumLayerV2

class QuantumLayerV3(QuantumLayerBase):
    '''

    It submit parameterized quantum circuits to CPUQVM and train the paramters in circuit.
    It needs input parameterized quantum circuits function returns with qprog.
    It supports batch data and use paramters-shift rules to estimate paramters\' gradients.
    For CRX,CRY,CRZ, this layer use formulas in https://iopscience.iop.org/article/10.1088/1367-2630/ac2cb3

    :param origin_qprog_func: callable quantum circuits function constructed by QPanda.
    :param para_num: `int` - Number of parameters; parameters are one-dimensional.
    :param num_qubits: `int` - Number of qubits in the quantum circuit.
    :param num_cubits: `int` - Number of classical bits for measurement in the quantum circuit.
    :param pauli_str_dict: `dict|list` - Dictionary or list of dictionary representing the Pauli operators in the quantum circuit. Default is None.
    :param shots: `int` - Number of measurement shots. Default is 1000.
    :param initializer: Initializer for parameter values. Default is None.
    :param dtype: Data type of parameters. Default is None, which uses the default data type.
    :param name: Name of the module. Default is an empty string.

    Note:
        origin_qprog_func is user defines quantum circuits function using pyQPanda :
        https://pyqpanda-toturial.readthedocs.io/zh/latest/QCircuit.html.

        This function should contains following input arguments, and return pyQPanda.QProg or originIR.

        origin_qprog_func (input,param,m_machine,qubits,cubits)

            `input`: array_like input 1-dim classic data defined by users.

            `param`: array_like input 1-dim quantum circuit\'s parameters defined by users.

            `m_machine`: simulator created by QuantumLayerV3.

            `qubits`: qubits allocated by QuantumLayerV3

            `cubits`: cubits allocated by QuantumLayerV3.if your circuits does not use cubits,
             you should also reserve this parameter.

    Example::

        import numpy as np
        import pyqpanda as pq
        import pyvqnet
        from pyvqnet.qnn import  QuantumLayerV3


        def qfun(input, param, m_machine, m_qlist, cubits):
            measure_qubits = [0,1, 2]
            m_prog = pq.QProg()
            cir = pq.QCircuit()

            cir.insert(pq.RZ(m_qlist[0], input[0]))
            cir.insert(pq.RX(m_qlist[2], input[2]))
            
            qcir = pq.RX(m_qlist[1], param[1])
            qcir.set_control(m_qlist[0])
            cir.insert(qcir)

            qcir = pq.RY(m_qlist[0], param[2])
            qcir.set_control(m_qlist[1])
            cir.insert(qcir)

            cir.insert(pq.RY(m_qlist[0], input[1]))

            qcir = pq.RZ(m_qlist[0], param[3])
            qcir.set_control(m_qlist[1])
            cir.insert(qcir)
            m_prog.insert(cir)

            for idx, ele in enumerate(measure_qubits):
                m_prog << pq.Measure(m_qlist[ele], cubits[idx])  # pylint: disable=expression-not-assigned
            return m_prog
        from pyvqnet.utils.initializer import ones
        l = QuantumLayerV3(qfun,
                        4,
                        3,
                        3,
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
    def __init__(self, origin_qprog_func: Callable, para_num: int, num_qubits: int, num_cubits: int, pauli_str_dict: list[dict] | dict | None = None, shots: int = 1000, initializer: Callable = None, dtype: int | None = None, name: str = '') -> None: ...
    query_by_taskid_sync_batched: Incomplete
    submit_task_asyn_batched: Incomplete
    calc_exp_asyn_batched: Incomplete
    calc_qmeasure_asyn_batched: Incomplete
    calc_split_circuits_exp_asyn_batched: Incomplete
    def set_dummy(self, is_dummy) -> None: ...
    def forward(self, x, *args, **kwargs): ...
    def _get_default_ps_irs(self, prog_func, x_amp_w_preload_all, stride, batchsize, p, num_x, machine, qlists, clists): ...
    def _postprocess_multi_type_outputs(self, qcir_offset, output, coffs): ...
QpandaQProgVQCLayer = QuantumLayerV3

class QuantumLayerMultiProcess(QuantumLayerBase):
    '''
    Abstract Calculation module for Variational Quantum Layer. It simulate a parameterized quantum
    circuit and get the measurement result. It inherits from Module,so that it can calculate
    gradients of circuits parameters,and trains Variational Quantum Circuits model or embeds
    Variational Quantum Circuits into hybird Quantum and Classic model.

    Unlike other quantum layer computing modules, this computing module uses multi-processing technology
    to speed up processing. You need to allocated simulation machine and qubits by yourself.

    :param qprog_with_measure: callable quantum circuits functions ,cosntructed by qpanda
    :param para_num: `int` - Number of parameter
    :param num_of_qubits: num of qubits
    :param num_of_cbits: num of classic bits
    :param diff_method: \'parameter_shift\' or \'finite_diff\'
    :param delta:  delta for diff.

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a module can calculate quantum circuits .

    Note:
        qprog_with_measure is quantum circuits function defined in pyQPanda :
        https://pyqpanda-toturial.readthedocs.io/zh/latest/QCircuit.html.

        This function should contains following parameters,otherwise it can not run properly
         in QuantumLayer.

        qprog_with_measure (input,param,nqubits,ncubits)

            `input`: array_like input 1-dim classic data

            `param`: array_like input 1-dim quantum circuit\'s parameters

            `nqubits`: number of qubits.

            `ncubits`: number cubits allocated by QuantumLayer.


    Example::

        def pqctest (input,param,nqubits,ncubits):
            machine = pq.CPUQVM()
            machine.init_qvm()
            qubits = machine.qAlloc_many(nqubits)
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
            print(prog)
            # pauli_dict  = {\'Z0 X1\':10,\'Y2\':-0.543}
            # exp2 = expval(machine,prog,pauli_dict,qubits)
            rlt_prob = ProbsMeasure([0,2],prog,machine,qubits)
            return rlt_prob


        pqc = QuantumLayerMultiProcess(pqctest,3,4,1)

        #classic data as input
        input = QTensor([[1,2,3,4],[4,2,2,3],[3,3,2,2]] )

        #forward circuits
        rlt = pqc(input)

        print(rlt)

        grad =  QTensor(np.ones(rlt.data.shape)*1000)
        #backward circuits
        rlt.backward(grad)

        print(pqc.m_para.grad)
    '''
    m_prog_func: Incomplete
    m_qubits: Incomplete
    m_cubits: Incomplete
    delta: Incomplete
    def __init__(self, qprog_with_measure: Callable, para_num: int, num_of_qubits: int, num_of_cbits: int = 1, diff_method: str = 'parameter_shift', delta: float = 0.01, dtype: int | None = None, name: str = '') -> None: ...
    history_expectation: Incomplete
    def forward(self, x): ...

def _validate_vqnet_grad(g): ...
def _validate_vqnet_input(input_data): ...
def _check_bsz_of_qlayer_input(x): ...
def _check_num_of_qlayer_g(g): ...
def _check_num_of_qlayer_p(param): ...
def _get_bsz_num_x_qlayer_bp(xdata): ...
def _init_param(para_num, initializer, factory_kwargs): ...
def _init_factory_kwargs_and_backend(device, dtype): ...
def _update_data_for_default_ps(x_amp_w_preload_all, stride, batchsize) -> None: ...
def _get_default_ps_irs(prog_func, x_amp_w_preload_all, stride, batchsize, p, num_x, machine, qlists, clists): ...
def _update_jac_use_default_ps(idx, batchsize, outputs, x_, num_x, stride, _x_jacobian, _jacobian) -> None: ...
def _create_x_cat_w_matrix_for_ps_grad(x_, param, batchsize): ...
def _postprocess_multi_type_outputs(self, qcir_offset, output, coffs, measure_number: int = -100):
    """
    pa2 version to insert measure obs
    """
