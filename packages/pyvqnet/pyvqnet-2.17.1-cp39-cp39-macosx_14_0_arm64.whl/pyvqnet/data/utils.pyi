from _typeshed import Incomplete
from collections import defaultdict as defaultdict

MP_STATUS_CHECK_INTERVAL: float
python_exit_status: bool
HAS_NUMPY: bool

class KeyErrorMessage(str):
    """str subclass that returns itself in repr"""

class ExceptionWrapper:
    """Wraps an exception plus traceback to communicate across threads"""
    exc_type: Incomplete
    exc_msg: Incomplete
    where: Incomplete
    def __init__(self, exc_info: Incomplete | None = None, where: str = 'in background') -> None: ...
    def reraise(self) -> None:
        """Reraises the wrapped exception in the current thread"""
