from _typeshed import Incomplete

class ProcessTopology:
    ''' Manages the mapping of n-dimensional Cartesian coordinates to linear
    indices. This mapping is used to map the rank of processes to the grid
    for various forms of parallelism.

    Each axis of the tensor is accessed by its name. The provided ordering
    of the axes defines the layout of the topology. ProcessTopology uses a "row-major"
    layout of the tensor axes, and so axes=[\'x\', \'y\'] would map coordinates (x,y) and
    (x,y+1) to adjacent linear indices. If instead axes=[\'y\', \'x\'] was used, coordinates
    (x,y) and (x+1,y) would be adjacent.

    Some methods return ProcessCoord namedtuples.
    '''
    axes: Incomplete
    dims: Incomplete
    ProcessCoord: Incomplete
    mapping: Incomplete
    def __init__(self, axes, dims) -> None:
        """Create a mapping of n-dimensional tensor coordinates to linear indices.

        Arguments:
            axes (list): the names of the tensor axes
            dims (list): the dimension (length) of each axis of the topology tensor
        """
    def get_rank(self, **coord_kwargs):
        """Return the global rank of a process via its coordinates.

        Coordinates are specified as kwargs. For example:

            >>> X = ProcessTopology(axes=['x', 'y'], dims=[2,3])
            >>> X.get_rank(x=0, y=1)
            1
        """
    def get_axis_names(self):
        """Return a list of the axis names in the ordering of the topology. """
    def get_rank_repr(self, rank, omit_axes=['data', 'pipe'], inner_sep: str = '_', outer_sep: str = '-'):
        """Return a string representation of a rank.

        This method is primarily used for checkpointing model data.

        For example:
            >>> topo = Topo(axes=['a', 'b'], dims=[2, 2])
            >>> topo.get_rank_repr(rank=3)
            'a_01-b_01'
            >>> topo.get_rank_repr(rank=3, omit_axes=['a'])
            'b_01'

        Args:
            rank (int): A rank in the topology.
            omit_axes (list, optional): Axes that should not be in the representation. Defaults to ['data', 'pipe'].
            inner_sep (str, optional): [description]. Defaults to '_'.
            outer_sep (str, optional): [description]. Defaults to '-'.

        Returns:
            str: A string representation of the coordinate owned by ``rank``.
        """
    def get_dim(self, axis):
        """Return the number of processes along the given axis.

        For example:
            >>> X = ProcessTopology(axes=['x', 'y'], dims=[2,3])
            >>> X.get_dim('y')
            3
        """
    def get_coord(self, rank):
        """Return the coordinate owned by a process rank.

        The axes of the returned namedtuple can be directly accessed as members. For
        example:
            >>> X = ProcessTopology(axes=['x', 'y'], dims=[2,3])
            >>> coord = X.get_coord(rank=1)
            >>> coord.x
            0
            >>> coord.y
            1
        """
    def get_axis_comm_lists(self, axis):
        """ Construct lists suitable for a communicator group along axis ``axis``.

        Example:
            >>> topo = Topo(axes=['pipe', 'data', 'model'], dims=[2, 2, 2])
            >>> topo.get_axis_comm_lists('pipe')
            [
                [0, 4], # data=0, model=0
                [1, 5], # data=0, model=1
                [2, 6], # data=1, model=0
                [3, 7], # data=1, model=1
            ]

        Returns:
            A list of lists whose coordinates match in all axes *except* ``axis``.
        """
    def filter_match(self, **filter_kwargs):
        """Return the list of ranks whose coordinates match the provided criteria.

        Example:
            >>> X = ProcessTopology(axes=['pipe', 'data', 'model'], dims=[2, 2, 2])
            >>> X.filter_match(pipe=0, data=1)
            [2, 3]
            >>> [X.get_coord(rank) for rank in X.filter_match(pipe=0, data=1)]
            [ProcessCoord(pipe=0, data=1, model=0), ProcessCoord(pipe=0, data=1, model=1)]

        Arguments:
            **filter_kwargs (dict): criteria used to select coordinates.

        Returns:
            The list of ranks whose coordinates match filter_kwargs.
        """
    def get_axis_list(self, axis, idx):
        """Returns the list of global ranks whose coordinate in an axis is idx.

        For example:
            >>> X = ProcessTopology(axes=['x', 'y'], dims=[2,3])
            >>> X.get_axis_list(axis='x', idx=0)
            [0, 1, 2]
            >>> X.get_axis_list(axis='y', idx=0)
            [0, 3]
        """
    def world_size(self): ...

class PipeDataParallelTopology(ProcessTopology):
    """ A topology specialization for hybrid data and pipeline parallelism.

        Uses data parallelism on the last dimension to encourage gradient
        reductions to use high-bandwidth intra-node links and lower-volume
        pipeline communications to use low-bandwidth inter-node links.
    """
    def __init__(self, num_pp, num_dp) -> None: ...

class PipeModelDataParallelTopology(ProcessTopology):
    """ A topology for hybrid pipeline, model, and data parallelism. """
    def __init__(self, num_pp, num_mp, num_dp) -> None: ...

class PipelineParallelGrid:
    """Implements a grid object that stores the data parallel ranks
    corresponding to each of the model parallel stages

    The grid object organizes the processes in a distributed vqnet job
    into a 2D grid, of stage_id and data_parallel_id.

    self.stage_id and self.data_parallel_id stores the stage id
    and the data parallel id of current process.

    self.dp_group groups the processes by stage_id.
    self.dp_group[i], is a list containing all process ranks whose
    stage_id is i.

    self.p2p_groups stores a list of tuple, where each tuple
    stores process ranks of adjacent stages for a given data_parallel_id.
    For example if num_stage is 5 then a tuple [7,8] represents stages [3, 4],
    with data_parallel id = 1. A stage wrap around will appear as non-adjacent ranks,
    for example tuple [4,0] with representing wrap-around stage 4 and 0, for
    data_parallel_id = 0, or similarly [9,5] represents wrapped around stages [4,0]
    for data_parallel_id = 1.
    """
    global_rank: Incomplete
    world_size: Incomplete
    data_parallel_size: Incomplete
    pipe_parallel_size: Incomplete
    model_parallel_size: Incomplete
    slice_parallel_size: Incomplete
    stage_id: Incomplete
    data_parallel_id: Incomplete
    ds_model_proc_group: Incomplete
    ds_model_rank: int
    ds_model_world_size: Incomplete
    dp_group: Incomplete
    dp_groups: Incomplete
    dp_proc_group: Incomplete
    is_first_stage: Incomplete
    is_last_stage: Incomplete
    p2p_groups: Incomplete
    pp_group: Incomplete
    pp_proc_group: Incomplete
    pipe_groups: Incomplete
    slice_group: Incomplete
    slice_proc_group: Incomplete
    mp_group: Incomplete
    model_groups: Incomplete
    def __init__(self, topology: Incomplete | None = None, process_group: Incomplete | None = None) -> None: ...
    def get_stage_id(self): ...
    def get_data_parallel_id(self): ...
    def stage_to_global(self, stage_id, **kwargs): ...
    def topology(self): ...
    def get_global_rank(self): ...
    def get_pipe_parallel_rank(self):
        """ The stage of the pipeline this rank resides in. """
    def get_pipe_parallel_world_size(self):
        """ The number of stages in the pipeline. """
    def get_pipe_parallel_group(self):
        """ The group of ranks within the same pipeline. """
    def get_data_parallel_rank(self):
        """ Which pipeline this rank resides in. """
    def get_data_parallel_world_size(self):
        """ The number of pipelines. """
    def get_data_parallel_group(self):
        """ The group of ranks within the same stage of all pipelines. """
    def get_model_parallel_rank(self): ...
    def get_model_parallel_world_size(self): ...
    def get_model_parallel_group(self): ...
    def get_slice_parallel_rank(self): ...
    def get_slice_parallel_world_size(self): ...
    def get_slice_parallel_group(self): ...
