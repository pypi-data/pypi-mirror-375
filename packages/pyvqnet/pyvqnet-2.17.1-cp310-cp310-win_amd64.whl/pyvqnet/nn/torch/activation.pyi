from ...tensor import to_tensor as to_tensor
from ..parameter import Parameter as Parameter
from .module import TorchModule as TorchModule
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock

class Gelu(TorchModule):
    name: Incomplete
    def __init__(self, approximate: str = 'tanh', name: str = '') -> None:
        '''
        Initializes the GELU (Gaussian Error Linear Unit) activation function module.
        
        :param approximate: str, optional. Specifies the approximation method for GELU. 
                            Default is "tanh". Options: "tanh" or "none".
        :param name: str, optional. Name of the module. Default is an empty string.
        '''
    def forward(self, x):
        """
        Forward pass method to compute the GELU activation using torch.
        
        :param x: Tensor. Input tensor to apply the GELU activation.
        :return: Tensor. Output tensor after applying the GELU activation using torch.
        """
GeLU = Gelu

class SiLU(TorchModule):
    name: Incomplete
    def __init__(self, name: str = '') -> None:
        """
        Initializes the SiLU (Sigmoid Linear Unit) activation function module.
        
        :param name: str, optional. Name of the module. Default is an empty string.
        """
    def forward(self, x):
        """
        Forward pass method to compute the SiLU activation using torch.
        
        :param x: Tensor. Input tensor to apply the SiLU activation.
        :return: Tensor. Output tensor after applying the SiLU activation using torch.
        """

class Sigmoid(TorchModule):
    name: Incomplete
    def __init__(self, name: str = '') -> None:
        """
        Initializes the Sigmoid activation function module.
        
        :param name: str, optional. Name of the module. Default is an empty string.
        """
    def forward(self, x):
        """
        Forward pass method to compute the Sigmoid activation using torch.
        
        :param x: Tensor. Input tensor to apply the Sigmoid activation.
        :return: Tensor. Output tensor after applying the Sigmoid activation using torch.
        """

class Softsign(TorchModule):
    name: Incomplete
    def __init__(self, name: str = '') -> None:
        """
        Initializes the Softsign activation function module.
        
        :param name: str, optional. Name of the module. Default is an empty string.
        """
    def forward(self, x):
        """
        Forward pass method to compute the Softsign activation using torch.
        
        :param x: Tensor. Input tensor to apply the Softsign activation.
        :return: Tensor. Output tensor after applying the Softsign activation using torch.
        """

class Softplus(TorchModule):
    name: Incomplete
    def __init__(self, name: str = '') -> None:
        """
        Initializes the Softplus activation function module.
        
        :param name: str, optional. Name of the module. Default is an empty string.
        """
    def forward(self, x):
        """
        Forward pass method to compute the Softplus activation using torch.
        
        :param x: Tensor. Input tensor to apply the Softplus activation.
        :return: Tensor. Output tensor after applying the Softplus activation using torch.
        """

class Softmax(TorchModule):
    name: Incomplete
    axis: Incomplete
    def __init__(self, axis: int = -1, name: str = '') -> None:
        """
        Initializes the Softmax activation function module.
        
        :param axis: int, optional. Dimension along which Softmax is computed. Default is -1.
        :param name: str, optional. Name of the module. Default is an empty string.
        """
    def forward(self, x):
        """
        Forward pass method to compute the Softmax activation using torch.
        
        :param x: Tensor. Input tensor to apply the Softmax activation.
        :return: Tensor. Output tensor after applying the Softmax activation using torch.
        """

class HardSigmoid(TorchModule):
    name: Incomplete
    def __init__(self, name: str = '') -> None:
        """
        Initializes the HardSigmoid activation function module.
        
        :param name: str, optional. Name of the module. Default is an empty string.
        """
    def forward(self, x):
        """
        Forward pass method to compute the HardSigmoid activation using torch.
        
        :param x: Tensor. Input tensor to apply the HardSigmoid activation.
        :return: Tensor. Output tensor after applying the HardSigmoid activation using torch.
        """

class ReLu(TorchModule):
    name: Incomplete
    def __init__(self, name: str = '') -> None:
        """
        Initializes the ReLU (Rectified Linear Unit) activation function module.
        
        :param name: str, optional. Name of the module. Default is an empty string.
        """
    def forward(self, x):
        """
        Forward pass method to compute the ReLU activation using torch.
        
        :param x: Tensor. Input tensor to apply the ReLU activation.
        :return: Tensor. Output tensor after applying the ReLU activation using torch.
        """
ReLU = ReLu

class LeakyReLu(TorchModule):
    name: Incomplete
    alpha: Incomplete
    def __init__(self, alpha: float = 0.01, name: str = '') -> None:
        """
        Initializes the LeakyReLU activation function module.
        
        :param alpha: float, optional. Negative slope coefficient. Default is 0.01.
        :param name: str, optional. Name of the module. Default is an empty string.
        """
    def forward(self, x):
        """
        Forward pass method to compute the LeakyReLU activation using torch.
        
        :param x: Tensor. Input tensor to apply the LeakyReLU activation.
        :return: Tensor. Output tensor after applying the LeakyReLU activation using torch.
        """

class ELU(TorchModule):
    name: Incomplete
    alpha: Incomplete
    def __init__(self, alpha: float = 1.0, name: str = '') -> None:
        """
        Initializes the ELU (Exponential Linear Unit) activation function module.
        
        :param alpha: float, optional. Scale factor for negative inputs. Default is 1.0.
        :param name: str, optional. Name of the module. Default is an empty string.
        """
    def forward(self, x):
        """
        Forward pass method to compute the ELU activation using torch.
        
        :param x: Tensor. Input tensor to apply the ELU activation.
        :return: Tensor. Output tensor after applying the ELU activation using torch.
        """

class Tanh(TorchModule):
    name: Incomplete
    def __init__(self, name: str = '') -> None:
        """
        Initializes the Tanh activation function module.
        
        :param name: str, optional. Name of the module. Default is an empty string.
        """
    def forward(self, x):
        """
        Forward pass method to compute the Tanh activation using torch.
        
        :param x: Tensor. Input tensor to apply the Tanh activation.
        :return: Tensor. Output tensor after applying the Tanh activation using torch.
        """
