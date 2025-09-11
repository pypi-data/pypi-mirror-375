from ..distributed_sampler import DistributedSampler as DistributedSampler
from _typeshed import Incomplete
from pyvqnet.data import DataLoader as DataLoader, RandomSampler as RandomSampler, Sampler as Sampler
from pyvqnet.device import get_gpu_max_count as get_gpu_max_count

class VQNetDeepSpeedDataLoader:
    deepspeed_dataloader_config: Incomplete
    tput_timer: Incomplete
    batch_size: Incomplete
    curriculum_learning_enabled: bool
    num_local_io_workers: Incomplete
    data_sampler: Incomplete
    dataset: Incomplete
    collate_fn: Incomplete
    device_count: Incomplete
    pin_memory: Incomplete
    data: Incomplete
    dataloader_drop_last: Incomplete
    post_process_func: Incomplete
    len: Incomplete
    def __init__(self, dataset, batch_size, pin_memory, local_rank, tput_timer, collate_fn=None, num_local_io_workers=None, data_sampler=None, data_parallel_world_size=None, data_parallel_rank=None, dataloader_drop_last: bool = False, deepspeed_dataloader_config={}) -> None: ...
    def __iter__(self): ...
    def __len__(self) -> int: ...
    def __next__(self): ...
