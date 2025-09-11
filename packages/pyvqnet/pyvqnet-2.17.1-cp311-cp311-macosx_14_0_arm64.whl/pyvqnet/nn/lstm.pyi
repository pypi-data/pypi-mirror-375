from _typeshed import Incomplete
from pyvqnet.nn.module import Module
from pyvqnet.tensor import PackedSequence, QTensor

__all__ = ['LSTM', 'Dynamic_LSTM']

class LSTM(Module):
    '''
    Long-Short Term Memory (LSTM) network cell.

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

    Example::
        from pyvqnet.nn import LSTM
        from pyvqnet.tensor import tensor

        rnn2 = LSTM(4, 6, 2, batch_first=False, bidirectional = True)
        input = tensor.ones([5, 3, 4])
        h0 = tensor.ones([4, 3, 6])
        c0 = tensor.ones([4, 3, 6])
        output, (hn, cn) = rnn2(input, (h0, c0))

        '''
    backend: Incomplete
    input_size: Incomplete
    hidden_size: Incomplete
    concat_size: Incomplete
    batch_first: Incomplete
    num_layers: Incomplete
    use_bias: Incomplete
    num_directions: Incomplete
    def __init__(self, input_size, hidden_size, num_layers: int = 1, batch_first: bool = True, use_bias: bool = True, bidirectional: bool = False, dtype: int | None = None, name: str = '') -> None: ...
    def __setattr__(self, attr, value) -> None: ...
    def forward(self, x, init_states=None):
        """
        forward function for lstm.

        :param x: input.
        :param init_states: initial states data ,default:None,using zero initial states.

        :return: tuple (out, (h_t, c_t)),out is features (h_t) from the last layer of the LSTM,
        h_t is the final hidden state for each element in the sequence,
        c_t is the final cell state for each element in the sequence.
        """

class Dynamic_LSTM(LSTM):
    '''
    Applies a multi-layer dynamic sequence legnth input LSTM(Long Short Term Memory) Module.

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

    Example::

        from pyvqnet.nn import Dynamic_LSTM
        from pyvqnet.tensor import tensor

        input_size = 2
        hidden_size = 2
        ml = 2
        seq_len = [3, 4, 1]
        batch_size = 3
        rnn2 = Dynamic_LSTM(input_size,
                            hidden_size=hidden_size,
                            num_layers=ml,
                            batch_first=False,
                            bidirectional=True)

        a = tensor.arange(1, seq_len[0] * input_size + 1).reshape(
            [seq_len[0], input_size])
        b = tensor.arange(1, seq_len[1] * input_size + 1).reshape(
            [seq_len[1], input_size])
        c = tensor.arange(1, seq_len[2] * input_size + 1).reshape(
            [seq_len[2], input_size])
        a.requires_grad = True
        b.requires_grad = True
        c.requires_grad = True
        y = tensor.pad_sequence([a, b, c], False)

        input = tensor.pack_pad_sequence(y,
                                        seq_len,
                                        batch_first=False,
                                        enforce_sorted=False)

        h0 = tensor.ones([ml * 2, batch_size, hidden_size])
        c0 = tensor.ones([ml * 2, batch_size, hidden_size])

        output, (hn, cn) = rnn2(input, (h0, c0))

        seq_unpacked, lens_unpacked =         tensor.pad_packed_sequence(output, batch_first=False)

        '''
    def __init__(self, input_size: int, hidden_size: int, num_layers: int = 1, batch_first: bool = True, use_bias: bool = True, bidirectional: bool = False, dtype: int | None = None, name: str = '') -> None: ...
    def __setattr__(self, attr, value) -> None: ...
    def __call__(self, x, *args, **kwargs): ...
    def forward(self, x: PackedSequence, init_states=None) -> tuple[PackedSequence, tuple[QTensor, QTensor]]:
        """
        forward function for dynamic lstm.

        :param x: input.
        :param init_states: initial states data ,default:None,using zero initial states.

        :return: tuple (out, (h_t, c_t)),out is features (h_t) from the last layer of the LSTM,
        h_t is the final hidden state for each element in the sequence,
        c_t is the final cell state for each element in the sequence.
        """
