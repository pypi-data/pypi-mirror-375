from .. import dist_cal_src as dist_cal_src
from ..backends import check_not_default_backend as check_not_default_backend, get_backend as get_backend, global_backend as global_backend
from ..config import get_is_dist_init as get_is_dist_init, set_is_dist_init as set_is_dist_init
from ..device import DEV_CPU as DEV_CPU, DEV_GPU as DEV_GPU
from _typeshed import Incomplete
from functools import lru_cache
from pyvqnet.tensor import tensor as tensor

@lru_cache
def is_mpi4py_version_greater_than(current_version, v): ...

current_version: Incomplete
comm: Incomplete

def is_initialized():
    """
    Return if control common initialized or not.
    """
def is_available():
    """
    if mpi is valid or not.
    """
def get_host_hash(string): ...
def get_host_name(): ...
def get_local_rank():
    """
    A method to get the process number on the current host.
    If use torch backend,you have to set os['LOCAL_RANK']
    
    Example::

        from pyvqnet.distributed import get_local_rank
                
        local_rank = get_local_rank()
        
        # mpirun -n 2 -f hosts python test.py 
    """
def get_rank():
    """
    A method to get the current process number.

    Example::

        from pyvqnet.distributed import get_rank
        cur_rank = get_rank()
        
    """
get_global_rank = get_rank

def get_world_size():
    """
    A method to get all process numbers.

    Example::

        from pyvqnet.distributed import get_size
        size = get_size()
        
    """
get_size = get_world_size

def get_group():
    """
    return current communication group for default `pyvqnet` backend.
    """
def init_group(rank_lists):
    """
    Initializes a set of communication groups and communicators for mpi.
    Use CommController.split_group for nccl.

    :param list rank_lists: A list of lists, where each sublist contains a set of process ranks.
                            For example: [[1, 2], [3, 4]].
    :raises ValueError: If the format of the input `rank_lists` is not as expected, or if any process number exceeds the total number of processes.

    :return: A list of lists, where each sublist contains a communicator and the corresponding rank list.

    """

class _CommController:
    """
    
    """
    finalized: bool
    backend: Incomplete
    nccl_op: Incomplete
    nccl_groups_dict: Incomplete
    nccl_color_groups_dict: Incomplete
    nccl_split_groups: Incomplete
    groupComm: Incomplete
    group_size: int
    rank: Incomplete
    size: Incomplete
    localrank: Incomplete
    def __init__(self, backend: str = 'mpi', rank=None, world_size=None, split_from: bool = False) -> None: ...
    def is_nccl_available(self):
        """Check if the NCCL backend is available."""
    def get_rank(self):
        '''
        A method to get the current process number.

        Example::

            from pyvqnet.distributed import CommController
            Comm_OP = CommController("nccl") # init nccl controller
            
            Comm_OP.getRank()
        '''
    getRank = get_rank
    def get_size(self):
        '''
        A method to get all process numbers.

        Example::

            from pyvqnet.distributed import CommController
            Comm_OP = CommController("nccl") # init nccl controller
            
            Comm_OP.getSize()
            # mpirun -n 2 python test.py 
            # 2
        '''
    getSize = get_size
    def get_local_rank(self):
        '''
        A method to get the process number on the current host.

        Example::

            from pyvqnet.distributed import CommController
            Comm_OP = CommController("nccl") # init nccl controller
            
            Comm_OP.getLocalRank()
            # mpirun -n 2 -f hosts python test.py 
        '''
    getLocalRank = get_local_rank
    def split_group(self, rank_lists):
        '''
        For pyvqnet + mpi backend, it returns communication groups of mpi.Comm.
        For pyvqnet + nccl backend,it returns None,use ncclSplitGroup to change every rank\'s color internally.

        ..note::
            for set_backend("torch"), it returns list of new ProcessGroup.

        :parma rank_lists: list of ranks for every groups.
        '''
    split_groups = split_group
    def get_device_num(self):
        '''
        A method to get the number of gpus on the current node.

        Example::

            from pyvqnet.distributed import CommController
            Comm_OP = CommController("nccl")
            Comm_OP.get_device_num()
            # 2
        '''
    def barrier(self):
        '''
        Synchronized use mpi.barrier or cudadevicesynchronize.

        Example::

            from pyvqnet.distributed import CommController
            Comm_OP = CommController("nccl")
            
            Comm_OP.barrier()
        '''
    def barrier_group(self, group=None):
        '''
        Synchronized method in process group.

        :param groups: communication process group.For nccl,the groups is defined
        
        Example::

            from pyvqnet.distributed import CommController, init_group
            Comm_OP = CommController("mpi")

            group_l = init_group([[0,1]])

            Comm_OP.barrier_group(group_l[0][0])
        '''
    def all_reduce(self, tensor_, c_op: str = 'avg') -> None:
        '''
        Reduces the tensor data across all machines in a way that all get the final result.

        After the call ``tensor`` is going to be bitwise identical in all processes.

        :param tensor_:  Input and output of the collective. The function operates in-place.
        :param c_op: calculation method,can be "sum" or "avg", default: "avg".
        
        Example::

            from pyvqnet.distributed import CommController
            from pyvqnet.tensor import tensor
            import numpy as np
            Comm_OP = CommController("mpi")

            num = tensor.to_tensor(np.random.rand(1, 5))
            print(f"rank {Comm_OP.getRank()}  {num}")

            Comm_OP.all_reduce(num, "sum")
            print(f"rank {Comm_OP.getRank()}  {num}")
            # mpirun -n 2 python test.py
        '''
    allreduce = all_reduce
    def reduce(self, tensor_, root: int = 0, c_op: str = 'avg') -> None:
        '''
        Reduces the tensor data across all machines.

        Only the process with rank ``root`` is going to receive the final result.

        :param tensor_: Input and output of the collective. The function
            operates in-place.
        :param root: rank of process to receive the final result.
        :param c_op: calculation method.
        
        Example::

            from pyvqnet.distributed import CommController
            from pyvqnet.tensor import tensor
            import numpy as np
            Comm_OP = CommController("mpi")

            num = tensor.to_tensor(np.random.rand(1, 5))
            print(f"rank {Comm_OP.getRank()}  {num}")
            
            Comm_OP.reduce(num, 1)
            print(f"rank {Comm_OP.getRank()}  {num}")
            # mpirun -n 2 python test.py
        '''
    def broadcast(self, tensor_, root: int = 0) -> None:
        '''
        Broadcast a message from one process to all other processes.

        :param tensor_: Data to be sent if ``root`` is the rank of current
            process, and tensor to be used to save received data otherwise..
        :param root: root.
        
        Example::

            from pyvqnet.distributed import CommController
            from pyvqnet.tensor import tensor
            import numpy as np
            Comm_OP = CommController("mpi")

            num = tensor.to_tensor(np.random.rand(1, 5))
            print(f"rank {Comm_OP.getRank()}  {num}")
            
            Comm_OP.broadcast(num, 1)
            print(f"rank {Comm_OP.getRank()}  {num}")
            # mpirun -n 2 python test.py
        '''
    def all_gather_batch_first(self, tensor_) -> tensor.QTensor:
        '''
        Gathers tensors from the whole group in a concatenated tensor.shape[0] is first dim.
        If tensor is 1d , return with shape of [size*tensor_.shape[0]].
        If tensor is 2d , return with shape of [tensor_.shape[0],size*tensor_.shape[1]].
        If tensor is >2d , return with shape of [tensor_.shape[0],size,tensor_.shape[1:]].
        All the tensors should have same shape.

        :param tensor_: input.
        :return all_gather_batch_first tensors.

        Example::

            from pyvqnet.distributed import CommController
            from pyvqnet.tensor import tensor
            import numpy as np
            Comm_OP = CommController("mpi")

            num = tensor.to_tensor(np.random.rand(1, 5))
            print(f"rank {Comm_OP.getRank()}  {num}")

            num = Comm_OP.all_gather_batch_first(num)
            print(f"rank {Comm_OP.getRank()}  {num}")
            # mpirun -n 2 python test.py
        '''
    def all_gather(self, tensor_):
        '''
        Gathers tensors from the whole group in a concatenated tensor.
        If tensor is 1d , return with shape of [size,tensor_.shape[0]].
        If tensor is >1d , return with shape of [size,tensor_.shape[0:]].
        All the tensors should have same shape.

        :param tensor_: input.
        :return all_gather tensors.

        Example::

            from pyvqnet.distributed import CommController
            from pyvqnet.tensor import tensor
            import numpy as np
            Comm_OP = CommController("mpi")

            num = tensor.to_tensor(np.random.rand(1, 5))
            print(f"rank {Comm_OP.getRank()}  {num}")

            num = Comm_OP.all_gather(num)
            print(f"rank {Comm_OP.getRank()}  {num}")
            # mpirun -n 2 python test.py
        '''
    allgather = all_gather
    def send_recv(self, send_buffer, dest, recv_buffer, source):
        """
        do peer to peer send and recv synchronously.

        :param send_buffer, send data.
        :param dest, integer target rank.
        :param recv_buffer, receive data.
        :param source, source rank.

        """
    def send(self, tensor_, dest) -> None:
        '''
        execute peer to peer send synchronously.

        :param tensor_: Tensor to send.
        :param dest: destination process rank.
        
        Example::

            from pyvqnet.distributed import CommController,get_rank
            from pyvqnet.tensor import tensor
            import numpy as np
            Comm_OP = CommController("mpi")

            num = tensor.to_tensor(np.random.rand(1, 5))
            recv = tensor.zeros_like(num)

            if get_rank() == 0:
                Comm_OP.send(num, 1)
            elif get_rank() == 1:
                Comm_OP.recv(recv, 0)
            print(f"rank {Comm_OP.getRank()}  {num}")
            print(f"rank {Comm_OP.getRank()}  {recv}")
            
            # mpirun -n 2 python test.py
        '''
    def recv(self, tensor_, source) -> None:
        '''
        execute peer to peer recv synchronously.

        :param tensor_: Tensor to receive.
        :param source: source process rank.
        
        Example::

            from pyvqnet.distributed import CommController,get_rank
            from pyvqnet.tensor import tensor
            import numpy as np
            Comm_OP = CommController("mpi")

            num = tensor.to_tensor(np.random.rand(1, 5))
            recv = tensor.zeros_like(num)

            if get_rank() == 0:
                Comm_OP.send(num, 1)
            elif get_rank() == 1:
                Comm_OP.recv(recv, 0)
            print(f"rank {Comm_OP.getRank()}  {num}")
            print(f"rank {Comm_OP.getRank()}  {recv}")
            
            # mpirun -n 2 python test.py
        '''
    def all_reduce_group(self, tensor_, c_op: str = 'avg', group=None) -> None:
        '''
        Reduce to All in process group.

        :param tensor_: Input and output of the collective. The function
            operates in-place.
        :param c_op: calculation method,default:"avg".
        :param group:process group,default:None,all process are used in all_reduce.

        Example::

            from pyvqnet.distributed import CommController,get_rank,get_local_rank
            from pyvqnet.tensor import tensor
            import numpy as np
            Comm_OP = CommController("nccl")

            new_group = Comm_OP._nccl_split_group([[0, 1]])

            complex_data = tensor.QTensor([3+1j, 2, 1 + get_rank()],dtype=8).reshape((3,1)).toGPU(1000+ get_local_rank())

            print(f"all_reduce_group before rank {get_rank()}: {complex_data}")

            Comm_OP.all_reduce_group(complex_data, c_op="sum",new_group[0])
            print(f"all_reduce_group after rank {get_rank()}: {complex_data}")
            # mpirun -n 2 python test.py
        '''
    allreduce_group = all_reduce_group
    def reduce_group(self, tensor_, root: int = 0, c_op: str = 'avg', group=None) -> None:
        '''
        Reduce tensor data to process with local_rank of `root` in process group.

        :param tensor_: Input and output of the collective. The function
            operates in-place.
        :param root: local rank in group for `pyvqnet`,global rank for `torch` and `torch-native`.
        :param c_op: calculation method.
        :param group: communication process group, for mpi ,group is group of comm, for nccl, group is target group index tuple.
        
        Example::
        
            from pyvqnet.distributed import CommController,get_rank,get_local_rank
            from pyvqnet.tensor import tensor
            import numpy as np
            Comm_OP = CommController("nccl")

            new_group = Comm_OP._nccl_split_group([[0, 1]])

            complex_data = tensor.QTensor([3+1j, 2, 1 + get_rank()],dtype=8).reshape((3,1)).toGPU(1000+ get_local_rank())

            print(f"reduce_group before rank {get_rank()}: {complex_data}")

            Comm_OP.reduce_group(complex_data, "sum",new_group[0])
            print(f"reduce_group after rank {get_rank()}: {complex_data}")
            # mpirun -n 2 python test.py
        '''
    def broadcast_group(self, tensor_, root: int = 0, group=None) -> None:
        '''
        Broadcast tensor data to process with local_rank of `root` in process group.

        :param tensor_: Input and output of the collective. The function
            operates in-place.
        :param root: local rank in group for `pyvqnet`,global rank for `torch` and `torch-native`. default: 0.
        :param group: communication process group, for mpi ,group is group of comm, for nccl, group is target group index tuple.
        
        Example::

            from pyvqnet.distributed import CommController,get_rank,get_local_rank
            from pyvqnet.tensor import tensor
            import numpy as np
            Comm_OP = CommController("nccl")

            new_group = Comm_OP._nccl_split_group([[0, 1]])

            complex_data = tensor.QTensor([3+1j, 2, 1 + get_rank()],dtype=8).reshape((3,1)).toGPU(1000+ get_local_rank())

            print(f"broadcast_group before rank {get_rank()}: {complex_data}")

            Comm_OP.broadcast_group(complex_data,new_group[0])
            Comm_OP.barrier()
            print(f"broadcast_group after rank {get_rank()}: {complex_data}")
            # mpirun -n 2 python test.py
        '''
    def all_gather_batch_first_group(self, tensor_, group=None):
        '''
        all_gather_batch_first_group tensor in process group.

        :param tensor_: Input and output of the collective. The function
            operates in-place.
        :param group: communication process group, for mpi ,group is group of comm, for nccl, group is target group index tuple.
        
        Example::

            from pyvqnet.distributed import CommController,get_rank,get_local_rank
            from pyvqnet.tensor import tensor
            import numpy as np
            Comm_OP = CommController("nccl")

            new_group = Comm_OP._nccl_split_group([[0, 1]])

            complex_data = tensor.QTensor([3+1j, 2, 1 + get_rank()],dtype=8).reshape((3,1)).toGPU(1000+ get_local_rank())

            print(f"all_gather_batch_first_group before rank {get_rank()}: {complex_data}")

            complex_data = Comm_OP.all_gather_batch_first_group(complex_data,new_group[0])
            print(f"all_gather_batch_first_group after rank {get_rank()}: {complex_data}")
            # mpirun -n 2 python test.py
        '''
    def all_gather_group(self, tensor_, group=None):
        '''
        all gather tensor in process group.

        :param tensor_: Input and output of the collective. The function
            operates in-place.
        :param group: communication process group, for mpi ,group is group of comm, for nccl, group is target group index tuple.
        
        Example::

            from pyvqnet.distributed import CommController,get_rank,init_group
            from pyvqnet.tensor import tensor

            Comm_OP = CommController("mpi")
            group = init_group([[0,1]])
            #mpi init group internally
            # A list of lists, where each sublist contains a communicator and the corresponding rank list.
            complex_data = tensor.QTensor([3+1j, 2, 1 + get_rank()],dtype=8).reshape((3,1))
            print(f" before rank {get_rank()}: {complex_data}")
            for comm_ in group:
                if Comm_OP.getRank() in comm_[1]:
                    complex_data = Comm_OP.all_gather_group(complex_data, comm_[0])
                    print(f"after rank {get_rank()}: {complex_data}")
            # mpirun -n 2 python test.py

            from pyvqnet.distributed import CommController,get_rank,get_local_rank
            from pyvqnet.tensor import tensor
            Comm_OP = CommController("nccl")
            new_group = Comm_OP._nccl_split_group([[0, 1]])
            complex_data = tensor.QTensor([3+1j, 2, 1 + get_rank()],dtype=8).reshape((3,1)).toGPU(1000+ get_local_rank())
            print(f" before rank {get_rank()}: {complex_data}")
            complex_data = Comm_OP.all_gather_group(complex_data,new_group[0])
            print(f"after rank {get_rank()}: {complex_data}")
            # mpirun -n 2 python test.py
        '''
    allgather_group = all_gather_group
    def grad_allreduce(self, optimizer) -> None:
        '''
        Allreduce optimizer grad.

        :param optimizer: optimizer.
        
        Example::

            from pyvqnet.distributed import CommController,get_rank,get_local_rank
            from pyvqnet.tensor import tensor
            from pyvqnet.nn.module import Module
            from pyvqnet.nn.linear import Linear
            from pyvqnet.nn.loss import MeanSquaredError
            from pyvqnet.optim import Adam
            from pyvqnet.nn import activation as F
            import numpy as np
            Comm_OP = CommController("nccl")

            class Net(Module):
                def __init__(self):
                    super(Net, self).__init__()
                    self.fc = Linear(input_channels=5, output_channels=1)
                def forward(self, x):
                    x = F.ReLu()(self.fc(x))
                    return x
                
            model = Net().toGPU(1000+ get_local_rank())
            opti = Adam(model.parameters(), lr=0.01)
            actual = tensor.QTensor([1,1,1,1,1,0,0,0,0,0],dtype=6).reshape((10,1)).toGPU(1000+ get_local_rank())
            x = tensor.randn((10, 5)).toGPU(1000+ get_local_rank())
            for i in range(10):
                opti.zero_grad()
                model.train()
                result = model(x)
                loss = MeanSquaredError()(actual, result)
                loss.backward()
                
                Comm_OP.grad_allreduce(opti)# print(Comm_OP.all_gather(model.parameters()[0]))
                if get_rank() == 0 :
                    print(f"rank {get_rank()} grad is {model.parameters()[0].grad} para {model.parameters()[0]} after")
                opti.step()
            # mpirun -n 2 python test.py
        '''
    def param_allreduce(self, model) -> None:
        '''
        Allreduce model parameters.

        :param model: model.
        
        Example::

            from pyvqnet.distributed import CommController,get_rank,get_local_rank
            from pyvqnet.tensor import tensor
            from pyvqnet.nn.module import Module
            from pyvqnet.nn.linear import Linear
            from pyvqnet.nn import activation as F
            import numpy as np
            Comm_OP = CommController("nccl")

            class Net(Module):
                def __init__(self):
                    super(Net, self).__init__()
                    self.fc = Linear(input_channels=5, output_channels=1)
                def forward(self, x):
                    x = F.ReLu()(self.fc(x))
                    return x
                
            model = Net().toGPU(1000+ get_local_rank())
            print(f"rank {get_rank()} parameters is {model.parameters()}")
            Comm_OP.param_allreduce(model)
                
            if get_rank() == 0:
                print(model.parameters())
        '''
    def broadcast_model_params(self, model, root: int = 0) -> None:
        '''
        Broadcast model parameter from a specified process to all process.
        
        :param: model: `Module`.
        :param: root: the specified rank.
        
        Example::
        
            from pyvqnet.distributed import CommController,get_rank,get_local_rank
            from pyvqnet.tensor import tensor
            from pyvqnet.nn.module import Module
            from pyvqnet.nn.linear import Linear
            from pyvqnet.nn import activation as F
            import numpy as np
            Comm_OP = CommController("nccl")

            class Net(Module):
                def __init__(self):
                    super(Net, self).__init__()
                    self.fc = Linear(input_channels=5, output_channels=1)
                def forward(self, x):
                    x = F.ReLu()(self.fc(x))
                    return x
                
            model = Net().toGPU(1000+ get_local_rank())
            print(f"bcast before rank {get_rank()}:{model.parameters()}")
            Comm_OP.broadcast_model_params(model, 0)
            # model = model
            print(f"bcast after rank {get_rank()}: {model.parameters()}")
        
        '''
    def acc_allreduce(self, acc):
        '''
        Allreduce model accuracy.
        
        :param: acc: model accuracy.
        
        Example::
        
            from pyvqnet.distributed import CommController,get_rank,get_local_rank
            from pyvqnet.tensor import tensor
            from pyvqnet.nn.module import Module
            from pyvqnet.nn.linear import Linear
            from pyvqnet.nn.loss import MeanSquaredError
            from pyvqnet.optim import Adam
            from pyvqnet.nn import activation as F
            import numpy as np
            Comm_OP = CommController("nccl")

            def get_accuary(result, label):
                result = (result > 0.5).astype(4)
                score = tensor.sums(result == label)
                return score

            class Net(Module):
                def __init__(self):
                    super(Net, self).__init__()
                    self.fc = Linear(input_channels=5, output_channels=1)
                def forward(self, x):
                    x = F.ReLu()(self.fc(x))
                    return x
            model = Net().toGPU(1000+ get_local_rank())
            opti = Adam(model.parameters(), lr=0.01)
            actual = tensor.QTensor([1,1,1,1,1,0,0,0,0,0],dtype=6).reshape((10,1)).toGPU(1000+ get_local_rank())
            x = tensor.randn((10, 5)).toGPU(1000+ get_local_rank())
            accuary = 0
            count = 0
            for i in range(100):
                opti.zero_grad()
                model.train()
                result = model(x)
                loss = MeanSquaredError()(actual, result)
                loss.backward()
                opti.step()
                
                count += 1
                accuary += get_accuary(result, actual.reshape([-1,1]))
            print(
                    f"rank {get_rank()} #####accuray:{accuary/count} #### {Comm_OP.acc_allreduce(accuary)/count}"
                )
        '''
    def __del__(self) -> None: ...

class CommController(_CommController):
    '''
    CommController: A class for generating distributed computing communications controller.It must be initialized first for
    default `pyvqnet` backend when using apis in pyvqnet.distributed.

    :param backend: Create a cpu(mpi) or gpu(nccl) communication controller,default:"mpi".
        If set_backend(`torch`), this argument can be `gloo`,`nccl`.
        If set_backend(`pyvqnet`), this argument can be `mpi`,`nccl`.
    :param rank: Rank of the current process,default:None.Required if set_backend(`torch`).
    :param world_size: Number of processes participating in the job.default:None.Required if set_backend(`torch`).
    :return: A CommController instance.
    
    Example::

        from pyvqnet.distributed import CommController
        Comm_OP = CommController("nccl") # init nccl controller
    '''
    def __init__(self, backend: str = 'mpi', rank=None, world_size=None) -> None: ...
