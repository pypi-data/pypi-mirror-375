from ...device import DEV_CPU as DEV_CPU, DEV_GPU_1 as DEV_GPU_1
from ..pq3.template import RandomTemplate as RandomTemplate
from _typeshed import Incomplete
from pyvqnet.nn.module import Module as Module, Parameter as Parameter
from pyvqnet.qnn.pq3 import expval as expval
from pyvqnet.qnn.qcnn.functions_conv import im2col_array as im2col_array
from pyvqnet.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor, tensor as tensor
from pyvqnet.utils.initializer import normal as normal, quantum_uniform as quantum_uniform

CoreTensor: Incomplete

class Quanvolution(Module):
    '''
        An implementation of qunatum convolution based on 
        `Quanvolutional Neural Networks: Powering Image Recognition with Quantum Circuits <https://arxiv.org/abs/1904.04767>`_ ,
        Replace the classical convolution filters with variational quantum circuits and
        we get quanvolutional neural networks with quanvolutional filters.
        
        In this Module, the input with shape[Batchsize,1,h,w] is splited into 2*2 patch with different `strides`.
        The patch is then encoded into 4 qubits with RY gates, a RandomTemplate with trainable parameters of shape [L,K] is used to 
        construct the quantum variational circuit. 
        At last , several PauliZ expectations are calculated on 4 qubits to get output.
        
        :param params_shape: shape of paramters .should be 2 dim.
        :param strides: strides of slice windows,default (1,1).
        :param kernel_initializer: kernel initializer of parameters.
        :param machine_type: machine type string,default:"cpu".

    Examples::

        from pyvqnet.qnn.qcnn import Quanvolution
        import pyvqnet.tensor as tensor
        qlayer = Quanvolution([4,2],(3,3))

        x = tensor.arange(1,25*25*3+1).reshape([3,1,25,25])

        y = qlayer(x)

        print(y.shape)

        y.backward()

        print(qlayer.m_para)
        print(qlayer.m_para.grad)
    '''
    m_para: Incomplete
    params_shape: Incomplete
    m_machine: Incomplete
    m_qubits: Incomplete
    m_cubits: Incomplete
    history_expectation: Incomplete
    delta: float
    m_prog_func: Incomplete
    def __init__(self, params_shape, strides=(1, 1), kernel_initializer=..., machine_type: str = 'cpu') -> None: ...
    def forward(self, x): ...

class QConv(Module):
    '''
    Quantum Convolution module. Replace Conv2D kernal with quantum circuits.
    Inputs to the conv module are of shape (batch_size, input_channels, height, width)
    reference `Samuel et al. (2020) <https://arxiv.org/abs/2012.12177>`_.

    :param input_channels: `int` - Number of input channels
    :param output_channels: `int` - Number of kernels
    :param quantum_number: `int` - Size of a single kernel.
     Each quantum number is kernel_size x kernel_size
    :param stride: `tuple` - Stride, defaults to (1, 1)
    :param padding: `tuple` - Padding, defaults to (0, 0)
    :param kernel_initializer: `callable` - Defaults to normal
    :param machine: `str` - machinecpu simulation

    :param dtype: data type of parameters,default: None,use default data type.
    :param name: name of module,default:"".
    :return: a quantum cnn class

    Example::

        x = tensor.ones([1,3,12,12])
        layer = QConv(input_channels=3, output_channels=2, quantum_number=4, stride=(2, 2))
        y = layer(x)

    '''
    name: Incomplete
    backend: Incomplete
    stride: Incomplete
    weights: Incomplete
    machine: Incomplete
    qlist: Incomplete
    def __init__(self, input_channels, output_channels, quantum_number, stride=(1, 1), padding=(0, 0), kernel_initializer=..., machine: str = 'cpu', dtype: int | None = None, name: str = '') -> None: ...
    def forward(self, x: tensor.QTensor): ...

def encode_cir(qlist, pixels): ...
def entangle_cir(qlist): ...
def param_cir(qlist, params): ...
def qcnn_circuit(pixels, params, machine, qlist):
    """
    qcnn_circuit
    """
