import os
from _typeshed import Incomplete
from pyvqnet.backends import check_not_default_backend as check_not_default_backend, get_backend as get_backend
from pyvqnet.device import DEV_CPU as DEV_CPU, DEV_GPU_0 as DEV_GPU_0
from pyvqnet.tensor.tensor import QTensor as QTensor

DEFAULT_PROTOCOL: int

class _opener:
    file_like: Incomplete
    def __init__(self, file_like) -> None: ...
    def __enter__(self): ...
    def __exit__(self, *args) -> None: ...

class _open_file(_opener):
    def __init__(self, name, mode) -> None: ...
    def __exit__(self, *args) -> None: ...

class _open_buf_reader(_opener):
    def __init__(self, buffer) -> None: ...

class _open_buf_writer(_opener):
    def __exit__(self, *args) -> None: ...

def save_optim(obj, f) -> None:
    """
    save scalar and QTensor value on disk,used for optim.

    :param obj: dict from state_dict().
    :param f: save path.
    """
def load_optim(f) -> dict:
    """
    load scalar and QTensor value from disk,used for optim.

    :param f: save path.
    :return:
            state dict 
    """
def save_parameters(obj, f: str | os.PathLike) -> None:
    '''\\\n
    Saves model parmeters to a disk file.

    :param obj: saved OrderedDict from state_dict()
    :param f: a string or os.PathLike object containing a file name
    :return: None

    Example::

        class Net(Module):
            def __init__(self):
                super(Net, self).__init__()
                self.conv1 = Conv2D(input_channels=1, output_channels=6,
                                    kernel_size=(5, 5), stride=(1, 1), padding="valid")

            def forward(self, x):
                return super().forward(x)

        model = Net()
        save_parameters( model.state_dict(),"tmp.model")

    '''
def load_parameters(f: str | os.PathLike) -> dict:
    '''
    Loads model paramters from a disk file.

    The model instance should be created first.

    :param f: a string or os.PathLike object containing a file name
    :return: saved state dict for load_state_dict()

    Example::

        class Net(Module):
            def __init__(self):
                super(Net, self).__init__()
                self.conv1 = Conv2D(input_channels=1, output_channels=6,
                                    kernel_size=(5, 5), stride=(1, 1), padding="valid")

            def forward(self, x):
                return super().forward(x)

        model = Net()
        model1 = Net()  # another Module object
        save_parameters( model.state_dict(),"tmp.model")
        model_para =  load_parameters("tmp.model")
        model1.load_state_dict(model_para)
    '''
