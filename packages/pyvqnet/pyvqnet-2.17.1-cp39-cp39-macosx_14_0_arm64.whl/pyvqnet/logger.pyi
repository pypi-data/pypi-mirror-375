from _typeshed import Incomplete

should_pyvqnet_use_this_log: bool

def get_should_pyvqnet_use_this_log(): ...
def set_should_pyvqnet_use_this_log(flag) -> None: ...

log_levels: Incomplete

class LoggerFactory:
    @staticmethod
    def create_logger(name: Incomplete | None = None, level=...):
        """create a logger

        Args:
            name (str): name of the logger
            level: level of logger

        Raises:
            ValueError is name is None
        """

logger: Incomplete

def warning_once(*args, **kwargs) -> None:
    """
    This method is identical to `logger.warning()`, but will emit the warning with the same message only once

    Note: The cache is for the function arguments, so 2 different callers using the same arguments will hit the cache.
    The assumption here is that all warning messages are unique across the code. If they aren't then need to switch to
    another type of cache that includes the caller frame information in the hashing function.
    """
def print_configuration(args, name) -> None: ...
def log_dist(message, ranks: Incomplete | None = None, level=...) -> None:
    """Log message when one of following condition meets

    + not dist.is_initialized()
    + dist.get_rank() in ranks if ranks is not None or ranks = [-1]

    Args:
        message (str)
        ranks (list)
        level (int)

    """
def print_json_dist(message, ranks: Incomplete | None = None, path: Incomplete | None = None) -> None:
    """Print message when one of following condition meets

    + not dist.is_initialized()
    + dist.get_rank() in ranks if ranks is not None or ranks = [-1]

    Args:
        message (str)
        ranks (list)
        path (str)

    """
def get_current_level():
    """
    Return logger's current log level
    """
def should_log_le(max_log_level_str):
    '''
    Args:
        max_log_level_str: maximum log level as a string

    Returns ``True`` if the current log_level is less or equal to the specified log level. Otherwise ``False``.

    Example:

        ``should_log_le("info")`` will return ``True`` if the current log level is either ``logging.INFO`` or ``logging.DEBUG``
    '''
