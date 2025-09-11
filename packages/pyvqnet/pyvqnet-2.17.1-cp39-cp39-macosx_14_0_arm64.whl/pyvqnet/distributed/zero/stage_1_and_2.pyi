from ..configs import groups as groups
from ..configs.constants import BASE_OPTIMIZER_STATE as BASE_OPTIMIZER_STATE, BASE_OPTIMIZER_STATE_STEP as BASE_OPTIMIZER_STATE_STEP, CLIP_GRAD as CLIP_GRAD, DS_VERSION as DS_VERSION, GROUP_PADDINGS as GROUP_PADDINGS, LOSS_SCALER as LOSS_SCALER, PARAM_SLICE_MAPPINGS as PARAM_SLICE_MAPPINGS, PARTITION_COUNT as PARTITION_COUNT, PIPE_REPLICATED as PIPE_REPLICATED, SINGLE_PARTITION_OF_FP32_GROUPS as SINGLE_PARTITION_OF_FP32_GROUPS, ZERO_STAGE as ZERO_STAGE
from .base_optimizer import ZeROOptimizer as ZeROOptimizer
from .runtime.utils import align_dense_tensors as align_dense_tensors, all_gather_dp_groups as all_gather_dp_groups, is_model_parallel_parameter as is_model_parallel_parameter
from .utils import logger as logger
from .zero_config import ZeroStageEnum as ZeroStageEnum
from _typeshed import Incomplete
from collections import OrderedDict as OrderedDict
from pyvqnet.tensor import flatten_dense_tensors as flatten_dense_tensors, tensor as tensor, unflatten_dense_tensors as unflatten_dense_tensors

pg_correctness_test: bool
OPTIMIZER_ALLGATHER_TIMER: str
OPTIMIZER_GRADIENTS_TIMER: str
OPTIMIZER_STEP_TIMER: str
OPTIMIZER_TIMERS: Incomplete

class LossScalerBase:
    """LossScalarBase
    Base class for a loss scaler
    """
    cur_scale: Incomplete
    dynamic: bool
    def __init__(self, cur_scale) -> None: ...
    @property
    def loss_scale(self): ...
    def scale_gradient(self, module, grad_in, grad_out): ...
    def update_scale(self, overflow) -> None: ...
    def backward(self, loss) -> None: ...

class LossScaler(LossScalerBase):
    """
    Class that manages a static loss scale.  This class is intended to interact with
    :class:`FP16_Optimizer`, and should not be directly manipulated by the user.

    Use of :class:`LossScaler` is enabled via the ``static_loss_scale`` argument to
    :class:`FP16_Optimizer`'s constructor.

    Args:
        scale (float, optional, default=1.0):  The loss scale.
    """
    def __init__(self, scale: int = 1) -> None: ...
    def has_overflow(self, params): ...

class DeepSpeedZeroOptimizer(ZeROOptimizer):
    """
    DeepSpeedZeroOptimizer designed to reduce the memory footprint
    required for training large deep learning models.

    For more details please see ZeRO: Memory Optimization Towards Training A Trillion Parameter Models
    https://arxiv.org/abs/1910.02054

    For usage examples, refer to TODO: DeepSpeed Tutorial

    """
    cpu_offload: bool
    cpu_offload_pin_memory: bool
    elastic_checkpoint: Incomplete
    param_names: Incomplete
    mpu: Incomplete
    optimizer: Incomplete
    flatten: Incomplete
    unflatten: Incomplete
    partition_gradients: bool
    reduce_scatter: Incomplete
    overlap_comm: bool
    deepspeed_adam_offload: bool
    device: Incomplete
    dp_process_group: Incomplete
    sequence_parallel_size: Incomplete
    ep_process_group: Incomplete
    expert_dp_process_group: Incomplete
    real_dp_process_group: Incomplete
    partition_count: Incomplete
    is_gradient_accumulation_boundary: bool
    contiguous_gradients: bool
    has_moe_layers: bool
    model_parallel_group: Incomplete
    model_parallel_world_size: int
    model_parallel_rank: int
    overflow: bool
    clip_grad: Incomplete
    communication_data_type: Incomplete
    gradient_predivide_factor: Incomplete
    postscale_gradients: Incomplete
    gradient_accumulation_steps: Incomplete
    micro_step_id: int
    ignore_unused_parameters: Incomplete
    round_robin_gradients: Incomplete
    extra_large_param_to_reduce: Incomplete
    fp16_master_weights_and_gradients: bool
    bit16_groups: Incomplete
    bit16_groups_flat: Incomplete
    parallel_partitioned_bit16_groups: Incomplete
    single_partition_of_fp32_groups: Incomplete
    params_not_in_partition: Incomplete
    params_in_partition: Incomplete
    first_offset: Incomplete
    partition_size: Incomplete
    nccl_start_alignment_factor: int
    all_reduce_print: bool
    dtype: Incomplete
    gradient_accumulation_dtype: Incomplete
    use_separate_grad_accum: bool
    use_grad_accum_attribute: bool
    round_robin_bit16_groups: Incomplete
    round_robin_bit16_indices: Incomplete
    round_robin_bit16_meta: Incomplete
    groups_padding: Incomplete
    reduce_bucket_size: Incomplete
    use_multi_rank_bucket_allreduce: bool
    allgather_bucket_size: Incomplete
    reduction_stream: Incomplete
    callback_queued: bool
    param_dict: Incomplete
    is_param_in_current_partition: Incomplete
    grads_in_ipg_bucket: Incomplete
    params_in_ipg_bucket: Incomplete
    elements_in_ipg_bucket: int
    params_already_reduced: Incomplete
    previous_reduced_grads: Incomplete
    ipg_bucket_has_moe_params: bool
    param_id: Incomplete
    param_to_partition_ids: Incomplete
    is_partition_reduced: Incomplete
    remaining_grads_in_partition: Incomplete
    total_grads_in_partition: Incomplete
    is_grad_computed: Incomplete
    grad_partition_insertion_offset: Incomplete
    grad_start_offset: Incomplete
    averaged_gradients: Incomplete
    offload_gradient_dict: Incomplete
    first_param_index_in_partition: Incomplete
    custom_loss_scaler: bool
    external_loss_scale: Incomplete
    loss_scaler: Incomplete
    dynamic_loss_scale: Incomplete
    def __init__(self, init_optimizer, param_names, backend, static_loss_scale: float = 1.0, dynamic_loss_scale: bool = False, dynamic_loss_args: Incomplete | None = None, verbose: bool = True, contiguous_gradients: bool = True, reduce_bucket_size: int = 500000000, use_multi_rank_bucket_allreduce: bool = True, allgather_bucket_size: int = 5000000000, dp_process_group: Incomplete | None = None, expert_parallel_group: Incomplete | None = None, expert_data_parallel_group: Incomplete | None = None, reduce_scatter: bool = False, overlap_comm: bool = False, offload_optimizer_config: Incomplete | None = None, mpu: Incomplete | None = None, clip_grad: float = 0.0, gradient_accumulation_dtype=..., communication_data_type=..., postscale_gradients: bool = True, gradient_predivide_factor: float = 1.0, gradient_accumulation_steps: int = 1, ignore_unused_parameters: bool = True, partition_grads: bool = False, round_robin_gradients: bool = False) -> None: ...
    def initialize_optimizer_states(self) -> None: ...
    def reduce_gradients(self, pipeline_parallel: bool = False) -> None: ...
    def independent_gradient_partition_epilogue(self) -> None: ...
    def overlapping_partition_gradients_reduce_epilogue(self) -> None: ...
    def get_gradient_for_reduction(self, param): ...
    def get_param_gradient_attribute(self, param): ...
    def clear_grad_attribute(self, param) -> None: ...
    def get_param_id(self, param): ...
    def flatten_dense_tensors_aligned(self, tensor_list, alignment): ...
    def reduce_independent_p_g_buckets_and_remove_grads(self, param, i) -> None: ...
    grads_in_partition_offset: int
    grads_in_partition: Incomplete
    def copy_grads_in_partition(self, param) -> None: ...
    def reduce_ipg_grads(self) -> None: ...
    def reduce_ready_partitions_and_remove_grads(self, param, i) -> None: ...
    def allreduce_bucket(self, bucket, rank: Incomplete | None = None, log: Incomplete | None = None, divide: bool = True, process_group: Incomplete | None = None): ...
    def buffered_reduce_fallback(self, rank, grads, elements_per_buffer: int = 500000000, log: Incomplete | None = None) -> None: ...
    def get_data_parallel_partitions(self, tensor, group_id): ...
    def get_partition_info(self, tensor_list, partition_size, partition_id): ...
    def zero_grad(self, set_to_none: bool = True) -> None:
        """
        Zero FP16 parameter grads.
        """
    def get_grad_norm_direct(self, gradients, params, norm_type: int = 2):
        """Clips gradient norm of an iterable of parameters.

        This is adapted from tensor.nn.utils.clip_grad.clip_grad_norm_ and
        added functionality to handle model parallel parameters. Note that
        the gradients are modified in place.

        Arguments:
            parameters (Iterable[Tensor] or Tensor): an iterable of Tensors or a
                single Tensor that will have gradients normalized
            max_norm (float or int): max norm of the gradients
            norm_type (float or int): type of the used p-norm. Can be ``'inf'`` for
                infinity norm.

        Returns:
            Total norm of the parameters (viewed as a single vector).
        """
    def get_flat_partition(self, tensor_list, first_offset, partition_size, dtype, device, return_tensor_list: bool = False): ...
    def free_grad_in_param_list(self, param_list) -> None: ...
    def set_lr(self, lr) -> None:
        """Set the learning rate."""
    def get_lr(self):
        """Return the current learning rate."""
    def scaled_global_norm(self, norm_type: int = 2): ...
    def step(self, closure: Incomplete | None = None) -> None:
        """
        Not supporting closure.
        """
    def update_lp_params(self) -> None: ...
    def unscale_and_clip_grads(self, grad_groups_flat, total_norm) -> None: ...
    ipg_buffer: Incomplete
    ipg_index: int
    def backward(self, loss, retain_graph: bool = False) -> None:
        """
        :attr:`backward` performs the following steps:

        1. fp32_loss = loss.float()
        2. scaled_loss = fp32_loss*loss_scale
        3. scaled_loss.backward(), which accumulates scaled gradients into the ``.grad`` attributes of the model's fp16 leaves
        """
    state: Incomplete
    param_groups: Incomplete
    loss_scale: Incomplete
    cur_scale: Incomplete
    def state_dict(self):
        '''
        Returns a dict containing the current state of this :class:`FP16_Optimizer` instance.
        This dict contains attributes of :class:`FP16_Optimizer`, as well as the state_dict
        of the contained Pytorch optimizer.
        Example::
            checkpoint = {}
            checkpoint[\'model\'] = model.state_dict()
            checkpoint[\'optimizer\'] = optimizer.state_dict()
            torch.save(checkpoint, "saved.pth")
        '''
    @property
    def param_groups(self):
        """Forward the wrapped optimizer's parameters."""
