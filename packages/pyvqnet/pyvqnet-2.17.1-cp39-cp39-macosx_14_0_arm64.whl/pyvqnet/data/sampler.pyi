from _typeshed import Incomplete
from typing import Iterator, Sized

class Sampler:
    """Base class for all Samplers.

    Every Sampler subclass has to provide an :meth:`__iter__` method, providing a
    way to iterate over indices of dataset elements, and a :meth:`__len__` method
    that returns the length of the returned iterators.

    .. note:: The :meth:`__len__` method isn't strictly required by
              :class:`~pyvqnet.data.DataLoader`, but is expected in any
              calculation involving the length of a :class:`~pyvqnet.data.DataLoader`.
    """
    def __init__(self, data_source: Sized | None) -> None: ...
    def __iter__(self): ...

class SequentialSampler(Sampler):
    """Samples elements sequentially, always in the same order.

    :param data_source (Dataset): dataset to sample from.


    Example:

        from pyvqnet.data.sampler import SequentialSampler
        y6 = list(SequentialSampler(range(10)))

    """
    data_source: Sized
    def __init__(self, data_source: Sized) -> None: ...
    def __iter__(self) -> Iterator[int]: ...
    def __len__(self) -> int: ...

class RandomSampler(Sampler):
    """Samples elements randomly. If without replacement, then sample from a shuffled dataset.
    If with replacement, then user can specify :attr:`num_samples` to draw.

    :param Dataset data_source: dataset to sample from
    :param bool replacement: samples are drawn on-demand with replacement if ``True``, default=``False``
    :param int num_samples: number of samples to draw, default=`len(dataset)`.
    :param Generator generator: Generator used in sampling.

    
    Example:

        from pyvqnet.data.sampler import RandomSampler,BatchSampler,SequentialSampler
        y1 = list(BatchSampler(RandomSampler(range(10),seed=42), batch_size=3, drop_last=False))
        y2 = list(BatchSampler(SequentialSampler(range(10)), batch_size=3, drop_last=True))
        y3 = list(BatchSampler(RandomSampler(range(10),seed=42), batch_size=3, drop_last=True))
        y4 = list(BatchSampler(SequentialSampler(range(10)), batch_size=3, drop_last=False))
        y5 = list(RandomSampler(range(10),seed=42))
        y6 = list(SequentialSampler(range(10)))

    """
    data_source: Sized
    replacement: bool
    seed: Incomplete
    def __init__(self, data_source: Sized, replacement: bool = False, num_samples: int | None = None, seed: Incomplete | None = None) -> None: ...
    @property
    def num_samples(self) -> int: ...
    def __iter__(self): ...
    def __len__(self) -> int: ...

class BatchSampler(Sampler):
    """Wraps another sampler to yield a mini-batch of indices.

    :param Union[Sampler, Iterable] sampler: Base sampler. Can be any iterable object
    :param int batch_size: Size of mini-batch.
    :param bool drop_last: If ``True``, the sampler will drop the last batch if
                its size would be less than ``batch_size``

    Example:

        from pyvqnet.data.sampler import RandomSampler,BatchSampler,SequentialSampler
        y1 = list(BatchSampler(RandomSampler(range(10),seed=42), batch_size=3, drop_last=False))
        y2 = list(BatchSampler(SequentialSampler(range(10)), batch_size=3, drop_last=True))
        y3 = list(BatchSampler(RandomSampler(range(10),seed=42), batch_size=3, drop_last=True))
        y4 = list(BatchSampler(SequentialSampler(range(10)), batch_size=3, drop_last=False))

    """
    sampler: Incomplete
    batch_size: Incomplete
    drop_last: Incomplete
    def __init__(self, sampler, batch_size: int, drop_last: bool) -> None: ...
    def __iter__(self) -> Iterator[list[int]]: ...
    def __len__(self) -> int: ...
