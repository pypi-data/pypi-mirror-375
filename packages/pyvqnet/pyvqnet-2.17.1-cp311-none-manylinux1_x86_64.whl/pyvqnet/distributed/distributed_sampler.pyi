from _typeshed import Incomplete
from pyvqnet.data import Sampler as Sampler

class DistributedSampler(Sampler):
    """Sampler that restricts data loading to a subset of the dataset.

    :param dataset: The dataset used for sampling.
    :param num_replicas: (int, optional) The number of processes participating in distributed training.
     If not provided, the :attr:`world_size` is retrieved from the current distributed group.
    :param rank: (int, optional) The rank of the current process within :attr:`num_replicas`. 
    If not provided, the :attr:`rank` is retrieved from the current distributed group.
    :param shuffle: (bool, optional) Whether to shuffle the indices. Defaults to ``True``.
    :param seed: (int, optional) The random seed used to shuffle the sampler if :attr:`shuffle=True`. 
    This seed should be identical across all processes in the distributed group. Defaults to ``0``.
    :param drop_last: (bool, optional) If ``True``, the sampler will drop the tail of the data to make it
     evenly divisible across the number of replicas. If ``False``, the sampler will add extra indices to make the data evenly divisible across the replicas. Defaults to ``False``.
    """
    dataset: Incomplete
    num_replicas: Incomplete
    rank: Incomplete
    epoch: int
    drop_last: Incomplete
    num_samples: Incomplete
    total_size: Incomplete
    shuffle: Incomplete
    seed: Incomplete
    def __init__(self, dataset, num_replicas: int | None = None, rank: int | None = None, shuffle: bool = True, seed: int = 0, drop_last: bool = False) -> None: ...
    def __iter__(self): ...
    def __len__(self) -> int: ...
    def set_epoch(self, epoch: int) -> None:
        """
        Sets the epoch for this sampler. When :attr:`shuffle=True`, this ensures all replicas
        use a different random ordering for each epoch. Otherwise, the next iteration of this
        sampler will yield the same ordering.

        :param epoch (int): Epoch number.
        """
