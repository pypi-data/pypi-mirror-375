from ..tensor import tensor as tensor
from .batch_norm import BatchNorm1d as BatchNorm1d, BatchNorm2d as BatchNorm2d
from .conv import Conv1D as Conv1D, Conv2D as Conv2D
from .linear import Identity as Identity, Linear as Linear

def fuse_module(model) -> None:
    '''Fuse a list of modules into a single module.

    Fuses only the following sequence of modules:
    conv, bn
    linear, bn
    All other sequences are left unchanged.
    For these sequences, replaces the first item in the list
    with the fused module, replacing the rest of the modules
    with identity.


    :param model: Model containing the modules to be fused

    Returns:
        model with fused modules. A new copy is created if inplace=True.

    Examples::
    
        from pyvqnet import tensor 
        from pyvqnet.nn import Linear
        from pyvqnet.nn import Module, BatchNorm1d, BatchNorm2d, Conv1D, Conv2D

        from pyvqnet.qnn.vqc import *
        from pyvqnet.optim import Adam
        from pyvqnet.nn import Module,BinaryCrossEntropy, Sigmoid
        from pyvqnet.data import data_generator
        import numpy as np
        from pyvqnet.tensor import QTensor

        from time import time
        from pyvqnet.utils import set_random_seed
        from pyvqnet.nn import fuse_module

        def get_accuary(result, label):
            result = (result > 0.5).astype(4)
            score = tensor.sums(result == label)
            return score.item()
            
        class Model(Module):
            def __init__(self):

                super(Model, self).__init__()

                self.conv1 = Conv2D(1,2,1)
                self.ban = BatchNorm2d(2)

                self.conv2 = Conv2D(2,1,1)
                self.li1 = Linear(64,1)
                self.ac = Sigmoid()
                
            def forward(self, x):
                x = self.conv1(x)
                x = self.ban(x)
                x = self.conv2(x).reshape([-1,64])
                x = self.li1(x)
                x = self.ac(x)

                return x
        X_train = np.random.randn(80, 1, 8, 8)
        y_train = np.random.choice([0,1], size=(80))
        
        model = Model().toGPU()
        optimizer = Adam(model.parameters(), lr = 0.001)
        batch_size = 20
        epoch = 80
        loss = BinaryCrossEntropy()
        print("start training..............")
        model.train()
        
        loss_history = []
        accuracy_history = []
        time2 = time()
        
        for i in range(epoch):
            count = 0
            sum_loss = 0
            accuary = 0
            t = 0
            for data, label in data_generator(X_train, y_train, batch_size, False):
                optimizer.zero_grad()
                data, label = QTensor(data,requires_grad=True).toGPU(), QTensor(label,
                                                    dtype=6,
                                                    requires_grad=False).toGPU()
                
                result = model(data)
                
                loss_b = loss(label.reshape([-1, 1]), result)
                
                loss_b.backward()
                optimizer._step()

                sum_loss += loss_b.item()
                count += batch_size
                accuary += get_accuary(result, label.reshape([-1,1]))
                t = t + 1
            
            loss_history.append(sum_loss/count)
            accuracy_history.append(accuary/count)
            print(
                f"epoch:{i}, #### loss:{sum_loss/count} #####accuray:{accuary/count}"
            )
        print(f"run time {time() - time2}")
        
        
        model.eval()

        input = tensor.randn((20, 1, 8, 8)).toGPU()
        print(list(model.named_children()))
        time_a = time()
        a = model(input)
        print(f"fuse before {time() - time_a}")
        fuse_module(model)
        model.toGPU()
        print(list(model.named_children()))
        time_b = time()
        b = model(input)
        print(f"fuse after {time() - time_b}")
        
        print(tensor.max(tensor.abs(a - b)).item())

    '''
