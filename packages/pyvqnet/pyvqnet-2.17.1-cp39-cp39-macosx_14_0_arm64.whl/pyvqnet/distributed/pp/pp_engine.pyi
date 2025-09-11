import pyvqnet.nn as nn
from . import p2p as p2p, schedule as schedule
from ... import tensor as tensor
from ...device import DEV_GPU as DEV_GPU
from ...dtype import kbool as kbool, kfloat32 as kfloat32, kint64 as kint64
from ...logger import logger as logger
from ...nn import Module as Module
from ...optim import Adam as Adam, AdamW as AdamW, Optimizer as Optimizer
from ...tensor import flatten_dense_tensors as flatten_dense_tensors, unflatten_dense_tensors as unflatten_dense_tensors
from ..configs import groups as groups
from ..configs.constants import ROUTE_EVAL as ROUTE_EVAL, ROUTE_PREDICT as ROUTE_PREDICT, ROUTE_TRAIN as ROUTE_TRAIN
from ..distributed_sampler import DistributedSampler as DistributedSampler
from ..zero.base_optimizer import DummyOptim as DummyOptim
from ..zero.stage_1_and_2 import DeepSpeedZeroOptimizer as DeepSpeedZeroOptimizer
from ..zero.zero_config import ZeroStageEnum as ZeroStageEnum
from .config import ADAM_OPTIMIZER as ADAM_OPTIMIZER, DeepSpeedConfig as DeepSpeedConfig, IF_DEBUG_WITH_NO_DIST_OP as IF_DEBUG_WITH_NO_DIST_OP, ZERO_OPTIMIZATION as ZERO_OPTIMIZATION
from .dataloader import VQNetDeepSpeedDataLoader as VQNetDeepSpeedDataLoader
from .pp_module import PipelineError as PipelineError, PipelineModule as PipelineModule
from _typeshed import Incomplete
from collections import OrderedDict as OrderedDict, defaultdict as defaultdict, deque as deque
from enum import Enum as Enum
from pyvqnet.device import get_readable_device_str as get_readable_device_str
from shutil import copyfile as copyfile

MEMORY_OPT_ALLREDUCE_SIZE: int
TARGET_ID: int
LOG_STAGE: int
DATA_PARALLEL_ID: int
BATCH_INPUT_TIMER: str
TRAIN_BATCH_TIMER: str
PIPE_SEND_OUTPUT_TIMER: str
PIPE_SEND_GRAD_TIMER: str
PIPE_RECV_INPUT_TIMER: str
PIPE_RECV_GRAD_TIMER: str

def is_even(number): ...
def split_half_float_double_sparse(tensors): ...

mem_alloced: int
mem_cached: int
ZERO_SUPPORTED_OPTIMIZERS: Incomplete

def is_zero_supported_optimizer(optimizer): ...

class get_args:
    def __init__(self, args_dict) -> None: ...

def initialize(args: Incomplete | None = None, model: nn.Module = None, optimizer: Optimizer = None, model_parameters: Incomplete | None = None, training_data: Incomplete | None = None):
    """
    Initial pipeline parallel engine.

    :param args: dict-like config.
    :param model: list of modules.
    :param model_parameters:module's parameters to train.
    :param training_Data: training dataset.

    :return pipeline parallel engine.
    """

class VQNetDeepSpeedEngine(Module):
    """DeepSpeed engine for training."""
    dont_change_device: Incomplete
    client_optimizer: Incomplete
    client_lr_scheduler: Incomplete
    training_data: Incomplete
    collate_fn: Incomplete
    mpu: Incomplete
    all_to_all_group: Incomplete
    data_parallel_group: Incomplete
    global_steps: int
    global_samples: int
    micro_steps: int
    skipped_steps: int
    gradient_average: bool
    warn_unscaled_loss: bool
    config: Incomplete
    loaded_checkpoint_mp_world_size: Incomplete
    loaded_checkpoint_dp_world_size: Incomplete
    enable_backward_allreduce: bool
    progressive_layer_drop: Incomplete
    eigenvalue: Incomplete
    block_eigenvalue: Incomplete
    gas_boundary_ctr: int
    dist_backend: str
    has_moe_layers: bool
    num_experts: Incomplete
    gate_modules: Incomplete
    moe_layers: Incomplete
    use_ds_comm: bool
    checkpoint_engine: Incomplete
    scale_wrt_gas: Incomplete
    losses: float
    monitor: Incomplete
    pipeline_parallelism: Incomplete
    param_names: Incomplete
    training_dataloader: Incomplete
    optimizer: Incomplete
    basic_optimizer: Incomplete
    lr_scheduler: Incomplete
    sparse_tensor_module_names: Incomplete
    save_non_zero_checkpoint: bool
    save_zero_checkpoint: bool
    flatten: Incomplete
    unflatten: Incomplete
    def __init__(self, args, model, optimizer: Incomplete | None = None, model_parameters: Incomplete | None = None, training_data: Incomplete | None = None, lr_scheduler: Incomplete | None = None, mpu: Incomplete | None = None, dist_init_required: Incomplete | None = None, collate_fn: Incomplete | None = None, config: Incomplete | None = None, config_class: Incomplete | None = None, dont_change_device: bool = False) -> None: ...
    def deepspeed_io(self, dataset, batch_size: Incomplete | None = None, route=..., pin_memory: bool = False, data_sampler: Incomplete | None = None, collate_fn: Incomplete | None = None, num_local_io_workers: int = 0): ...
    def destroy(self) -> None: ...
    def set_train_batch_size(self, train_batch_size) -> None:
        """Adjust the global batch size by increasing or decreasing the number of
        micro-batches (i.e., gradient accumulation steps). The size of each micro-batch
        (i.e., ``train_micro_batch_size_per_gpu``) is not changed.
        Args:
            train_batch_size (int): The new global batch size for training.
        Raises:
            ValueError: if ``train_batch_size`` is not divisible by the
                configured micro-batch size and data parallelism.
        """
    def set_train_micro_batch_size(self, micro_batch_size) -> None:
        """Adjust the micro batch size(i.e., the micro batch size in every data parallel group),
        while keep the gradient accumulation steps the same.
        Args:
            micro_batch_size (int): The new micro batch size for training.
        """
    def __getattr__(self, name):
        """
        Pass through attributes defined in the model if they are not overridden by ds-engine.
        """
    def train_batch_size(self): ...
    def train_micro_batch_size_per_gpu(self): ...
    def optimizer_name(self): ...
    def optimizer_params(self): ...
    def zero_optimization(self): ...
    def zero_allow_untested_optimizer(self): ...
    def zero_force_ds_cpu_optimizer(self): ...
    def zero_reduce_scatter(self): ...
    def zero_overlap_comm(self): ...
    def zero_offload_optimizer(self): ...
    def zero_partial_offload(self): ...
    def zero_sub_group_size(self): ...
    def zero_optimization_stage(self): ...
    def mics_shard_size(self): ...
    def zero_reduce_bucket_size(self): ...
    def zero_multi_rank_bucket_allreduce(self): ...
    def zero_allgather_bucket_size(self): ...
    def zero_optimization_partition_gradients(self): ...
    def zero_optimization_partition_weights(self): ...
    def zero_contiguous_gradients(self): ...
    def zero_round_robin_gradients(self): ...
    def zero_elastic_checkpoint(self): ...
    def zero_ignore_unused_parameters(self): ...
    def gradient_accumulation_steps(self): ...
    def load_universal_checkpoint(self): ...
    @property
    def communication_data_type(self): ...
    @communication_data_type.setter
    def communication_data_type(self, value) -> None: ...
    def postscale_gradients(self): ...
    def gradient_predivide_factor(self): ...
    def steps_per_print(self): ...
    def gradient_clipping(self): ...
    @staticmethod
    def is_map_style_dataset(obj): ...
    @staticmethod
    def is_iterable_style_dataset(obj): ...
    def dataloader_drop_last(self): ...
    def was_step_applied(self) -> bool:
        """Returns True if the latest ``step()`` produced in parameter updates.
        Note that a ``False`` return is not an error condition. Steps are frequently
        no-ops, such as between gradient accumulation boundaries or when overflows
        occur.
        """
    def train(self, mode: bool = True) -> None: ...
    def eval(self) -> None: ...
    def forward(self, *inputs, **kwargs):
        """Execute forward propagation
        Arguments:
            *inputs: Variable length input list
            **kwargs: variable length keyword arguments
        """
    def allreduce_gradients(self, bucket_size=...) -> None: ...
    def backward(self, loss, allreduce_gradients: bool = True, scale_wrt_gas: bool = True):
        """Execute backward pass on the loss

        """
    def is_gradient_accumulation_boundary(self):
        """
        Query whether the current micro-batch is at the boundary of
        gradient accumulation, and thus will trigger gradient reductions and
        an optimizer step.

        Returns:
            bool: if the current step is a gradient accumulation boundary.

        """
    def set_gradient_accumulation_boundary(self, is_boundary) -> None:
        """
        Manually overrides the DeepSpeed engine's gradient accumulation boundary state, this is an optional
        feature and should be used with care. The state should be set before to the intended
        value before each forward/backward. The final forward/backward should have the
        boundary state set to True. This style allows client code to only call engine.step() once after all
        the gradient accumulation passes are complete. See example below:
        .. code-block:: python
        engine.set_gradient_accumulation_boundary(False)
        for _ in range(gradient_accumulation_steps - 1):
            micro_batch = next(data_loader)
            loss = engine(micro_batch)
            engine.backward(loss)
        engine.set_gradient_accumulation_boundary(True)
        micro_batch = next(data_loader)
        loss = engine(micro_batch)
        engine.backward(loss)
        engine.step()
        Arguments:
            is_boundary (bool): are we at a gradient accumulation boundary or not?
        """
    def zero_grad(self) -> None:
        """
        Zero parameter grads.
        """
    def step(self, lr_kwargs: Incomplete | None = None) -> None:
        """Execute the weight update step after forward and backward propagation
        on effective_train_batch.
        """
    def allreduce_bucket(self, bucket, dp_group): ...
    def allreduce_and_copy(self, small_bucket, dp_group) -> None: ...
    def allreduce_no_retain(self, bucket, dp_group, numel_per_bucket: int = 500000000) -> None: ...
    def buffered_allreduce_fallback(self, grads: Incomplete | None = None, elements_per_buffer: int = 500000000) -> None: ...
    def update_optimizer_step(self, step) -> None: ...

class RepeatingLoader:
    loader: Incomplete
    data_iter: Incomplete
    def __init__(self, loader) -> None:
        """Wraps an iterator to allow for infinite iteration. This is especially useful
        for DataLoader types that we wish to automatically restart upon completion.

        Args:
            loader (iterator): The data loader to repeat.
        """
    def __iter__(self): ...
    def __next__(self): ...

class PipelineEngine(VQNetDeepSpeedEngine):
    """ A training engine hybrid pipeline, data, and model parallel training.

    This engine is created by ``initialize()`` when a :class:`PipelineModule`
    is provided.
    """
    enable_backward_allreduce: bool
    has_bool_tensors: Incomplete
    eval_return_logits: bool
    outputs: Incomplete
    using_bf16_optimizer: bool
    pipeline_enable_backward_allreduce: bool
    log_batch_step_id: int
    micro_batch_size: Incomplete
    micro_batches: Incomplete
    grid: Incomplete
    global_rank: Incomplete
    num_stages: Incomplete
    stage_id: Incomplete
    prev_stage: Incomplete
    next_stage: Incomplete
    data_iterator: Incomplete
    batch_fn: Incomplete
    is_pipe_parallel: Incomplete
    is_data_parallel: Incomplete
    is_model_parallel: Incomplete
    is_pipe_partitioned: Incomplete
    is_grad_partitioned: Incomplete
    num_pipe_buffers: int
    pipe_buffers: Incomplete
    pipe_recv_buf: Incomplete
    grad_layer: Incomplete
    meta_buffer: Incomplete
    first_output_send: bool
    first_gradient_send: bool
    pipe_partition_input_meta_cache: Incomplete
    pipe_partition_output_meta_cache: Incomplete
    pipe_partition_grad_meta_cache: Incomplete
    grad_partition_grad_layer_meta_cache: Incomplete
    loss: Incomplete
    total_loss: Incomplete
    loss_dict: Incomplete
    agg_loss: Incomplete
    dp_group_loss: Incomplete
    loss_model: Incomplete
    has_attention_mask: Incomplete
    def __init__(self, has_bool_tensors: bool = False, *super_args, **super_kwargs) -> None: ...
    def set_has_attention_mask(self, value) -> None: ...
    def eval_batch(self, data_iter, return_logits: bool = False, compute_loss: bool = True, reduce_output: str = 'avg', bcast_loss: bool = True, num_micro_batches: Incomplete | None = None): ...
    def set_train_batch_size(self, train_batch_size) -> None:
        """Adjust the global batch size by increasing or decreasing the number of
        micro-batches (i.e., gradient accumulation steps). The size of each micro-batch
        (i.e., ``train_micro_batch_size_per_gpu``) is not changed.
        Args:
            train_batch_size (int): The new global batch size for training.
        Raises:
            ValueError: if ``train_batch_size`` is not divisible by the
                configured micro-batch size and data parallelism.
        """
    def is_first_stage(self):
        """True if this process is in the first stage in the pipeline."""
    def is_last_stage(self):
        """True if this process is in the last stage in the pipeline."""
    training_dataloader: Incomplete
    def set_dataloader(self, loader) -> None: ...
    def set_dataiterator(self, iterator) -> None:
        """ Store an iterator to sample for training data. """
    def set_batch_fn(self, fn) -> None:
        """Execute a post-processing function on input data.

        Args:
            fn (function): The function to run.
        """
    def is_gradient_accumulation_boundary(self):
        """True if the engine is executing a gradient reduction or optimizer step instruction.

        This is overridden from :class:`VQNetDeepSpeedEngine` to force reductions
        and steps when the pipeline engine is instructed to do so.

        Returns:
            bool: whether reductions and optimizer steps should occur.
        """
    agg_train_loss: Incomplete
    def train_batch(self):
        """Progress the pipeline to train the next batch of data.

        return:
            The arithmetic mean of the losses computed this batch.
        """
    def forward(self, *args, **kwargs) -> None:
        """Disabled for pipeline parallel training. See ``train_batch()``. """
    def backward(self, *args, **kwargs) -> None:
        """Disabled for pipeline parallel training. See ``train_batch()``. """
    def step(self, *args, **kwargs) -> None:
        """Disabled for pipeline parallel training. See ``train_batch()``. """
