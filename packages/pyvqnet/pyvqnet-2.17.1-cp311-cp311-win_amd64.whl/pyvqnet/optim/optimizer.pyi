from ..backends import check_not_default_backend as check_not_default_backend, get_backend as get_backend
from ..tensor import DEV_CPU as DEV_CPU, DEV_GPU_0 as DEV_GPU_0, QTensor as QTensor, no_grad as no_grad, to_tensor as to_tensor
from _typeshed import Incomplete
from collections import OrderedDict as OrderedDict

class _RequiredParameter:
    """Singleton class representing a required parameter for an Optimizer."""

required: Incomplete

class Optimizer:
    """
    Base class for all optimizers.

    :param params: params of model which need to be optimized
    :param lr: learning_rate of model (default: 0.01)
    """
    params: Incomplete
    lr: Incomplete
    defaults: Incomplete
    state: Incomplete
    param_groups: Incomplete
    def __init__(self, params, lr: float = 0.1, defaults={}) -> None: ...
    def step(self) -> None: ...
    def zero_grad(self, set_to_none: bool = False): ...
    def add_param_group(self, param_group) -> None:
        """Add a param group to the :class:`Optimizer` s `param_groups`.

        This can be useful when fine tuning a pre-trained network as frozen layers can be made
        trainable and added to the :class:`Optimizer` as training progresses.

        Args:
            param_group (dict): Specifies what Tensors should be optimized along with group
                specific optimization options.
        """
    def state_dict(self):
        """Returns the state of the optimizer as a :class:`dict`.

        It contains two entries:

        * state - a dict holding current optimization state. Its content
            differs between optimizer classes.
        * param_groups - a list containing all parameter groups where each
            parameter group is a dict
        """
    def load_state_dict(self, state_dict):
        """Loads the optimizer state.

        Args:
            state_dict (dict): optimizer state. Should be an object returned
                from a call to :meth:`state_dict`.
        """
