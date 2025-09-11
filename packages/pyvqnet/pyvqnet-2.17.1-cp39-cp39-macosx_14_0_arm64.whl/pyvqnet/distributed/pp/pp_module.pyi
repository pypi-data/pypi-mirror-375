import pyvqnet.nn as nn
from ...device import DEV_GPU as DEV_GPU
from .topo import PipeDataParallelTopology as PipeDataParallelTopology, PipelineParallelGrid as PipelineParallelGrid
from _typeshed import Incomplete
from pyvqnet.logger import logger as logger

class PipelineError(Exception):
    """Errors related to the use of deepspeed.PipelineModule """

class LayerSpec:
    """Building block for specifying pipeline-parallel modules.

    LayerSpec stores the type information and parameters for each stage in a
    PipelineModule. For example:
    """
    typename: Incomplete
    module_args: Incomplete
    module_kwargs: Incomplete
    global_rank: Incomplete
    def __init__(self, typename, *module_args, **module_kwargs) -> None: ...
    def build(self, log: bool = False):
        """Build the stored specification."""

class TiedLayerSpec(LayerSpec):
    key: Incomplete
    forward_fn: Incomplete
    tied_weight_attr: Incomplete
    def __init__(self, key, typename, *module_args, forward_fn: Incomplete | None = None, tied_weight_attr=['weight'], **module_kwargs) -> None: ...

class PipelineModule(nn.Module):
    """Modules to be parallelized with pipeline parallelism.

    The key constraint that enables pipeline parallelism is the
    representation of the forward pass as a sequence of layers
    and the enforcement of a simple interface between them. The
    forward pass is implicitly defined by the module ``layers``. 

    :param layers: (Iterable) A sequence of layers defining the pipeline structure. Can be a ``nn.Sequential`` module.
    :param num_stages: (int, optional) The degree of pipeline parallelism. If not specified, ``topology`` must be provided.
    :param topology: (``deepspeed.runtime.pipe.ProcessTopology``, optional) Defines the axes of parallelism axes for training. Must be provided if ``num_stages`` is ``None``.
    :param loss_fn: (callable, optional) The function to compute the loss as ``loss = loss_fn(outputs, label``.
    :param base_seed: (int, optional) The starting seed for layer seeding. Defaults to 1234.
    :param partition_method: (str, optional) The method upon which the layers are partitioned. Defaults to 'parameters'.

    """
    micro_offset: int
    loss_fn: Incomplete
    checkpointable_layers: Incomplete
    seed_layers: bool
    seed_fn: Incomplete
    base_seed: Incomplete
    world_group: Incomplete
    global_rank: Incomplete
    world_size: Incomplete
    local_rank: Incomplete
    num_stages: Incomplete
    stage_id: Incomplete
    forward_funcs: Incomplete
    fwd_map: Incomplete
    tied_modules: Incomplete
    tied_weight_attrs: Incomplete
    tied_comms: Incomplete
    activation_checkpoint_interval: Incomplete
    activation_checkpoint_func: Incomplete
    def __init__(self, layers, num_stages: Incomplete | None = None, topology: Incomplete | None = None, loss_fn: Incomplete | None = None, base_seed: int = 1234, partition_method: str = 'parameters') -> None: ...
    curr_layer: Incomplete
    def forward(self, forward_input): ...
    def allreduce_tied_weight_gradients(self) -> None:
        """All reduce the gradients of the tied weights between tied stages"""
    def get_tied_weights_and_groups(self): ...
    def partitions(self): ...
    def stage_owner(self, layer_idx): ...
    def topology(self):
        """ ProcessTopology object to query process mappings. """
    def mpu(self): ...
    def num_pipeline_stages(self): ...
