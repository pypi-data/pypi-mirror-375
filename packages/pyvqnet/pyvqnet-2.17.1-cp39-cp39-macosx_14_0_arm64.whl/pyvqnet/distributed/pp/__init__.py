##
#pipeline parallism
##

from ..._core.vqnet import if_gpu_compiled, if_nccl_compiled
if if_gpu_compiled() and if_nccl_compiled():

    from .wrapper import PipelineParallelTrainingWrapper
else:
    raise ImportWarning("PipelineParallelTrainingWrapper only avaiable if_gpu_compiled() and if_nccl_compiled()")