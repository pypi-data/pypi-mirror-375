import numpy as np
from ..qnn.pq3 import AngleEmbeddingCircuit as AngleEmbeddingCircuit, BasicEntanglerTemplate as BasicEntanglerTemplate, IQPEmbeddingCircuits as IQPEmbeddingCircuits, StronglyEntanglingTemplate as StronglyEntanglingTemplate
from _typeshed import Incomplete
from typing import Callable, Iterable

url_base: str
key_file: Incomplete
RX_ANGLE_ENCODING: str
RY_ANGLE_ENCODING: str
RZ_ANGLE_ENCODING: str
AMPLITUDE_ENCODING: str
StronglyEntanglingEncoding: str
RX_BasicEntanglerEncoding: str
RY_BasicEntanglerEncoding: str
RZ_BasicEntanglerEncoding: str
IQP_ENCODING: str

def data_generator(inputs: np.ndarray | list, labels: np.ndarray | list, batch_size: int = 32, shuffle: bool = True, dtype: np.dtype = ..., ldtype: np.dtype = ...):
    """
    Yields batch inputs and batch targets. Inputs and labels must have the same first dimension!

    :param inputs: `np.ndarray or python list` - inputs to the neural network
    :param labels: `np.ndarray or python list` - targets
    :param batch_size: `int` - batch size , defaults to 32
    :param shuffle: `bool` - if shuffle the data,l defaults to True
    :param dtype:  data type for data, default to np.float32.
    :param ldtype:  data type for label, default to np.int64.
    """

class Dataset:
    """An abstract class representing a :class:`Dataset`.

    All datasets that represent a map from keys to data samples should subclass
    it. All subclasses should overwrite :meth:`__getitem__`, supporting fetching a
    data sample for a given key. Subclasses could also optionally overwrite
    :meth:`__len__`, which is expected to return the size of the dataset by many
    :class:`~pyvqnet.data.Sampler` implementations and the default options
    of :class:`~pyvqnet.data.DataLoader`.

    """
    def __getitem__(self, index) -> None: ...

class CIFAR10_Dataset(Dataset):
    base_folder: str
    url: str
    filename: str
    tgz_md5: str
    train_list: Incomplete
    test_list: Incomplete
    meta: Incomplete
    root: Incomplete
    train: bool
    data: Incomplete
    labels: Incomplete
    transform: Incomplete
    def __init__(self, root: str = './cifar10-data', mode: str = 'train', transform: Callable | None = None, layout: str = 'CHW') -> None:
        '''Loading Cifar10 dataset for training or evaluation.

        :param root: File save directory. Default: "./cifar10-data".
        :param mode: Loading `train` or `test` data. Default: `train`.
        :param transform: Transform function. Default:None.
        :param layout: Loading data in different layout, default:"CHW". `layout` should be `CHW` for [b,c,h,w] or `HWC` for [b,h,w,c].

        :return:
                Dataset.
        
        Example::
            import pyvqnet

            transform = pyvqnet.data.TransformCompose([
            pyvqnet.data.TransformResize(256),
            pyvqnet.data.TransformCenterCrop(224),
            pyvqnet.data.TransformToTensor(),
            pyvqnet.data.TransformNormalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

            trainset = pyvqnet.data.CIFAR10_Dataset(root=dl_path,
                                                    mode="train",
                                                    transform=transform,layout="HWC")
        
        '''
    def __getitem__(self, index: int):
        """
        Args:
            index (int): Index

        Returns:
            tuple: (image, target) where target is index of the target class.
        """
    def __len__(self) -> int: ...
    def download(self) -> None: ...
    def extra_repr(self) -> str: ...

class IterableDataset(Dataset):
    """An iterable Dataset.

    All datasets that represent an iterable of data samples should subclass it.
    Such form of datasets is particularly useful when data come from a stream.

    All subclasses should overwrite :meth:`__iter__`, which would return an
    iterator of samples in this dataset.

    """
    def __iter__(self): ...
    def __add__(self, other: Dataset): ...

class ChainDataset(IterableDataset):
    """Dataset for chaining multiple :class:`IterableDataset` s.

    This class is useful to assemble different existing dataset streams. The
    chaining operation is done on-the-fly, so concatenating large-scale
    datasets with this class will be efficient.

    Args:
        datasets (iterable of IterableDataset): datasets to be chained together
    """
    datasets: Incomplete
    def __init__(self, datasets: Iterable[Dataset]) -> None: ...
    def __iter__(self): ...
    def __len__(self) -> int: ...

USER_AGENT: str

def download_url(url: str, root: str, filename=None, md5=None, max_redirect_hops: int = 3): ...
def download_and_extract_archive(url, download_root, extract_root=None, filename=None, md5=None, remove_finished: bool = False): ...
def calculate_md5(fpath: str, chunk_size: int = ...): ...
def check_md5(fpath, md5, **kwargs): ...
def check_integrity(fpath, md5=None): ...
def download_mnist(dataset_dir) -> None: ...
