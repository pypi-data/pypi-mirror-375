from _typeshed import Incomplete
from enum import Enum
from pydantic import BaseModel

class ZeroStageEnum(int, Enum):
    """ Enum class for possible zero stages """
    disabled = 0
    optimizer_states = 1
    gradients = 2
    weights = 3
    max_stage = 3

class pp_int(int):
    '''
    A wrapper for integers that will return a custom string or comma-formatted
    string of the integer. For example, print(pp_int(1e5)) will return
    "10,000". This is useful mainly for auto-generated documentation purposes.
    '''
    def __new__(cls, val, custom_print_str: Incomplete | None = None): ...

class DeepSpeedConfigModel(BaseModel):
    '''
    This class should be used as a base for all DeepSpeed configs. It extends
    pydantic.BaseModel to allow for deprecated fields. To enable this feature,
    add deprecated=True to pydantic.Field:

    my_dep_field: int = Field(0, deprecated=True)

    Deprecated Field kwargs:
    - deprecated: [True|False], default False
        Enables / Disables deprecated fields
    - deprecated_msg: str, default ""
        Message to include with deprecation warning
    - new_param: str, default ""
        Name of the field replacing the deprecated field
    - set_new_param: [True|False], default True
        If new_param is provided, enables setting the value of that param with
        deprecated field value
    - new_param_fn: callable, default (lambda x: x)
        If new_param is provided and set_new_param is True, this function will
        modify the value of the deprecated field before placing that value in
        the new_param field

    Example:
        my_new_field is replacing a deprecated my_old_field. The expected type
        for my_new_field is int while the expected type for my_old_field is
        str. We want to maintain backward compatibility with our configs, so we
        define the fields with:

        class MyExampleConfig(DeepSpeedConfigModel):
            my_new_field: int = 0
            my_old_field: str = Field(\'0\',
                                      deprecated=True,
                                      new_param=\'my_new_field\',
                                      new_param_fn=(lambda x: int(x)))
    '''
    def __init__(self, strict: bool = False, **data) -> None: ...
    model_config: Incomplete

class DeepSpeedZeroConfig(DeepSpeedConfigModel):
    """
    Sets parameters for ZeRO optimizations.
    """
    stage: ZeroStageEnum
    contiguous_gradients: bool
    reduce_scatter: bool
    reduce_bucket_size: int
    use_multi_rank_bucket_allreduce: bool
    allgather_partitions: bool
    allgather_bucket_size: int
    overlap_comm: bool | None
    load_from_fp32_weights: bool
    elastic_checkpoint: bool
    max_live_parameters: int
    max_reuse_distance: int
    gather_16bit_weights_on_model_save: bool
    use_all_reduce_for_fetch_params: bool
    stage3_gather_fp16_weights_on_model_save: bool
    ignore_unused_parameters: bool
    legacy_stage1: bool
    round_robin_gradients: bool
    zero_hpz_partition_size: int
    zero_quantized_weights: bool
    zero_quantized_nontrainable_weights: bool
    zero_quantized_gradients: bool
    mics_shard_size: int
    mics_hierarchical_params_gather: bool
    def overlap_comm_valid(self): ...
