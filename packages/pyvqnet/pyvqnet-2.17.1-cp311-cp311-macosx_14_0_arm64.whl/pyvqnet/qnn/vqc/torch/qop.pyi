from ....dtype import C_DTYPE as C_DTYPE, kcomplex64 as kcomplex64
from ....nn.torch import TorchModule as TorchModule
from ....tensor import QTensor as QTensor, tensor as tensor
from ....torch import float_to_complex_param as float_to_complex_param
from ..qmachine import AbstractQMachine as AbstractQMachine
from ..qmatrix import double_mat_dict as double_mat_dict, float_mat_dict as float_mat_dict, half_float_mat_dict as half_float_mat_dict
from ..qop import DiagonalOperation as NDiagonalOperation, Observable as NObservable, Operation as NOperation, Operator as NOperator, QMachine as NQMachine, QModule as NQModule, StateEncoder as NStateEncoder
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock

dtype_mat_callable_dict: Incomplete

class QModule(TorchModule, NQModule):
    def __init__(self, name: str = '') -> None: ...

class Encoder(TorchModule):
    def __init__(self) -> None: ...

class StateEncoder(Encoder, NStateEncoder):
    def __init__(self) -> None: ...
    def forward(self, x, q_machine) -> None: ...

class Operator(QModule, NOperator):
    dtype_mat_callable_dict = dtype_mat_callable_dict
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
