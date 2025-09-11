from . import signal_handling as signal_handling
from .data import Dataset as Dataset
from .utils import ExceptionWrapper as ExceptionWrapper, HAS_NUMPY as HAS_NUMPY, MP_STATUS_CHECK_INTERVAL as MP_STATUS_CHECK_INTERVAL
from _typeshed import Incomplete
from dataclasses import dataclass
from pyvqnet.utils import set_random_seed as set_random_seed

class ManagerWatchdog:
    manager_pid: Incomplete
    manager_dead: bool
    def __init__(self) -> None: ...
    def is_alive(self): ...

class WorkerInfo:
    id: int
    num_workers: int
    seed: int
    dataset: Dataset
    def __init__(self, **kwargs) -> None: ...
    def __setattr__(self, key, val): ...

def get_worker_info() -> WorkerInfo | None:
    """Returns the information about the current
    :class:`~torch.utils.data.DataLoader` iterator worker process.

    When called in a worker, this returns an object guaranteed to have the
    following attributes:

    * :attr:`id`: the current worker id.
    * :attr:`num_workers`: the total number of workers.
    * :attr:`seed`: the random seed set for the current worker. This value is
      determined by main process RNG and the worker id. See
      :class:`~torch.utils.data.DataLoader`'s documentation for more details.
    * :attr:`dataset`: the copy of the dataset object in **this** process. Note
      that this will be a different object in a different process than the one
      in the main process.

    When called in the main process, this returns ``None``.

    .. note::
       When used in a :attr:`worker_init_fn` passed over to
       :class:`~torch.utils.data.DataLoader`, this method can be useful to
       set up each worker process differently, for instance, using ``worker_id``
       to configure the ``dataset`` object to only read a specific fraction of a
       sharded dataset, or use ``seed`` to seed other libraries used in dataset
       code.
    """

@dataclass(frozen=True)
class _IterableDatasetStopIteration:
    worker_id: int
    def __init__(self, worker_id) -> None: ...

@dataclass(frozen=True)
class _ResumeIteration:
    seed: int | None = ...
    def __init__(self, seed=...) -> None: ...
