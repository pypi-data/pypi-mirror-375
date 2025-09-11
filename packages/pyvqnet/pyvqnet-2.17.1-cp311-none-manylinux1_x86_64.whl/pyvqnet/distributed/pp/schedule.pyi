import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from collections.abc import Generator

def call_to_str(base, *args, **kwargs):
    """Construct a string representation of a call.

    Args:
        base (str): name of the call
        args (tuple, optional): args to ``base``
        kwargs (dict, optional): kwargs supplied to ``base``

    Returns:
        str: A string representation of base(*args, **kwargs)
    """

class PipeSchedule(ABC, metaclass=abc.ABCMeta):
    """Directs the execution of a pipeline engine by generating sequences of
    :class:`PipeInstruction`.

    Schedules are generators that yield sequences of
    :class:`PipeInstruction` to process the micro-batches in one batch.
    Each yielded step is atomic in the sense that a barrier
    synchronization can be placed between successive steps without
    deadlock.

    Below is an example schedule that implements data parallelism with gradient accumulation:

    .. code-block:: python

        class DataParallelSchedule(PipeSchedule):
            def steps(self):
                for step_id in range(self.micro_batches):
                    cmds = [
                        LoadMicroBatch(buffer_id=0),
                        ForwardPass(buffer_id=0),
                        BackwardPass(buffer_id=0),
                    ]
                    if step_id == self.micro_batches - 1:
                        cmds.extend([
                            ReduceGrads(),
                            OptimizerStep(),
                        ])
                    yield cmds

            def num_pipe_buffers(self):
                return 1

    Args:
        micro_batches (int): The number of micro-batches that comprise a batch.
        stages (int): The number of pipeline stages.
        stage_id (int): The pipe stage that will execute the generated schedule.
    """
    micro_batches: Incomplete
    stages: Incomplete
    stage_id: Incomplete
    prev_stage: Incomplete
    next_stage: Incomplete
    def __init__(self, micro_batches, stages, stage_id) -> None: ...
    @abstractmethod
    def steps(self):
        """Yield a list of :class:`PipeInstruction` for each step in the schedule.

        .. note::
            Schedules must implement ``steps()`` to define the schedule.

        Returns:
            Instructions to be executed as one step of the pipeline
        """
    def num_pipe_buffers(self):
        """The number of pipeline buffers that will be used by this stage.

        .. note::
            Schedules should specialize ``num_pipe_buffers()`` for memory savings at scale.

        Returns:
            The number of buffers for the engine to allocate.
        """
    @property
    def stage(self):
        """Stage index used to configure this schedule."""
    @property
    def num_stages(self):
        """The number of total pipeline stages used to configure this schedule."""
    @property
    def num_micro_batches(self):
        """The number of total micro_batches used to configure this schedule."""
    @property
    def is_first_stage(self):
        """True if the configured ``stage_id`` is the first stage in the pipeline."""
    @property
    def is_last_stage(self):
        """True if the configured ``stage_id`` is the last stage in the pipeline."""
    it: Incomplete
    def __iter__(self): ...
    def __next__(self): ...

class InferenceSchedule(PipeSchedule):
    """A schedule for inferencing batches using pipeline parallelism.
    """
    def steps(self) -> Generator[Incomplete]: ...
    def num_pipe_buffers(self):
        """Only two pipeline buffers are required for inferencing.

        Returns:
            ``2``
        """

class TrainSchedule(PipeSchedule):
    """A schedule for training a batch using hybrid parallelism.

    Pipeline parallelism is extracted through gradient accumulation and thus
    convergence follows that of a data parallel approach with the same batch
    size.
    """
    def steps(self) -> Generator[Incomplete]: ...
    def num_pipe_buffers(self):
        """Return the number of pipeline buffers required for this stage.

        This is equivalent to the maximum number of in-flight forward passes,
        since we need to remember the activations of forward passes in order
        to run backpropagation. For synchronous 1F1B, this is equivalent to
        the index difference between this stage and the last stage.
        """

class DataParallelSchedule(PipeSchedule):
    """An example schedule that trains using traditional data parallelism with gradient
    accumulation.
    """
    def steps(self) -> Generator[Incomplete]: ...
    def num_pipe_buffers(self):
        """Only one pipeline buffer needed.
        """

class PipeInstruction:
    """Base class for all instructions to be executed by the pipeline engine.

    All keyword arguments are stored as members similar to a ``namedtuple``. These are
    then accessible to the :class:`PipeEngine` during execution.

    Args:
        kwargs (optional): keyword arguments to store as members
    """
    name: Incomplete
    kwargs: Incomplete
    def __init__(self, **kwargs) -> None: ...

class OptimizerStep(PipeInstruction):
    """Performs one step with the optimizer and zeros gradients.

    .. note:: Should be issued after :class:`ReduceGrads` and :class:`ReduceTiedGrads`.

    .. note:: Can be a synchronization point among data-parallel ranks.
    """
class ReduceGrads(PipeInstruction):
    """Reduce the computed gradients among data-parallel processes within the stage.
    """
class ReduceTiedGrads(PipeInstruction):
    """Reduce the computed gradients of tied modules within a pipeline-parallel group.

    .. warning::
        The stages included in this synchronization point are not known until
        the model is partitioned among pipeline stages. In the worst case, it
        includes all pipeline stages. This instruction should be scheduled
        carefully to avoid deadlocks.
    """

class BufferOpInstruction(PipeInstruction):
    """A pipeline instruction that operates on pipeline buffer(s).

    Args:
        buffer_id (int): the index of the pipeline buffer() to modify.
    """
    def __init__(self, buffer_id, **kwargs) -> None: ...

class LoadMicroBatch(BufferOpInstruction):
    """Load a micro-batch into a buffer.

    Roughly:

    .. code-block:: python

        buffers['inputs'][buffer_id] = next(data_iter)
    """
class ForwardPass(BufferOpInstruction):
    """Compute a forward pass.

    Roughly:

    .. code-block:: python

        buffers['outputs'][buffer_id] = forward(buffers['inputs'][buffer_id])
    """
class BackwardPass(BufferOpInstruction):
    """Compute a backward pass and accumulate gradients.

    """
class SendActivation(BufferOpInstruction):
    """Send activations to the next stage in the pipeline.

    """
class RecvActivation(BufferOpInstruction):
    """Receive activations from the previous stage in the pipeline.

    """
class SendGrad(BufferOpInstruction):
    """Send computed gradients to the previous pipeline stage.
    with respect to the received activations

    .. note::
        Only received tensors with ``requires_grad==True`` will produce gradients.
        Missing gradients will be replaced with ``None`` on the receiving stage.

    .. note::
        The communication is blocking and must be paired with a :class:`RecvGrad`
        on the previous pipeline stage to avoid deadlock.
    """
class RecvGrad(BufferOpInstruction):
    """Receive computed gradients the next pipeline stage.

    .. note::
        Only activations with ``requires_grad==True`` will produce gradients.
        Missing gradients will be replaced with ``None``.

    .. note::
        The communication is blocking and must be paired with a :class:`SendGrad`
        on the next pipeline stage to avoid deadlock.
    """
