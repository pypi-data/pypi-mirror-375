from _typeshed import Incomplete
from pyvqnet.nn.module import Module
from pyvqnet.tensor import QTensor, tensor

__all__ = ['RNN', 'Dynamic_RNN']

class RNN(Module):
    '''
    Applies a multi-layer simple RNN with :math:`\\tanh` or :math:`\\text{ReLU}` non-linearity to an
    input .

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

    Example::
        from pyvqnet.nn import RNN
        from pyvqnet.tensor import tensor

        rnn2 = RNN(4, 6, 2, batch_first=False, bidirectional = True)

        input = tensor.ones([5, 3, 4])
        h0 = tensor.ones([4, 3, 6])
        output, hn = rnn2(input, h0)

        '''
    backend: Incomplete
    mode: Incomplete
    input_size: Incomplete
    hidden_size: Incomplete
    concat_size: Incomplete
    batch_first: Incomplete
    num_layers: Incomplete
    use_bias: Incomplete
    num_directions: Incomplete
    def __init__(self, input_size: int, hidden_size: int, num_layers: int = 1, nonlinearity: str = 'tanh', batch_first: bool = True, use_bias: bool = True, bidirectional: bool = False, dtype: int | None = None, name: str = '') -> None: ...
    def __setattr__(self, attr, value) -> None: ...
    def forward(self, x, init_states=None) -> QTensor:
        """
        forward function for rnn.

        :param x: input.
        :param init_states: initial states data ,default:None,using zero initial states.

        :return: tuple (out, h_t),out is features (h_t) from the last layer of the rnn,
        h_t is the final hidden state for each element in the sequence,

        """

class Dynamic_RNN(RNN):
    '''
    Applies a multi-layer dynamic sequence legnth input RNN with :math:`\\tanh` or :math:`\\text{ReLU}` non-linearity to an
    input .

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

    Example::

        from pyvqnet.nn import Dynamic_RNN
        from pyvqnet.tensor import tensor
        seq_len = [4,1,2]
        input_size = 4
        batch_size =3
        hidden_size = 2
        ml = 2
        rnn2 = Dynamic_RNN(input_size,
                        hidden_size=2,
                        num_layers=2,
                        batch_first=False,
                        bidirectional=True,
                        nonlinearity=\'relu\')

        a = tensor.arange(1, seq_len[0] * input_size + 1).reshape(
            [seq_len[0], input_size])
        b = tensor.arange(1, seq_len[1] * input_size + 1).reshape(
            [seq_len[1], input_size])
        c = tensor.arange(1, seq_len[2] * input_size + 1).reshape(
            [seq_len[2], input_size])

        y = tensor.pad_sequence([a, b, c], False)

        input = tensor.pack_pad_sequence(y,
                                        seq_len,
                                        batch_first=False,
                                        enforce_sorted=False)

        h0 = tensor.ones([ml * 2, batch_size, hidden_size])

        output, hn = rnn2(input, h0)

        seq_unpacked, lens_unpacked = \\\n        tensor.pad_packed_sequence(output, batch_first=False)
        print(seq_unpacked)
        print(lens_unpacked)

        # [
        # [[1.2980951, 0.0000000, 0.0000000, 0.0000000],
        #  [1.5040692, 0.0000000, 0.0000000, 0.0000000],
        #  [1.4927036, 0.0000000, 0.0000000, 0.1065927]],
        # [[2.6561704, 0.0000000, 0.0000000, 0.2532321],
        #  [0.0000000, 0.0000000, 0.0000000, 0.0000000],
        #  [3.1472805, 0.0000000, 0.0000000, 0.0000000]],
        # [[5.1231661, 0.0000000, 0.0000000, 0.7596353],
        #  [0.0000000, 0.0000000, 0.0000000, 0.0000000],
        #  [0.0000000, 0.0000000, 0.0000000, 0.0000000]],
        # [[8.4954977, 0.0000000, 0.0000000, 0.8191229],
        #  [0.0000000, 0.0000000, 0.0000000, 0.0000000],
        #  [0.0000000, 0.0000000, 0.0000000, 0.0000000]]
        # ]
        # [4 1 2]

        '''
    def __init__(self, input_size: int, hidden_size: int, num_layers: int = 1, nonlinearity: str = 'tanh', batch_first: bool = True, use_bias: bool = True, bidirectional: bool = False, dtype: int | None = None, name: str = '') -> None: ...
    def __setattr__(self, attr, value) -> None: ...
    def __call__(self, x, *args, **kwargs): ...
    def forward(self, x: tensor.PackedSequence, init_states=None) -> tuple[tensor.PackedSequence, QTensor]:
        """
        forward function for dynamic rnn.

        :param x: input.
        :param init_states: initial states data ,default:None,using zero initial states.

        :return: tuple (out, h_t),out is features (h_t) from the last layer of the dynamic rnn,
        h_t is the final hidden state for each element in the sequence,

        """
