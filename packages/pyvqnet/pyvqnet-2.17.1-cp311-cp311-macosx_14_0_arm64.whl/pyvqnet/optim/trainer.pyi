import pyvqnet.nn as nn
from .utils import clip_grad_norm_ as clip_grad_norm_
from _typeshed import Incomplete
from abc import ABCMeta, abstractmethod
from pyvqnet.data import data_generator as data_generator
from pyvqnet.optim import Adam as Adam, AdamW as AdamW, Adamax as Adamax, RMSProp as RMSProp, SGD as SGD
from pyvqnet.optim.optimizer import Optimizer as Optimizer
from pyvqnet.tensor import QTensor as QTensor, tensor as tensor

vqnet: Incomplete
INF: Incomplete

def build_optim_wrapper(model: nn.Module, cfg: dict):
    """Build function of OptimWrapper.

    If ``constructor`` is set in the ``cfg``, this method will build an
    optimizer wrapper constructor, and use optimizer wrapper constructor to
    build the optimizer wrapper. If ``constructor`` is not set, the
    ``DefaultOptimWrapperConstructor`` will be used by default.

    :param model (nn.Module): Model to be optimized.
    :param cfg (dict): Config of optimizer wrapper, optimizer constructor and
            optimizer.

    Returns:
        OptimWrapper: The built optimizer wrapper.
    """

optim_str_cls_map: Incomplete

class DefaultOptimWrapperConstructor:
    """
    
    """
    optim_wrapper_cfg: Incomplete
    optimizer_cfg: Incomplete
    paramwise_cfg: Incomplete
    base_lr: Incomplete
    base_wd: Incomplete
    def __init__(self, optim_wrapper_cfg: dict, paramwise_cfg: dict | None = None) -> None: ...
    def add_params(self, params: list[dict], module: nn.Module, prefix: str = '', is_dcn_module: int | float | None = None) -> None: ...
    def __call__(self, model: nn.Module): ...

class BaseOptimWrapper(metaclass=ABCMeta):
    optimizer: Incomplete
    base_param_settings: Incomplete
    def __init__(self, optimizer) -> None: ...
    @abstractmethod
    def update_params(self, *args, **kwargs):
        """Update parameters in :attr:`optimizer`."""
    @abstractmethod
    def backward(self, loss, **kwargs) -> None:
        """Perform gradient back propagation."""
    @abstractmethod
    def zero_grad(self, **kwargs) -> None:
        """A wrapper of ``Optimizer.zero_grad``."""
    @abstractmethod
    def step(self, **kwargs):
        """Call the step method of optimizer."""
    def state_dict(self) -> dict:
        """A wrapper of ``Optimizer.state_dict``."""
    def load_state_dict(self, state_dict: dict) -> None:
        """A wrapper of ``Optimizer.load_state_dict``. load the state dict of
        :attr:`optimizer`.

        Provide unified ``load_state_dict`` interface compatible with automatic
        mixed precision training. Subclass can overload this method to
        implement the required logic.

        Args:
            state_dict (dict): The state dictionary of :attr:`optimizer`.
        """
    @property
    def param_groups(self) -> list[dict]:
        """A wrapper of ``Optimizer.param_groups``.

        Make OptimizeWrapper compatible with :class:`_ParamScheduler`.

        Returns:
             dict: the ``param_groups`` of :attr:`optimizer`.
        """
    @property
    def defaults(self) -> dict:
        """A wrapper of ``Optimizer.defaults``.

        Make OptimizeWrapper compatible with :class:`_ParamScheduler`.

        Returns:
             dict: the ``param_groups`` of :attr:`optimizer`.
        """
    def get_lr(self):
        """Get the learning rate of the optimizer.

        Provide unified interface to get learning rate of optimizer.

        Returns:
            Dict[str, List[float]]:
            param_groups learning rate of the optimizer.
        """
    def get_momentum(self) -> dict[str, list[float]]:
        """Get the momentum of the optimizer.

        Provide unified interface to get momentum of optimizer.

        Returns:
            Dict[str, List[float]]: Momentum of the optimizer.
        """

class OptimWrapper(BaseOptimWrapper):
    """Optimizer wrapper provides a common interface for updating parameters.

    
    """
    optimizer: Incomplete
    clip_func: Incomplete
    grad_name: str
    clip_grad_kwargs: Incomplete
    base_param_settings: Incomplete
    def __init__(self, optimizer: Optimizer, accumulative_counts: int = 1, clip_grad: dict | None = None) -> None: ...
    def should_update(self) -> bool:
        """Decide whether the parameters should be updated at the current
        iteration.

        Called by :meth:`update_params` and check whether the optimizer
        wrapper should update parameters at current iteration.

        Returns:
            bool: Whether to update parameters.
        """
    def zero_grad(self, **kwargs) -> None:
        """A wrapper of ``Optimizer.zero_grad``.

        """
    def backward(self, loss, **kwargs) -> None:
        """Perform gradient back propagation.

        Note:
            If subclasses inherit from ``OptimWrapper`` override
            ``backward``, ``_inner_count +=1`` must be implemented.

        Args:
            loss (tensor.QTensor): The loss of current iteration.
            kwargs: Keyword arguments passed to :meth:`tensor.QTensor.backward`.
        """
    def update_params(self, loss, step_kwargs: dict | None = None, zero_kwargs: dict | None = None) -> None:
        """Update parameters in :attr:`optimizer`.
        """
    def zero_grad(self, **kwargs) -> None:
        """A wrapper of ``Optimizer.zero_grad``.

        """
    def step(self, **kwargs) -> None:
        """A wrapper of ``Optimizer.step``.


        Clip grad if :attr:`clip_grad_kwargs` is not None, and then update
        parameters.

        :param kwargs: Keyword arguments passed to
                :meth:`optim.Optimizer.step`.
        """
    def initialize_count_status(self, model: nn.Module, init_counts: int, max_counts: int) -> None:
        """Initialize gradient accumulation related attributes.

        ``OptimWrapper`` can be used without calling
        ``initialize_iter_status``. However, Consider the case of  ``len(
        dataloader) == 10``, and the ``accumulative_iter == 3``. Since 10 is
        not divisible by 3, the last iteration will not trigger
        ``optimizer.step()``, resulting in one less parameter updating.

        Args:
            model (nn.Module): Training model
            init_counts (int): The initial value of the inner count.
            max_counts (int): The maximum value of the inner count.
        """

class _ParamScheduler:
    """Base class for parameter schedulers.

    It should be inherited by all schedulers that schedule parameters in the
    optimizer's ``param_groups``. All subclasses should overwrite the
    ``_get_value()`` according to their own schedule strategy.
    The implementation is motivated by
    https://github.com/pytorch/pytorch/blob/master/torch/optim/lr_scheduler.py.

    Args:
        optimizer (BaseOptimWrapper or Optimizer): Wrapped optimizer.
        param_name (str): Name of the parameter to be adjusted, such as
            ``lr``, ``momentum``.
        begin (int): Step at which to start updating the parameters.
            Defaults to 0.
        end (int): Step at which to stop updating the parameters.
            Defaults to INF.
        last_step (int): The index of last step. Used for resuming without
            state dict. Default value ``-1`` means the ``step`` function is
            never be called before. Defaults to -1.
        by_epoch (bool): Whether the scheduled parameters are updated by
            epochs. Defaults to True.
        verbose (bool): Whether to print the value for each update.
            Defaults to False.
    """
    optimizer: Incomplete
    param_name: Incomplete
    begin: Incomplete
    end: Incomplete
    by_epoch: Incomplete
    base_values: Incomplete
    last_step: Incomplete
    verbose: Incomplete
    def __init__(self, optimizer, param_name: str, begin: int = 0, end: int = ..., last_step: int = -1, by_epoch: bool = True, verbose: bool = False) -> None: ...
    def step(self) -> None:
        """Adjusts the parameter value of each parameter group based on the
        specified schedule."""

class LinearParamScheduler(_ParamScheduler):
    """Decays the parameter value of each parameter group by linearly changing
    small multiplicative factor until the number of epoch reaches a pre-defined
    milestone: ``end``.

    Notice that such decay can happen simultaneously with other changes to the
    parameter value from outside this scheduler.

    Args:
        optimizer (Optimizer or BaseOptimWrapper): optimizer or Wrapped
            optimizer.
        param_name (str): Name of the parameter to be adjusted, such as
            ``lr``, ``momentum``.
        start_factor (float): The number we multiply parameter value in the
            first epoch. The multiplication factor changes towards end_factor
            in the following epochs. Defaults to 1./3.
        end_factor (float): The number we multiply parameter value at the end
            of linear changing process. Defaults to 1.0.
        begin (int): Step at which to start updating the parameters.
            Defaults to 0.
        end (int): Step at which to stop updating the parameters.
            Defaults to INF.
        last_step (int): The index of last step. Used for resume without
            state dict. Defaults to -1.
        by_epoch (bool): Whether the scheduled parameters are updated by
            epochs. Defaults to True.
        verbose (bool): Whether to print the value for each update.
            Defaults to False.
    """
    start_factor: Incomplete
    end_factor: Incomplete
    total_iters: Incomplete
    def __init__(self, optimizer: Optimizer | BaseOptimWrapper, param_name: str, start_factor: float = ..., end_factor: float = 1.0, begin: int = 0, end: int = ..., last_step: int = -1, by_epoch: bool = True, verbose: bool = False) -> None: ...

class LinearLR(LinearParamScheduler):
    def __init__(self, optimizer, *args, **kwargs) -> None: ...

class CosineAnnealingParamScheduler(_ParamScheduler):
    T_max: Incomplete
    eta_min: Incomplete
    eta_min_ratio: Incomplete
    def __init__(self, optimizer: Optimizer | BaseOptimWrapper, T_max: int | None = None, eta_min: float | None = None, begin: int = 0, end: int = ..., last_step: int = -1, by_epoch: bool = True, verbose: bool = False, eta_min_ratio: float | None = None) -> None: ...

param_schedulers_dict: Incomplete

class CLS_Runner:
    model: nn.Module
    device: Incomplete
    train_iter: Incomplete
    val_interval: Incomplete
    batch_size: Incomplete
    val_begin: Incomplete
    optim_wrapper: Incomplete
    param_schedulers: Incomplete
    save_dir: Incomplete
    data_process_cfg: Incomplete
    def __init__(self, model, optim_cfg, learning_schedule_cfg, train_val_cfg, data_process_cfg) -> None: ...
    @property
    def max_epochs(self):
        """int: Total epochs to train model."""
    @property
    def max_iters(self):
        """int: Total iterations to train model."""
    @property
    def epoch(self):
        """int: Current epoch."""
    @property
    def iter(self):
        """int: Current iteration."""
    def data_process(self, data, labels, img_size, mean, std, num_classes): ...
    def train(self, train_data, train_labels, eval_data, eval_labels) -> None: ...
    def after_train_iter(self, batch_idx: int) -> None:
        """Call step function for each scheduler after each training iteration.

    
        """
    def after_train_epoch(self) -> None:
        """Call step function for each scheduler after each training epoch.

        Args:
            runner (Runner): The runner of the training process.
        """
    def build_param_scheduler(self, scheduler: dict | list):
        """Build parameter schedulers.
"""
