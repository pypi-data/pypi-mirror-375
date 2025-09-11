from . import signal_handling as signal_handling, worker as worker
from ..utils import get_random_seed as get_random_seed
from .collate import default_collate as default_collate, default_convert as default_convert
from .data import Dataset as Dataset
from .sampler import BatchSampler as BatchSampler, RandomSampler as RandomSampler, Sampler as Sampler, SequentialSampler as SequentialSampler
from .utils import ExceptionWrapper as ExceptionWrapper, MP_STATUS_CHECK_INTERVAL as MP_STATUS_CHECK_INTERVAL
from _typeshed import Incomplete
from typing import Any, Iterable, Sequence

class _DatasetKind:
    Map: int
    Iterable: int
    @staticmethod
    def create_fetcher(kind, dataset, auto_collation, collate_fn, drop_last): ...

class _InfiniteConstantSampler(Sampler):
    """Analogous to ``itertools.repeat(None, None)``.
    Used as sampler for :class:`~pyvqnet.data.IterableDataset`.

    Args:
        data_source (Dataset): dataset to sample from
    """
    def __init__(self) -> None: ...
    def __iter__(self): ...

class DataLoader:
    dataset: Incomplete
    batch_size: Incomplete
    drop_last: Incomplete
    sampler: Incomplete
    num_workers: Incomplete
    worker_init_fn: Incomplete
    timeout: Incomplete
    multiprocessing_context: Incomplete
    batch_sampler: Incomplete
    prefetch_factor: Incomplete
    collate_fn: Incomplete
    persistent_workers: bool
    pin_memory: bool
    pin_memory_device: str
    seed: Incomplete
    def __init__(self, dataset: Dataset, batch_size: int | None = 1, shuffle: bool | None = None, sampler: Incomplete | None = None, batch_sampler: Sampler | Iterable[Sequence] | None = None, seed: int = None, num_workers: int = 0, prefetch_factor: int | None = None, collate_fn: Incomplete | None = None, drop_last: bool = False, timeout: int = 0, multiprocessing_context: Incomplete | None = None) -> None: ...
    def check_worker_number_rationality(self): ...
    def __iter__(self) -> _BaseDataLoaderIter: ...
    def __len__(self) -> int: ...

class _BaseDataLoaderIter:
    def __init__(self, loader: DataLoader) -> None: ...
    def __iter__(self) -> _BaseDataLoaderIter: ...
    def __next__(self) -> Any: ...
    def __len__(self) -> int: ...

class _SingleProcessDataLoaderIter(_BaseDataLoaderIter):
    def __init__(self, loader) -> None: ...

class _MultiProcessingDataLoaderIter(_BaseDataLoaderIter):
    """Iterates once over the DataLoader's dataset, as specified by the sampler"""
    def __init__(self, loader) -> None: ...
    def __del__(self) -> None: ...
