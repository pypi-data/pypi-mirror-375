from ..tensor import zeros as zeros
from _typeshed import Incomplete

BUCKET_SIZE_FOR_GRADIENTS_ALLREDUCE: Incomplete

def tensor_all_reduce(Comm, large_tensor) -> None: ...
def post_grad_all_reduce(all_parameters):
    """
    create gradients for all paramters and use slice as each paramters' gradients.
    """
def all_grad_all_reduce(Comm, all_grad) -> None: ...
