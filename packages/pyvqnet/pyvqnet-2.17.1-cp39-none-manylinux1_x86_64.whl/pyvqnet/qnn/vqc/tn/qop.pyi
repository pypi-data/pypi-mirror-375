from ....device import DEV_GPU as DEV_GPU
from ....dtype import C_DTYPE as C_DTYPE, kcomplex64 as kcomplex64
from ....nn.torch import TorchModule as TorchModule
from ....tensor import QTensor as QTensor, tensor as tensor
from ....torch import float_to_complex_param as float_to_complex_param
from ..qmachine import AbstractQMachine as AbstractQMachine
from ..qop import DiagonalOperation as NDiagonalOperation, Observable as NObservable, Operation as NOperation, Operator as NOperator, QMachine as NQMachine, QModule as NQModule, StateEncoder as NStateEncoder
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock
from typing import Sequence

class QModule(TorchModule, NQModule):
    def __init__(self, name: str = '') -> None: ...

class TNQModule(QModule):
    '''
    A Module use tensornetwork to execute quantum circuit.
    
    :param use_jit: control quantum circuit jit compilation functionality.
    :param vectorized_argnums: the args to be vectorized,
            these arguments should share the same batch shape in the fist dimension,defaults to 0.
    :param name: name of Module.
    :return: A Module can be used in Torch and VQNet.

    .. warning::

        This Module is based on `tensornetwork` and `pytorch`, you need to install these packages first.
        This Module needs set torch backend. use ``pyvqnet.backends.set_backend("torch") first. ``

        Unlike the :func:`forward` function in :class:`QModule`, since this class uses :func:`torch.vmap`,  
        users need to assume that the input :obj:`x` is a one-dimensional :class:`Tensor` when writing  
        the :func:`forward` function for this class. PyTorch will automatically handle batch  
        inputs of shape ``[bsz, x_dim]``. For example, ``x[:, 2]`` in the :func:`forward` function  
        of :class:`QModule` should be changed to ``x[2]``.  

        The :class:`QMachine` of this class needs to use the :class:`TNQMachine` class to construct  
        the quantum simulator. Since the input :obj:`x` is a 1D :class:`Tensor` in the :func:`torch.vmap` function,  
        the :obj:`bsz` parameter in :meth:`TNQMachine.reset_states(bsz)` at the beginning of each iteration  
        cannot be set using ``x.shape[0]`` but must be provided separately.  
 

    Example::

        import pyvqnet
        from pyvqnet.nn import Parameter
        pyvqnet.backends.set_backend("torch")
        from pyvqnet.qnn.vqc.tn import TNQModule
        from pyvqnet.qnn.vqc.tn import TNQMachine, RX, RY, CNOT, PauliX, PauliZ,qmeasure,qcircuit,VQC_RotCircuit
        class QModel(TNQModule):
            def __init__(self, num_wires, dtype,batch_size=2):
                super(QModel, self).__init__()

                self._num_wires = num_wires
                self._dtype = dtype
                self.qm = TNQMachine(num_wires, dtype=dtype)

                self.w = Parameter((2,4,3),initializer=pyvqnet.utils.initializer.quantum_uniform)
                self.cnot = CNOT(wires=[0, 1])
                self.batch_size = batch_size
            def forward(self, x, *args, **kwargs):
                self.qm.reset_states(batchsize=self.batch_size)

                def get_cnot(nqubits,qm):
                    for i in range(len(nqubits) - 1):
                        CNOT(wires = [nqubits[i], nqubits[i + 1]])(q_machine = qm)
                    CNOT(wires = [nqubits[len(nqubits) - 1], nqubits[0]])(q_machine = qm)


                def build_circult(weights, xx, nqubits,qm):
                    def Rot(weights_j, nqubits,qm):#pylint:disable=invalid-name
                        VQC_RotCircuit(qm,nqubits,weights_j)

                    def basisstate(qm,xx, nqubits):
                        for i in nqubits:
                            qcircuit.rz(q_machine=qm, wires=i, params=xx[i])
                            qcircuit.ry(q_machine=qm, wires=i, params=xx[i])
                            qcircuit.rz(q_machine=qm, wires=i, params=xx[i])

                    basisstate(qm,xx,nqubits)

                    for i in range(weights.shape[0]):

                        weights_i = weights[i, :, :]
                        for j in range(len(nqubits)):
                            weights_j = weights_i[j]
                            Rot(weights_j, nqubits[j],qm)
                        get_cnot(nqubits,qm)

                build_circult(self.w, x,range(4),self.qm)

                y= qmeasure.MeasureAll(obs={\'Z0\': 1})(self.qm)
                return y


        x= pyvqnet.tensor.QTensor([[1,0,0,1],[1,1,0,1]],dtype=pyvqnet.kfloat32)
        model = QModel(4,pyvqnet.kcomplex64,2)
        y = model(x)
        y.backward()

    '''
    vectorized_argnums: Incomplete
    use_jit: Incomplete
    def __init__(self, use_jit: bool = False, vectorized_argnums: int | Sequence[int] = 0, name: str = '') -> None: ...
    def __call__(self, *x): ...

class Encoder(TorchModule):
    def __init__(self) -> None: ...

class StateEncoder(Encoder, NStateEncoder):
    def __init__(self) -> None: ...
    def forward(self, x, q_machine) -> None: ...

class Operator(QModule, NOperator):
    def __init__(self, has_params: bool = False, trainable: bool = False, init_params=None, wires=None, dtype=..., use_dagger: bool = False, **kwargs) -> None: ...

class Operation(Operator, NOperation):
    def __init__(self, has_params: bool = False, trainable: bool = False, init_params=None, wires=None, dtype=..., use_dagger: bool = False, **kwargs) -> None: ...
    def reset_params(self, init_params=None) -> None: ...

class Observable(Operator, NObservable):
    def __init__(self, has_params: bool = False, trainable: bool = False, init_params=None, wires=None, dtype=..., use_dagger: bool = False, **kwargs) -> None: ...

class DiagonalOperation(Operation, NDiagonalOperation):
    def __init__(self, has_params: bool = False, trainable: bool = False, init_params=None, wires=None, dtype=..., use_dagger: bool = False) -> None: ...

class QMachine(TorchModule, NQMachine):
    def __init__(self, num_wires: int, dtype: int = ..., grad_mode: str = '', save_ir: bool = False) -> None: ...
    def add_params_infos(self, params) -> None: ...

class TNQMachine(TorchModule, NQMachine):
    '''
    A tensornetwork based quantum circuit simulation machine.

    :param num_wires: number of qubits to use
    :param dtype: internal data type used to calculate.
    :param use_mps: open MPSCircuit for large bit models.
    
    Example::

        import pyvqnet
        from pyvqnet.nn import Parameter
        pyvqnet.backends.set_backend("torch")
        from pyvqnet.qnn.vqc.tn import TNQModule
        from pyvqnet.qnn.vqc.tn import TNQMachine, RX, RY, CNOT, PauliX, PauliZ,qmeasure,qcircuit,VQC_RotCircuit
        class QModel(TNQModule):
            def __init__(self, num_wires, dtype,batch_size=2):
                super(QModel, self).__init__()

                self._num_wires = num_wires
                self._dtype = dtype
                self.qm = TNQMachine(num_wires, dtype=dtype)

                self.w = Parameter((2,4,3),initializer=pyvqnet.utils.initializer.quantum_uniform)
                self.cnot = CNOT(wires=[0, 1])
                self.batch_size = batch_size
            def forward(self, x, *args, **kwargs):
                self.qm.reset_states(batchsize=self.batch_size)

                def get_cnot(nqubits,qm):
                    for i in range(len(nqubits) - 1):
                        CNOT(wires = [nqubits[i], nqubits[i + 1]])(q_machine = qm)
                    CNOT(wires = [nqubits[len(nqubits) - 1], nqubits[0]])(q_machine = qm)


                def build_circult(weights, xx, nqubits,qm):
                    def Rot(weights_j, nqubits,qm):#pylint:disable=invalid-name
                        VQC_RotCircuit(qm,nqubits,weights_j)

                    def basisstate(qm,xx, nqubits):
                        for i in nqubits:
                            qcircuit.rz(q_machine=qm, wires=i, params=xx[i])
                            qcircuit.ry(q_machine=qm, wires=i, params=xx[i])
                            qcircuit.rz(q_machine=qm, wires=i, params=xx[i])

                    basisstate(qm,xx,nqubits)

                    for i in range(weights.shape[0]):

                        weights_i = weights[i, :, :]
                        for j in range(len(nqubits)):
                            weights_j = weights_i[j]
                            Rot(weights_j, nqubits[j],qm)
                        get_cnot(nqubits,qm)

                build_circult(self.w, x,range(4),self.qm)

                y= qmeasure.MeasureAll(obs={\'Z0\': 1})(self.qm)
                return y


        x= pyvqnet.tensor.QTensor([[1,0,0,1],[1,1,0,1]],dtype=pyvqnet.kfloat32)
        model = QModel(4,pyvqnet.kcomplex64,2)
        y = model(x)
        y.backward()
    
    '''
    use_mps: Incomplete
    def __init__(self, num_wires: int, dtype: int = ..., use_mps: bool = False) -> None: ...
    def get_states(self): ...
