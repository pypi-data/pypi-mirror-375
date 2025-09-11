from pyvqnet.distributed import *
import pyvqnet
from ...tensor import QTensor as QTensor
from _typeshed import Incomplete
from pyvqnet.device import DEV_CPU as DEV_CPU
from pyvqnet.distributed import CommController as CommController
from pyvqnet.nn.parameter import Parameter as Parameter
from pyvqnet.tensor import AutoGradNode as AutoGradNode
from pyvqnet.utils.initializer import zeros as zeros
from typing import Callable

def ensure_divisibility(numerator, denominator) -> None:
    """Ensure that numerator is divisible by the denominator."""
def divide(numerator, denominator):
    """Ensure that numerator is divisible by the denominator and return
    the division value."""

class ColumnParallelLinear(pyvqnet.nn.Module):
    '''Linear layer with column parallelism.

    The linear layer is defined as Y = XA + b. A is parallelized along
    its second dimension as A = [A_1, ..., A_p].

    Args:
        :param input_size: first dimension of matrix A.
        :param output_size: second dimension of matrix A.
        :param weight_initializer: `callable` - defaults to normal.
        :param bias_initializer: `callable` - defaults to zeros.
        :param use_bias: `bool` - defaults to True.
        :param dtype: default: None,use default data type.
        :param name: name of module,default:"".
        :param tp_comm: Comm Controller.
        
    Example::
    
        import pyvqnet.distributed
        import pyvqnet.optim as optim
        import pyvqnet.nn as nn
        import pyvqnet
        import sys
        from pyvqnet.distributed.tensor_parallel import ColumnParallelLinear, RowParallelLinear
        from pyvqnet.distributed import *
        from time import time

        import pyvqnet
        import numpy as np
        import os
        from pyvqnet import *
        import pytest

        Comm_OP = CommController("nccl")

        import struct
        def load_mnist(dataset="training_data",
                    digits=np.arange(2),
                    path="./"):
            from array import array as pyarray
            # download_mnist(path)
            if dataset == "training_data":
                fname_image = os.path.join(path, "train-images-idx3-ubyte").replace(
                    "\\", "/")
                fname_label = os.path.join(path, "train-labels-idx1-ubyte").replace(
                    "\\", "/")
            elif dataset == "testing_data":
                fname_image = os.path.join(path, "t10k-images-idx3-ubyte").replace(
                    "\\", "/")
                fname_label = os.path.join(path, "t10k-labels-idx1-ubyte").replace(
                    "\\", "/")
            else:
                raise ValueError("dataset must be \'training_data\' or \'testing_data\'")

            flbl = open(fname_label, "rb")
            _, size = struct.unpack(">II", flbl.read(8))

            lbl = pyarray("b", flbl.read())
            flbl.close()

            fimg = open(fname_image, "rb")
            _, size, rows, cols = struct.unpack(">IIII", fimg.read(16))
            img = pyarray("B", fimg.read())
            fimg.close()

            ind = [k for k in range(size) if lbl[k] in digits]
            num = len(ind)
            images = np.zeros((num, rows, cols),dtype=np.float32)

            labels = np.zeros((num, 1), dtype=int)
            for i in range(len(ind)):
                images[i] = np.array(img[ind[i] * rows * cols:(ind[i] + 1) * rows *
                                        cols]).reshape((rows, cols))
                labels[i] = lbl[ind[i]]

            return images, labels

        train_images_np, train_labels_np = load_mnist(dataset="training_data", digits=np.arange(10),path="./data/MNIST/raw/")
        train_images_np = train_images_np / 255.

        test_images_np, test_labels_np = load_mnist(dataset="testing_data", digits=np.arange(10),path="./data/MNIST/raw/")
        test_images_np = test_images_np / 255.

        local_rank = pyvqnet.distributed.get_rank()

        class MNISTClassifier(nn.Module):
            def __init__(self):
                super(MNISTClassifier, self).__init__()
                self.fc1 = RowParallelLinear(28*28, 512, tp_comm = Comm_OP)
                self.fc2 = ColumnParallelLinear(512, 256, tp_comm = Comm_OP)
                self.fc3 = RowParallelLinear(256, 128, tp_comm = Comm_OP)
                self.fc4 = ColumnParallelLinear(128, 64, tp_comm = Comm_OP)
                self.fc5 = RowParallelLinear(64, 10, tp_comm = Comm_OP)
                self.ac = nn.activation.ReLu()

            def forward(self, x:pyvqnet.tensor.QTensor):

                x = x.reshape([-1, 28*28])
                x = self.ac(self.fc1(x))
                x = self.fc2(x)
                x = self.fc3(x)
                x = self.fc4(x)
                x = self.fc5(x)
                return x


        model = MNISTClassifier()
        total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

        model.to(local_rank + 1000)

        Comm_OP.broadcast_model_params(model, 0)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        def compute_acc(outputs, labels, correct, total):
            predicted = pyvqnet.tensor.argmax(outputs, dim=1, keepdims=True)
            total += labels.size
            correct += pyvqnet.tensor.sums(predicted == labels).item()
            return correct, total

        train_acc = 0
        test_acc = 0
        epochs = 5
        loss = 0

        time1 = time()
        for epoch in range(epochs):
            model.train()
            total = 0
            correct = 0
            step = 0

            batch_size = 64
            num_batches = (train_images_np.shape[0] + batch_size - 1) // batch_size

            for i in range(num_batches):
                data_ = tensor.QTensor(train_images_np[i*batch_size: (i+1) * batch_size,:], dtype = kfloat32)
                labels = tensor.QTensor(train_labels_np[i*batch_size: (i+1) * batch_size,:], dtype = kint64)

                data_ = data_.to(local_rank + 1000)
                labels = labels.to(local_rank + 1000)

                optimizer.zero_grad()

                outputs = model(data_)
                loss = criterion(labels, outputs)

                loss.backward()
                optimizer.step()

                correct, total = compute_acc(outputs, labels, correct, total)
                step += 1
                if step % 50 == 0:
                    print(f"Train : rank {get_rank()} Epoch [{epoch+1}/{epochs}], step {step} Loss: {loss.item():.4f} acc {100 * correct / total}")
                    sys.stdout.flush()

            train_acc = 100 * correct / total
        time2 = time()

        print(f\'Accuracy of the model on the 10000 Train images: {train_acc}% time cost {time2 - time1}\')
        
    '''
    input_size: Incomplete
    output_size: Incomplete
    weight_initializer: Incomplete
    use_bias: Incomplete
    tp_comm: Incomplete
    gather_output: Incomplete
    output_size_per_partition: Incomplete
    weights: Incomplete
    bias: Incomplete
    def __init__(self, input_size, output_size, weight_initializer: Callable | None = None, bias_initializer: Callable | None = None, use_bias: bool = True, dtype: int | None = None, name: str = '', tp_comm: CommController = None) -> None: ...
    def forward(self, input: pyvqnet.tensor.QTensor):
        """Forward of ColumnParallelLinear

        Args:
            input: 2D tensor whose order of dimension is [batch, hidden]

        Returns:
            - output

        """

class RowParallelLinear(pyvqnet.nn.Module):
    '''Linear layer with Row parallelism.

    The linear layer is defined as Y = XA + b. A is parallelized along its first dimension and X along its second dimension.
    A = transpose([A_1 .. A_p]) X = [X_1, ..., X_p].

    Args:
        :param input_size: first dimension of matrix A.
        :param output_size: second dimension of matrix A.
        :param weight_initializer: `callable` - defaults to normal.
        :param bias_initializer: `callable` - defaults to zeros.
        :param use_bias: `bool` - defaults to True.
        :param dtype: default: None,use default data type.
        :param name: name of module,default:"".
        :param tp_comm: Comm Controller.

    Example::
    
        import pyvqnet.distributed
        import pyvqnet.optim as optim
        import pyvqnet.nn as nn
        import pyvqnet
        import sys
        from pyvqnet.distributed.tensor_parallel import ColumnParallelLinear, RowParallelLinear
        from pyvqnet.distributed import *
        from time import time

        import pyvqnet
        import numpy as np
        import os
        from pyvqnet import *
        import pytest

        Comm_OP = CommController("nccl")

        import struct
        def load_mnist(dataset="training_data",
                    digits=np.arange(2),
                    path="./"):
            from array import array as pyarray
            # download_mnist(path)
            if dataset == "training_data":
                fname_image = os.path.join(path, "train-images-idx3-ubyte").replace(
                    "\\", "/")
                fname_label = os.path.join(path, "train-labels-idx1-ubyte").replace(
                    "\\", "/")
            elif dataset == "testing_data":
                fname_image = os.path.join(path, "t10k-images-idx3-ubyte").replace(
                    "\\", "/")
                fname_label = os.path.join(path, "t10k-labels-idx1-ubyte").replace(
                    "\\", "/")
            else:
                raise ValueError("dataset must be \'training_data\' or \'testing_data\'")

            flbl = open(fname_label, "rb")
            _, size = struct.unpack(">II", flbl.read(8))

            lbl = pyarray("b", flbl.read())
            flbl.close()

            fimg = open(fname_image, "rb")
            _, size, rows, cols = struct.unpack(">IIII", fimg.read(16))
            img = pyarray("B", fimg.read())
            fimg.close()

            ind = [k for k in range(size) if lbl[k] in digits]
            num = len(ind)
            images = np.zeros((num, rows, cols),dtype=np.float32)

            labels = np.zeros((num, 1), dtype=int)
            for i in range(len(ind)):
                images[i] = np.array(img[ind[i] * rows * cols:(ind[i] + 1) * rows *
                                        cols]).reshape((rows, cols))
                labels[i] = lbl[ind[i]]

            return images, labels

        train_images_np, train_labels_np = load_mnist(dataset="training_data", digits=np.arange(10),path="./data/MNIST/raw/")
        train_images_np = train_images_np / 255.

        test_images_np, test_labels_np = load_mnist(dataset="testing_data", digits=np.arange(10),path="./data/MNIST/raw/")
        test_images_np = test_images_np / 255.

        local_rank = pyvqnet.distributed.get_rank()

        class MNISTClassifier(nn.Module):
            def __init__(self):
                super(MNISTClassifier, self).__init__()
                self.fc1 = RowParallelLinear(28*28, 512, tp_comm = Comm_OP)
                self.fc2 = ColumnParallelLinear(512, 256, tp_comm = Comm_OP)
                self.fc3 = RowParallelLinear(256, 128, tp_comm = Comm_OP)
                self.fc4 = ColumnParallelLinear(128, 64, tp_comm = Comm_OP)
                self.fc5 = RowParallelLinear(64, 10, tp_comm = Comm_OP)
                self.ac = nn.activation.ReLu()

            def forward(self, x:pyvqnet.tensor.QTensor):

                x = x.reshape([-1, 28*28])
                x = self.ac(self.fc1(x))
                x = self.fc2(x)
                x = self.fc3(x)
                x = self.fc4(x)
                x = self.fc5(x)
                return x


        model = MNISTClassifier()
        total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

        model.to(local_rank + 1000)

        Comm_OP.broadcast_model_params(model, 0)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)

        def compute_acc(outputs, labels, correct, total):
            predicted = pyvqnet.tensor.argmax(outputs, dim=1, keepdims=True)
            total += labels.size
            correct += pyvqnet.tensor.sums(predicted == labels).item()
            return correct, total

        train_acc = 0
        test_acc = 0
        epochs = 5
        loss = 0

        time1 = time()
        for epoch in range(epochs):
            model.train()
            total = 0
            correct = 0
            step = 0

            batch_size = 64
            num_batches = (train_images_np.shape[0] + batch_size - 1) // batch_size

            for i in range(num_batches):
                data_ = tensor.QTensor(train_images_np[i*batch_size: (i+1) * batch_size,:], dtype = kfloat32)
                labels = tensor.QTensor(train_labels_np[i*batch_size: (i+1) * batch_size,:], dtype = kint64)

                data_ = data_.to(local_rank + 1000)
                labels = labels.to(local_rank + 1000)

                optimizer.zero_grad()

                outputs = model(data_)
                loss = criterion(labels, outputs)

                loss.backward()
                optimizer.step()

                correct, total = compute_acc(outputs, labels, correct, total)
                step += 1
                if step % 50 == 0:
                    print(f"Train : rank {get_rank()} Epoch [{epoch+1}/{epochs}], step {step} Loss: {loss.item():.4f} acc {100 * correct / total}")
                    sys.stdout.flush()

            train_acc = 100 * correct / total
        time2 = time()

        print(f\'Accuracy of the model on the 10000 Train images: {train_acc}% time cost {time2 - time1}\')

    '''
    input_size: Incomplete
    output_size: Incomplete
    gather_output: Incomplete
    use_bias: Incomplete
    tp_comm: Incomplete
    input_size_per_partition: Incomplete
    weights: Incomplete
    bias: Incomplete
    def __init__(self, input_size, output_size, weight_initializer: Callable | None = None, bias_initializer: Callable | None = None, use_bias: bool = True, dtype: int | None = None, name: str = '', tp_comm: CommController = None) -> None: ...
    def forward(self, input_: pyvqnet.tensor.QTensor):
        """Forward of ColumnParallelLinear

        Args:
            input: 2D tensor whose order of dimension is [batch, hidden]

        Returns:
            - output

        """
