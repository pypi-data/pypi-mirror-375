from _typeshed import Incomplete
from typing import Any

__all__ = ['RemovableHandle']

class RemovableHandle:
    """
    A handle which provides the capability to remove a hook.

    Args:
        hooks_dict (dict): A dictionary of hooks, indexed by hook ``id``.
        extra_dict (Union[dict, List[dict]]): An additional dictionary or list of
            dictionaries whose keys will be deleted when the same keys are
            removed from ``hooks_dict``.
    """
    id: int
    next_id: int
    hooks_dict_ref: Incomplete
    extra_dict_ref: Incomplete
    def __init__(self, hooks_dict: Any, *, extra_dict: Any = None) -> None: ...
    def remove(self) -> None: ...
    def __enter__(self) -> RemovableHandle: ...
    def __exit__(self, type: Any, value: Any, tb: Any) -> None: ...
