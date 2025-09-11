from _typeshed import Incomplete
from collections import namedtuple as namedtuple
from pyvqnet.backends import global_backend as global_backend
from pyvqnet.device import DEV_CPU as DEV_CPU, DEV_GPU_0 as DEV_GPU_0
from pyvqnet.nn.parameter import Parameter as Parameter
from pyvqnet.tensor import tensor as tensor
from pyvqnet.tensor.tensor import QTensor as QTensor
from typing import Any, Callable, Iterable, Iterator, Mapping, TypeVar, overload
from typing_extensions import Self

class Module:
    """Base class for all neural network modules including quantum modules or classic modules.

        Your models should also be subclass of this class for autograd calculation.

        Modules can also contain other Modules, allowing to nest them in
        a tree structure. You can assign the submodules as regular attributes::

            class Model(Module):
                def __init__(self):
                    super(Model, self).__init__()
                    self.conv1 = pyvqnet.nn.Conv2d(1, 20, (5,5))
                    self.conv2 = pyvqnet.nn.Conv2d(20, 20, (5,5))

                def forward(self, x):
                    x = pyvqnet.nn.activation.relu(self.conv1(x))
                    return pyvqnet.nn.activation.relu(self.conv2(x))

        Submodules assigned in this way will be registered

        """
    train_mode: bool
    training: bool
    name: Incomplete
    backend: int
    def __init__(self, *args, **kwargs) -> None:
        """
        Represents abstract module in a neural network.
        """
    def register_buffer(self, name: str, tensor_buffer: QTensor | None) -> None:
        """Adds a buffer to the module.

        This is typically used to register a buffer that should not to be
        considered a model parameter. For example, BatchNorm's ``running_mean``
        is not a parameter, but is part of the module's state.

        Buffers can be accessed as attributes using given names.

        :param name: name of the buffer. The buffer can be accessed
            from this module using the given name
        :param tensor_buffer: buffer to be registered.

        Example::

            from pyvqnet.nn import Linear
            from pyvqnet.tensor import tensor
            a = Linear(2,5)
            a.register_buffer('running_mean', tensor.zeros((2,2,)))

        """
    def register_parameter(self, name: str, param: Parameter | None) -> None:
        """Adds a parameter to the module.

        The parameter can be accessed as an attribute using given name.

        :param name: name of the parameter. The parameter can be accessed
            from this module using the given name
        :param tensor: parameter to be added to the module.

        Example::

            from pyvqnet.nn import Linear
            from pyvqnet.tensor import tensor
            a = Linear(2,5)
            a.register_parameter('running_mean', tensor.zeros((2,2,)))
        """
    def add_module(self, name: str, module: Module | None) -> None:
        """Adds a child module to the current module.

        The module can be accessed as an attribute using the given name.

        :param name (string): name of the child module. The child module can be
                accessed from this module using the given name
        :param module (Module): child module to be added to the module.
        """
    def __getattr__(self, name: str) -> QTensor | Module: ...
    def __setattr__(self, name: str, value: QTensor | Module) -> None: ...
    def __delattr__(self, name) -> None: ...
    def children(self) -> Iterator['Module']:
        """Returns an iterator over immediate children modules.

        Yields:
            Module: a child module
        """
    def named_children(self) -> Iterator[tuple[str, 'Module']]:
        """Returns an iterator over immediate children modules, yielding both
        the name of the module as well as the module itself.

        Yields:
            (string, Module): Tuple containing a name and child module

        Example::

            >>> for name, module in model.named_children():
            >>>     if name in ['conv4', 'conv5']:
            >>>         print(module)

        """
    def named_modules(self, memo: set['Module'] | None = None, prefix: str = '', remove_duplicate: bool = True):
        """Returns an iterator over all modules in the network, yielding
        both the name of the module as well as the module itself.

        Args:
            memo: a memo to store the set of modules already added to the result
            prefix: a prefix that will be added to the name of the module
            remove_duplicate: whether to remove the duplicated module instances in the result
                or not

        Yields:
            (str, Module): Tuple of name and module

        Note:
            Duplicate modules are returned only once. In the following
            example, ``l`` will be returned only once.


        """
    def named_buffers(self, prefix: str = '', recurse: bool = True, remove_duplicate: bool = True) -> Iterator[tuple[str, QTensor]]:
        """Return an iterator over module buffers, yielding both the name of the buffer as well as the buffer itself.

        Args:
            prefix (str): prefix to prepend to all buffer names.
            recurse (bool, optional): if True, then yields buffers of this module
                and all submodules. Otherwise, yields only buffers that
                are direct members of this module. Defaults to True.
            remove_duplicate (bool, optional): whether to remove the duplicated buffers in the result. Defaults to True.

        Yields:
            (str, QTensor): Tuple containing the name and buffer

 

        """
    def named_parameters(self, prefix: str = '', recurse: bool = True, remove_duplicate: bool = True) -> Iterator[tuple[str, Parameter]]:
        """Returns an iterator over module parameters, yielding both the
        name of the parameter as well as the parameter itself.


            :param prefix (str): prefix to prepend to all parameter names.
            :param recurse (bool): if True, then yields parameters of this module
                and all submodules. Otherwise, yields only parameters that
                are direct members of this module.
            :param remove_duplicate: (bool, optional): whether to remove the duplicated
                parameters in the result. Defaults to True.
        Yields:
            (str, Parameter): Tuple containing the name and parameter

 

        """
    T_destination = TypeVar('T_destination', bound=dict[str, Any])
    def state_dict(self, destination: T_destination = None, prefix: str = '', keep_vars: bool = False):
        """Returns a dictionary containing a whole state of the module.

        Both parameters and persistent buffers (e.g. running averages) are
        included. Keys are corresponding parameter and buffer names.

        :param destination: a dict where state will be stored
        :param prefix: the prefix for parameters and buffers used in this
            module
        :param keep_vars: by default the :class:`~QTensor` s
                returned in the state dict are detached from autograd. If it's
                set to ``True``, detaching will not be performed.
                Default: ``False``.

        :return: a dictionary containing a whole state of the module

        Example::

            module.state_dict().keys()
            ['bias', 'weight']

        """
    def apply(self, fn): ...
    def to_gpu(self, device=...):
        '''
        Move Module and it\'s paramters and buffers into specific GPU device.

        device specifies the device where the it\'s inner data is stored. When device = DEV_CPU
        the data is stored on the CPU, and when device >= DEV_GPU_0, the data is stored on the GPU.
        If your computer has multiple GPUs, you can specify different devices for data storage.
        For example, device = 1001, 1002, 1003, ... means stored on GPUs with different serial numbers.
        
        Note:

            Module in different GPU could not do calculation. 
            If you try to create a QTensor on GPU with id more than maximum number
            of validate GPUs, will raise Cuda Error.

        :param device: current device to save QTensor , default = 0,stored in cpu. device= pyvqnet.DEV_GPU_0,
        stored in 1st GPU, devcie  = 1001,stored in 2nd GPU,and so on

        :return: the module move to GPU device

        Example::

                from pyvqnet.nn.conv import ConvT2D 
                test_conv = ConvT2D(3, 2, [4,4], [2, 2], "same")
                test_conv = test_conv.toGPU()
                print(test_conv.backend)
                #1000
        '''
    toGPU = to_gpu
    def to_cpu(self):
        '''
        Move Module and it\'s paramters and buffers into CPU device.

        :return: the module move to CPU device

        Example::

                from pyvqnet.nn.conv import ConvT2D 
                test_conv = ConvT2D(3, 2, [4,4], [2, 2], "same")
                test_conv = test_conv.toCPU()
                print(test_conv.backend)
                #0
        '''
    toCPU = to_cpu
    def to(self, device): ...
    def load_state_dict(self, state_dict: Mapping[str, Any], strict: bool = True) -> None:
        '''Copies parameters and buffers from :attr:`state_dict` into
        this module and its descendants.

        :param state_dict : a dict containing parameters and persistent buffers.
        :param strict: whether to strictly enforce that the keys in state_dict match the model\'s state_dict().

        :return: error msg if encouters.
        
        Example::

            from pyvqnet.nn import Module,Conv2D
            import pyvqnet

            class Net(Module):
                def __init__(self):
                    super(Net, self).__init__()
                    self.conv1 = Conv2D(input_channels=1, output_channels=6, kernel_size=(5, 5),
                     stride=(1, 1), padding="valid")

                def forward(self, x):
                    return super().forward(x)

            model = Net()
            pyvqnet.utils.storage.save_parameters(model.state_dict(), "tmp.model")
            model_param =  pyvqnet.utils.storage.load_parameters("tmp.model")
            model.load_state_dict(model_param)
        '''
    def parameters(self, recurse: bool = True) -> list[Parameter]:
        """
        Returns all the parameters from the subclass module.

        :param recurse (bool): if True, then output parameters of this module
                and all submodules. Otherwise, output only parameters that
                are direct members of this module.
        """
    def modules(self):
        """
        Returns all the modules for current class.
        """
    def __call__(self, x, *args, **kwargs):
        """
        Redefined call operator.
        """
    forward: Callable[..., Any]
    def train(self, mode: bool = True):
        """Sets the module in training mode.

        This has any effect only on certain modules. See documentations of
        particular modules for details of their behaviors in training/evaluation
        mode, if they are affected, e.g. :class:`Dropout`, :class:`BatchNorm`,
        etc.

        :param mode (bool): whether to set training mode (``True``) or evaluation
                         mode (``False``). Default: ``True``.

        :return: Module: self
        """
    def eval(self) -> None:
        """
        Prepares module for evaluation.It may influence dropout or batchnorm and etc.
        """
    def zero_grad(self) -> None:
        """
        Sets all parameters and buffers' gradients to zero.
        """

class ModuleList(Module):
    '''    
    
    Holds submodules in a list. ModuleList can be indexed like a regular Python list, but
    modules it contains are properly registered, sucn as Parameters.

    :param modules: lists of nn.Modules

    :return: a ModuleList

    Example::
    
        from pyvqnet.tensor import *
        from pyvqnet.nn import Module,Linear,ModuleList
        from pyvqnet.qnn import ProbsMeasure,QuantumLayer
        import pyqpanda as pq
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


        class M(Module):
            def __init__(self):
                super(M, self).__init__()
                self.pqc2 = ModuleList([QuantumLayer(pqctest,3,"cpu",4,1), Linear(4,1)
                ])

            def forward(self, x, *args, **kwargs):
                y = self.pqc2[0](x)  + self.pqc2[1](x)
                return y

        mm = M()
        print(mm.state_dict().keys())
        #odict_keys([\'pqc2.0.m_para\', \'pqc2.1.weights\', \'pqc2.1.bias\'])


    '''
    def __init__(self, modules: Iterable[Module] | None = None) -> None: ...
    def __getitem__(self, idx: int | slice) -> Module | ModuleList: ...
    def __setitem__(self, idx: int, module: Module) -> None: ...
    def __delitem__(self, idx: int | slice) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Module]: ...
    def __iadd__(self, modules: Iterable[Module]) -> ModuleList: ...
    def __add__(self, other: Iterable[Module]) -> ModuleList: ...
    def __dir__(self): ...
    def insert(self, index: int, module: Module) -> None:
        """Insert a given module before a given index in the list.

        Args:
            index (int): index to insert.
            module (nn.Module): module to insert
        """
    def append(self, module: Module) -> ModuleList:
        """Appends a given module to the end of the list.

        Args:
            module (nn.Module): module to append
        """
    def extend(self, modules: Iterable[Module]) -> ModuleList:
        """Appends modules from a Python iterable to the end of the list.

        Args:
            modules (iterable): iterable of modules to append
        """
    def forward(self, x, *args, **kwargs) -> None:
        """

        """
T = TypeVar('T', bound=Module)

class ParameterDict(Module):
    """Holds parameters in a dictionary.

    ParameterDict can be indexed like a regular Python dictionary, but Parameters it
    contains are properly registered, and will be visible by all Module methods.
    Other objects are treated as would be done by a regular Python dictionary

    :class:`~pyvqnet.nn.ParameterDict` is an **ordered** dictionary.
    :meth:`~pyvqnet.nn.ParameterDict.update` with other unordered mapping
    types (e.g., Python's plain ``dict``) does not preserve the order of the
    merged mapping. On the other hand, ``OrderedDict`` or another :class:`~pyvqnet.nn.ParameterDict`
    will preserve their ordering.

    Note that the constructor, assigning an element of the dictionary and the
    :meth:`~pyvqnet.nn.ParameterDict.update` method will convert any :class:`~pyvqnet.Tensor` into
    :class:`~pyvqnet.nn.Parameter`.

    Args:
        values (iterable, optional): a mapping (dictionary) of
            (string : Any) or an iterable of key-value pairs
            of type (string, Any)

    """
    def __init__(self, parameters: Any = None) -> None: ...
    def __getitem__(self, key: str) -> Any: ...
    def __setitem__(self, key: str, value: Any) -> None: ...
    def __delitem__(self, key: str) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[str]: ...
    def __reversed__(self) -> Iterator[str]: ...
    def copy(self) -> ParameterDict:
        """Return a copy of this :class:`~pyvqnet.nn.ParameterDict` instance."""
    def __contains__(self, key: str) -> bool: ...
    def setdefault(self, key: str, default: Any | None = None) -> Any:
        """Set the default for a key in the Parameterdict.

        If key is in the ParameterDict, return its value.
        If not, insert `key` with a parameter `default` and return `default`.
        `default` defaults to `None`.

        Args:
            key (str): key to set default for
            default (Any): the parameter set to the key
        """
    def clear(self) -> None:
        """Remove all items from the ParameterDict."""
    def pop(self, key: str) -> Any:
        """Remove key from the ParameterDict and return its parameter.

        Args:
            key (str): key to pop from the ParameterDict
        """
    def popitem(self) -> tuple[str, Any]:
        """Remove and return the last inserted `(key, parameter)` pair from the ParameterDict."""
    def get(self, key: str, default: Any | None = None) -> Any:
        """Return the parameter associated with key if present. Otherwise return default if provided, None if not.

        Args:
            key (str): key to get from the ParameterDict
            default (Parameter, optional): value to return if key not present
        """
    def fromkeys(self, keys: Iterable[str], default: Any | None = None) -> ParameterDict:
        """Return a new ParameterDict with the keys provided.

        Args:
            keys (iterable, string): keys to make the new ParameterDict from
            default (Parameter, optional): value to set for all keys
        """
    def keys(self) -> Iterable[str]:
        """Return an iterable of the ParameterDict keys."""
    def items(self) -> Iterable[tuple[str, Any]]:
        """Return an iterable of the ParameterDict key/value pairs."""
    def values(self) -> Iterable[Any]:
        """Return an iterable of the ParameterDict values."""
    def update(self, parameters: Mapping[str, Any] | ParameterDict) -> None:
        """Update the :class:`~pyvqnet.nn.ParameterDict` with key-value pairs from ``parameters``, overwriting existing keys.

        .. note::
            If :attr:`parameters` is an ``OrderedDict``, a :class:`~pyvqnet.nn.ParameterDict`, or
            an iterable of key-value pairs, the order of new elements in it is preserved.

        Args:
            parameters (iterable): a mapping (dictionary) from string to
                :class:`~pyvqnet.nn.Parameter`, or an iterable of
                key-value pairs of type (string, :class:`~pyvqnet.nn.Parameter`)
        """
    def __call__(self, input) -> None: ...
    def __or__(self, other: ParameterDict) -> ParameterDict: ...
    def __ror__(self, other: ParameterDict) -> ParameterDict: ...
    def __ior__(self, other: ParameterDict) -> Self: ...

class ParameterList(Module):
    """
    Holds parameters in a list.

    :class:`~pyvqnet.nn.ParameterList` can be used like a regular Python
    list, but Tensors that are :class:`~pyvqnet.nn.Parameter` are properly registered,
    and will be visible by all :class:`~pyvqnet.nn.Module` methods.

    Note that the constructor, assigning an element of the list, the
    :meth:`~pyvqnet.nn.ParameterDict.append` method and the :meth:`~pyvqnet.nn.ParameterDict.extend`
    method will convert any :class:`~pyvqnet.Tensor` into :class:`~pyvqnet.nn.Parameter`.

    :param values: lists of nn.Parameter
    
    :return: a ParameterList
    
    Example::

        import pyvqnet.nn as nn

        class MyModule(nn.Module):
            def __init__(self):
                super().__init__()
                self.params = nn.ParameterList(
                    [nn.Parameter((10, 10)) for i in range(10)])

            def forward(self, x):

                # ParameterList can act as an iterable, or be indexed using ints
                for i, p in enumerate(self.params):
                    x = self.params[i // 2] * x + p * x
                return x


        model = MyModule()
        print(model.state_dict().keys())

    """
    def __init__(self, values: Iterable[Parameter] | None = None) -> None: ...
    @overload
    def __getitem__(self, idx: int) -> Parameter: ...
    @overload
    def __getitem__(self, idx: slice) -> T: ...
    def __setitem__(self, idx: int, param: QTensor | Parameter) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[Parameter]: ...
    def __iadd__(self, parameters: Iterable[Parameter]) -> ParameterList: ...
    def __dir__(self): ...
    def append(self, value: Parameter) -> ParameterList:
        """Appends a given value at the end of the list.

        Args:
            value (Any): value to append
        """
    def extend(self, values: Iterable[Parameter]) -> ParameterList:
        """Appends values from a Python iterable to the end of the list.

        Args:
            values (iterable): iterable of values to append
        """
    def forward(self, x, *args, **kwargs) -> None:
        """

        """

class Sequential(Module):
    '''A sequential container.
    Modules will be added to it in the order they are passed in the
    constructor. Alternatively, an ``OrderedDict`` of modules can be
    passed in. The ``forward()`` method of ``Sequential`` accepts any
    input and forwards it to the first module it contains. It then
    "chains" outputs to inputs sequentially for each subsequent module,
    finally returning the output of the last module.

    The value a ``Sequential`` provides over manually calling a sequence
    of modules is that it allows treating the whole container as a
    single module, such that performing a transformation on the
    ``Sequential`` applies to each of the modules it stores (which are
    each a registered submodule of the ``Sequential``).

    What\'s the difference between a ``Sequential`` and a
    :class:`pyvqnet.nn.ModuleList`? A ``ModuleList`` is exactly what it
    sounds like--a list for storing ``Module`` s! On the other hand,
    the layers in a ``Sequential`` are connected in a cascading way.

    :param values: module to append
    
    :return: Sequential
    

    '''
    def __init__(self, *args) -> None: ...
    def __getitem__(self, idx: slice | int) -> Sequential | T: ...
    def __setitem__(self, idx: int, module: Module) -> None: ...
    def __delitem__(self, idx: slice | int) -> None: ...
    def __len__(self) -> int: ...
    def __add__(self, other) -> Sequential: ...
    def pop(self, key: int | slice) -> Module: ...
    def __iadd__(self, other) -> Sequential: ...
    def __mul__(self, other: int) -> Sequential: ...
    def __rmul__(self, other: int) -> Sequential: ...
    def __imul__(self, other: int) -> Sequential: ...
    def __dir__(self): ...
    def __iter__(self) -> Iterator[Module]: ...
    def forward(self, input): ...
    def append(self, module: Module) -> Sequential:
        """Appends a given module to the end.

        Args:
            module (nn.Module): module to append
        """
    def insert(self, index: int, module: Module) -> Sequential: ...
    def extend(self, sequential) -> Sequential: ...

class ModuleDict(Module):
    """Holds submodules in a dictionary.

    :class:`~nn.ModuleDict` can be indexed like a regular Python dictionary,
    but modules it contains are properly registered, and will be visible by all
    :class:`~nn.Module` methods.

    :class:`~nn.ModuleDict` is an **ordered** dictionary that respects

    * the order of insertion, and

    * in :meth:`~nn.ModuleDict.update`, the order of the merged
      ``OrderedDict``, ``dict`` (started from Python 3.6) or another
      :class:`~nn.ModuleDict` (the argument to
      :meth:`~nn.ModuleDict.update`).

    Note that :meth:`~nn.ModuleDict.update` with other unordered mapping
    types (e.g., Python's plain ``dict`` before Python version 3.6) does not
    preserve the order of the merged mapping.

    Args:
        modules (iterable, optional): a mapping (dictionary) of (string: module)
            or an iterable of key-value pairs of type (string, module)

    Example::

        class MyModule(nn.Module):
            def __init__(self):
                super().__init__()
                self.choices = nn.ModuleDict({
                        'conv': nn.Conv2d(10, 10, 3),
                        'pool': nn.MaxPool2d(3)
                })
                self.activations = nn.ModuleDict([
                        ['lrelu', nn.LeakyReLU()],
                        ['prelu', nn.PReLU()]
                ])

            def forward(self, x, choice, act):
                x = self.choices[choice](x)
                x = self.activations[act](x)
                return x
    """
    def __init__(self, modules: Mapping[str, Module] | None = None) -> None: ...
    def __getitem__(self, key: str) -> Module: ...
    def __setitem__(self, key: str, module: Module) -> None: ...
    def __delitem__(self, key: str) -> None: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[str]: ...
    def __contains__(self, key: str) -> bool: ...
    def clear(self) -> None:
        """Remove all items from the ModuleDict.
        """
    def pop(self, key: str) -> Module:
        """Remove key from the ModuleDict and return its module.

        Args:
            key (str): key to pop from the ModuleDict
        """
    def keys(self) -> Iterable[str]:
        """Return an iterable of the ModuleDict keys.
        """
    def items(self) -> Iterable[tuple[str, Module]]:
        """Return an iterable of the ModuleDict key/value pairs.
        """
    def values(self) -> Iterable[Module]:
        """Return an iterable of the ModuleDict values.
        """
    def update(self, modules: Mapping[str, Module]) -> None:
        """Update the :class:`~nn.ModuleDict` with the key-value pairs from a
        mapping or an iterable, overwriting existing keys.

        .. note::
            If :attr:`modules` is an ``OrderedDict``, a :class:`~nn.ModuleDict`, or
            an iterable of key-value pairs, the order of new elements in it is preserved.

        Args:
            modules (iterable): a mapping (dictionary) from string to :class:`~nn.Module`,
                or an iterable of key-value pairs of type (string, :class:`~nn.Module`)
        """
