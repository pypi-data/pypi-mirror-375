from .ControlComm import get_rank as get_rank, get_size as get_size

def split_data(x_train, y_train, shuffle: bool = False):
    """
    Split the dataset process based on the process number, and train based on the split data on different processes.

    :param: x_train: `np.array` - train datas.
    :param: y_train: `np.array` -  train labels.
    :param: shuffle: `bool` - if shuffle the data,l defaults to True

    Example::
        from pyvqnet.distributed import split_data
        import numpy as np

        x_train = np.random.randint(255, size = (100, 5))
        y_train = np.random.randint(2, size = (100, 1))

        x_train, y_train= split_data(x_train, y_train)

    """
