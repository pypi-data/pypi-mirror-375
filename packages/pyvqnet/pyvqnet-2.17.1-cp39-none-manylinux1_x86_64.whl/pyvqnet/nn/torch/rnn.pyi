from ...tensor import QTensor as QTensor, index_select as index_select, to_tensor as to_tensor
from ..gru import Dynamic_GRU as NDynamic_GRU, GRU as NGRU
from ..lstm import Dynamic_LSTM as NDynamic_LSTM, LSTM as NLSTM
from ..parameter import Parameter as Parameter
from ..rnn import Dynamic_RNN as NDynamic_RNN, RNN as NRNN
from .module import TorchModule as TorchModule
from pyvqnet.backends_mock import TorchMock as TorchMock

class Dynamic_RNN(TorchModule, NDynamic_RNN):
    '''
    Applies a multi-layer dynamic sequence legnth input RNN with :math:`\\tanh` or :math:`\\text{ReLU}` non-linearity to an
    input.

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.

    The fisrt input should be a batched sequences input with variable length defined 
    by a ``tensor.PackedSequence`` class.
    The ``tensor.PackedSequence`` class could be construced by 
    Consecutive calling of the next functions: ``pad_sequence``, ``pack_pad_sequence``.

    The first output of Dynamic_RNN is also a ``tensor.PackedSequence`` class, 
    which can be unpacked to normal QTensor using ``tensor.pad_pack_sequence``.
 
    For each element in the input , each layer computes the following
    function:

    .. math::
        h_t = \\tanh(W_{ih} x_t + b_{ih} + W_{hh} h_{(t-1)} + b_{hh})

    where :math:`h_t` is the hidden state at time `t`, :math:`x_t` is
    the input at time `t`, and :math:`h_{(t-1)}` is the hidden state of the
    previous layer at time `t-1` or the initial hidden state at time `0`.
    If :attr:`nonlinearity` is ``\'relu\'``, then :math:`\\text{ReLU}` is used instead of :math:`\\tanh`.

    :param input_size: Input feature dimension.
    :param hidden_size:  Hidden feature dimension.
    :param num_layers: Number of recurrent layers. Default: 1.
    :param nonlinearity: nonlinearity function, `tanh` or `relu` , Default: `tanh`.
    :param batch_first: If True, input shape is provided as [batch_size,seq_len,feature_dim],
    if False, input shape is provided as [seq_len,batch_size,feature_dim],default True
    :param use_bias: If False, then the layer does not use bias weights b_ih and b_hh. Default: True.
    :param bidirectional: If RNN, becomes a bidirectional RNN. Default: False.

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a Dynamic_RNN class


    '''
    def __init__(self, input_size: int, hidden_size: int, num_layers: int = 1, nonlinearity: bool = 'tanh', batch_first: bool = True, use_bias: bool = True, bidirectional: bool = False, dtype: int | None = None, name: str = '') -> None: ...
    def __setattr__(self, attr, value) -> None: ...
    def forward(self, x, init_states): ...

class Dynamic_LSTM(TorchModule, NDynamic_LSTM):
    '''
    Applies a multi-layer dynamic sequence legnth input LSTM(Long Short Term Memory) Module.

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.

    The fisrt input should be a batched sequences input with variable length defined 
    by a ``tensor.PackedSequence`` class.
    The ``tensor.PackedSequence`` class could be construced by 
    Consecutive calling of the next functions: ``pad_sequence``, ``pack_pad_sequence``.

    The first output of Dynamic_LSTM is also a ``tensor.PackedSequence`` class, 
    which can be unpacked to normal QTensor using ``tensor.pad_pack_sequence``.
    
    Each call computes the following function:

    .. math::
        \x08egin{array}{ll} \\\n            i_t = \\sigma(W_{ii} x_t + b_{ii} + W_{hi} h_{t-1} + b_{hi}) \\\n            f_t = \\sigma(W_{if} x_t + b_{if} + W_{hf} h_{t-1} + b_{hf}) \\\n            g_t = \tanh(W_{ig} x_t + b_{ig} + W_{hg} h_{t-1} + b_{hg}) \\\n            o_t = \\sigma(W_{io} x_t + b_{io} + W_{ho} h_{t-1} + b_{ho}) \\\n            c_t = f_t \\odot c_{t-1} + i_t \\odot g_t \\\n            h_t = o_t \\odot \tanh(c_t) \\\n        \\end{array}

    :param input_size: Input feature dimension.
    :param hidden_size:  Hidden feature dimension.
    :param num_layers: Number of recurrent layers. Default: 1
    :param batch_first: If True, input shape is provided as [batch_size,seq_len,feature_dim],
    if False, input shape is provided as [seq_len,batch_size,feature_dim],default True
    :param use_bias: If False, then the layer does not use bias weights b_ih and b_hh. Default: True.
    :param bidirectional: If True, becomes a bidirectional LSTM. Default: False.
    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a LSTM class

     
        '''
    def __init__(self, input_size: int, hidden_size: int, num_layers: int = 1, batch_first: bool = True, use_bias: bool = True, bidirectional: bool = False, dtype: int | None = None, name: str = '') -> None: ...
    def __setattr__(self, attr, value) -> None: ...
    def forward(self, x, init_states): ...

class Dynamic_GRU(TorchModule, NDynamic_GRU):
    '''
    Applies a multi-layer gated recurrent unit (GRU) RNN to an dyanmaic length input sequence.

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.

    The fisrt input should be a batched sequences input with variable length defined 
    by a ``tensor.PackedSequence`` class.
    The ``tensor.PackedSequence`` class could be construced by 
    Consecutive calling of the next functions: ``pad_sequence``, ``pack_pad_sequence``.

    The first output of Dynamic_GRU is also a ``tensor.PackedSequence`` class, 
    which can be unpacked to normal QTensor using ``tensor.pad_pack_sequence``.

    For each element in the input sequence, each layer computes the following
    function:

    .. math::
        \\begin{array}{ll}
            r_t = \\sigma(W_{ir} x_t + b_{ir} + W_{hr} h_{(t-1)} + b_{hr}) \\\\\n            z_t = \\sigma(W_{iz} x_t + b_{iz} + W_{hz} h_{(t-1)} + b_{hz}) \\\\\n            n_t = \\tanh(W_{in} x_t + b_{in} + r_t * (W_{hn} h_{(t-1)}+ b_{hn})) \\\\\n            h_t = (1 - z_t) * n_t + z_t * h_{(t-1)}
        \\end{array}

    :param input_size: Input feature dimension.
    :param hidden_size: Hidden feature dimension.
    :param num_layers: Number of recurrent layers. Default: 1
    :param batch_first: If True, input shape is provided as [batch_size,seq_len,feature_dim],
    if False, input shape is provided as [seq_len,batch_size,feature_dim],default True
    :param use_bias: If False, then the layer does not use bias weights b_ih and b_hh. Default: True.
    :param bidirectional: If True, becomes a bidirectional GRU. Default: False.

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a Dynamic_GRU class
    '''
    def __init__(self, input_size: int, hidden_size: int, num_layers: int = 1, batch_first: bool = True, use_bias: bool = True, bidirectional: bool = False, dtype: int | None = None, name: str = '') -> None: ...
    def __setattr__(self, attr, value) -> None: ...
    def forward(self, x, init_states): ...

class LSTM(TorchModule, NLSTM):
    '''
    Long-Short Term Memory (LSTM) network cell.

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.


    Each call computes the following function:

    .. math::
        \x08egin{array}{ll} \\\n            i_t = \\sigma(W_{ii} x_t + b_{ii} + W_{hi} h_{t-1} + b_{hi}) \\\n            f_t = \\sigma(W_{if} x_t + b_{if} + W_{hf} h_{t-1} + b_{hf}) \\\n            g_t = \tanh(W_{ig} x_t + b_{ig} + W_{hg} h_{t-1} + b_{hg}) \\\n            o_t = \\sigma(W_{io} x_t + b_{io} + W_{ho} h_{t-1} + b_{ho}) \\\n            c_t = f_t \\odot c_{t-1} + i_t \\odot g_t \\\n            h_t = o_t \\odot \tanh(c_t) \\\n        \\end{array}

    :param input_size: Input feature dimension.
    :param hidden_size:  Hidden feature dimension.
    :param num_layers: Number of recurrent layers. Default: 1
    :param batch_first: If True, input shape is provided as [batch_size,seq_len,feature_dim],
    if False, input shape is provided as [seq_len,batch_size,feature_dim],default True
    :param use_bias: If False, then the layer does not use bias weights b_ih and b_hh. Default: True.
    :param bidirectional: If True, becomes a bidirectional LSTM. Default: False.
    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".

    :return: a LSTM class
    '''
    def __init__(self, input_size, hidden_size, num_layers: int = 1, batch_first: bool = True, use_bias: bool = True, bidirectional: bool = False, dtype: int | None = None, name: str = '') -> None: ...
    def __setattr__(self, attr, value) -> None: ...
    def forward(self, x, init_states): ...

class RNN(TorchModule, NRNN):
    '''
    Applies a multi-layer simple RNN with :math:`\\tanh` or :math:`\\text{ReLU}` non-linearity to an
    input .

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.

    For each element in the input , each layer computes the following
    function:

    .. math::
        h_t = \\tanh(W_{ih} x_t + b_{ih} + W_{hh} h_{(t-1)} + b_{hh})

    where :math:`h_t` is the hidden state at time `t`, :math:`x_t` is
    the input at time `t`, and :math:`h_{(t-1)}` is the hidden state of the
    previous layer at time `t-1` or the initial hidden state at time `0`.
    If :attr:`nonlinearity` is ``\'relu\'``, then :math:`\\text{ReLU}` is used instead of :math:`\\tanh`.

    :param input_size: Input feature dimension.
    :param hidden_size:  Hidden feature dimension.
    :param num_layers: Number of recurrent layers. Default: 1
    :param nonlinearity: nonlinearity function, `tanh` or `relu` , Default: `tanh`.
    :param batch_first: If True, input shape is provided as [batch_size,seq_len,feature_dim],
    if False, input shape is provided as [seq_len,batch_size,feature_dim],default True
    :param use_bias: If False, then the layer does not use bias weights b_ih and b_hh. Default: True.
    :param bidirectional: If RNN, becomes a bidirectional RNN. Default: False.
    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".

    :return: a RNN class
    '''
    def __init__(self, input_size: int, hidden_size: int, num_layers: int = 1, nonlinearity: str = 'tanh', batch_first: bool = True, use_bias: bool = True, bidirectional: bool = False, dtype: int | None = None, name: str = '') -> None: ...
    def __setattr__(self, attr, value) -> None: ...
    def forward(self, x, init_states): ...

class GRU(TorchModule, NGRU):
    '''
    Applies a multi-layer gated recurrent unit (GRU) RNN to an input sequence.

    This class inherits from ``pyvqnet.nn.Module`` and ``torch.nn.Module``, and can be added to the torch model as a submodule of ``torch.nn.Module``.

    The data in ``_buffers`` of this class is of ``torch.Tensor`` type.
    The data in ``_parmeters`` of this class is of ``torch.nn.Parameter`` type.

    For each element in the input sequence, each layer computes the following
    function:

    .. math::
        \\begin{array}{ll}
            r_t = \\sigma(W_{ir} x_t + b_{ir} + W_{hr} h_{(t-1)} + b_{hr}) \\\\\n            z_t = \\sigma(W_{iz} x_t + b_{iz} + W_{hz} h_{(t-1)} + b_{hz}) \\\\\n            n_t = \\tanh(W_{in} x_t + b_{in} + r_t * (W_{hn} h_{(t-1)}+ b_{hn})) \\\\\n            h_t = (1 - z_t) * n_t + z_t * h_{(t-1)}
        \\end{array}

    :param input_size: Input feature dimension.
    :param hidden_size: Hidden feature dimension.
    :param num_layers: Number of recurrent layers. Default: 1
    :param batch_first: If True, input shape is provided as [batch_size,seq_len,feature_dim],
    if False, input shape is provided as [seq_len,batch_size,feature_dim],default True
    :param use_bias: If False, then the layer does not use bias weights b_ih and b_hh. Default: True.
    :param bidirectional: If True, becomes a bidirectional GRU. Default: False.
    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".

    :return: a GRU class

    Example::
        
        from pyvqnet.nn import GRU
        from pyvqnet.tensor import tensor

        rnn2 = GRU(4, 6, 2, batch_first=False, bidirectional = True)

        input = tensor.ones([5, 3, 4])
        h0 = tensor.ones([4, 3, 6])

        output,hn = rnn2(input, h0)

        '''
    def __init__(self, input_size: int, hidden_size: int, num_layers: int = 1, batch_first: bool = True, use_bias: bool = True, bidirectional: bool = False, dtype: int | None = None, name: str = '') -> None: ...
    def __setattr__(self, attr, value) -> None: ...
    def forward(self, x, init_states): ...
