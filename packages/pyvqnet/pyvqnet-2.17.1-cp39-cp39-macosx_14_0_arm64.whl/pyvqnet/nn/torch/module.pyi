import torch
from ...backends import get_backend_name as get_backend_name
from ...device import DEV_CPU as DEV_CPU, DEV_GPU_0 as DEV_GPU_0
from ...tensor import QTensor as QTensor, tensor as tensor
from ...torch import to_device as to_device
from ..module import Module as Module, ModuleDict as ModuleDict, ModuleList as ModuleList, ParameterDict as ParameterDict, ParameterList as ParameterList, Sequential as Sequential
from ..parameter import Parameter as Parameter
from _typeshed import Incomplete
from collections import deque as deque, namedtuple as namedtuple
from pyvqnet.backends_mock import TorchMock as TorchMock
from typing import Iterable, Iterator, Mapping

class TorchModuleList(ModuleList, torch.nn.ModuleList):
    """
    torch backend module list

    
    """
    def __init__(self, modules: Incomplete | None = None) -> None:
        '''
        :param modules: list of modules.
        
        Example::

            from pyvqnet.tensor import *
            from pyvqnet.nn.torch import TorchModule,Linear,TorchModuleList

            import pyvqnet
            pyvqnet.backends.set_backend("torch")

            class M(TorchModule):
                def __init__(self):
                    super(M, self).__init__()
                    self.pqc2 = TorchModuleList([Linear(4,1), Linear(4,1)
                    ])

                def forward(self, x):
                    y = self.pqc2[0](x)  + self.pqc2[1](x)
                    return y

            mm = M()
        '''

class TorchModule(Module, torch.nn.Module):
    """
    This class the basic class to define a nn module for torch backend.
    The parameters in TorchModule is torch.Tensor type.
    """
    def __init__(self, *args, **kwargs) -> None:
        """
        The base class for users defined nerual network module when use torch backend.
        """
    def __setattr__(self, name: str, value) -> None: ...
    train_mode: Incomplete
    training: Incomplete
    def train(self, mode: bool = True): ...
    def eval(self) -> None:
        """
        Prepares module for evaluation.
        """
    def register_parameter(self, name: str, param: Parameter | None) -> None: ...
    def to_gpu(self, device=...): ...
    toGPU = to_gpu
    def to_cpu(self): ...
    toCPU = to_cpu
    def to(self, device):
        """
        move paramters and buffers of modules and its submodule into target device.
        """

class TorchModuleDict(TorchModule, torch.nn.ModuleDict):
    def __init__(self, modules: Mapping[str, TorchModule] | None = None) -> None: ...
    def __getitem__(self, key: str) -> TorchModule: ...
    def __setitem__(self, key: str, module: TorchModule) -> None: ...
    def __delitem__(self, key: str) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[str]: ...
    def __contains__(self, key: str) -> bool: ...
    def clear(self) -> None:
        """Remove all items from the ModuleDict.
        """
    def pop(self, key: str) -> TorchModule:
        """Remove key from the ModuleDict and return its module.

        Args:
            key (str): key to pop from the ModuleDict
        """
    def keys(self) -> Iterable[str]:
        """Return an iterable of the ModuleDict keys.
        """
    def items(self) -> Iterable[tuple[str, TorchModule]]:
        """Return an iterable of the ModuleDict key/value pairs.
        """
    def values(self) -> Iterable[TorchModule]:
        """Return an iterable of the ModuleDict values.
        """
    def update(self, modules: Mapping[str, TorchModule]) -> None:
        """Update the :class:`~nn.ModuleDict` with the key-value pairs from a
        mapping or an iterable, overwriting existing keys.

        .. note::
            If :attr:`modules` is an ``OrderedDict``, a :class:`~nn.ModuleDict`, or
            an iterable of key-value pairs, the order of new elements in it is preserved.

        Args:
            modules (iterable): a mapping (dictionary) from string to :class:`~nn.Module`,
                or an iterable of key-value pairs of type (string, :class:`~nn.Module`)
        """

class TorchParameterDict(TorchModule, ParameterDict):
    """
    This class inherits from TorchModule and ParameterDict, which constructs Parameters dict for TorchModule.
    The variable constructed by this class is QTensor type, which .data attribute stores the torch.nn.Parameter data.
    """
    def __init__(self, values: Incomplete | None = None) -> None: ...

class TorchParameterList(TorchModule, ParameterList):
    """
    This class inherits from TorchModule and ParameterList, which constructs Parameters list for TorchModule.
    The variable constructed by this class is QTensor type, which .data attribute stores the torch.nn.Parameter data.
    """
    def __init__(self, values: Incomplete | None = None) -> None:
        '''
        :param values: list of paramaters

        Example::

            from pyvqnet.tensor import *
            from pyvqnet.nn.torch import TorchModule,Linear,TorchParameterList
            import pyvqnet.nn as nn
            import pyvqnet
            pyvqnet.backends.set_backend("torch")
            class MyModule(TorchModule):
                def __init__(self):
                    super().__init__()
                    self.params = TorchParameterList([nn.Parameter((10, 10)) for i in range(10)])
                def forward(self, x):

                    # ParameterList can act as an iterable, or be indexed using ints
                    for i, p in enumerate(self.params):
                        x = self.params[i // 2] * x + p * x
                    return x

            model = MyModule()
            print(model.state_dict().keys())
        '''

class TorchSequential(TorchModule, Sequential):
    """
    torch backend of sequential.
    """
    def __init__(self, *args) -> None:
        '''
        :param args: modules to append.

        Example::
        
            import pyvqnet
            from collections import OrderedDict
            from pyvqnet.tensor import *
            from pyvqnet.nn.torch import TorchModule,Conv2D,ReLu,                TorchSequential
            pyvqnet.backends.set_backend("torch")
            model = TorchSequential(
                        Conv2D(1,20,(5, 5)),
                        ReLu(),
                        Conv2D(20,64,(5, 5)),
                        ReLu()
                    )
            print(model.state_dict().keys())

            model = TorchSequential(OrderedDict([
                        (\'conv1\', Conv2D(1,20,(5, 5))),
                        (\'relu1\', ReLu()),
                        (\'conv2\', Conv2D(20,64,(5, 5))),
                        (\'relu2\', ReLu())
                    ]))
            print(model.state_dict().keys())

        '''
