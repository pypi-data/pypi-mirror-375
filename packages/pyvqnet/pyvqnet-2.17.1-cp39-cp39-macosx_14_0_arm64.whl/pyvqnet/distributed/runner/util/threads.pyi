from _typeshed import Incomplete

def execute_function_multithreaded(fn, args_list, block_until_all_done: bool = True, max_concurrent_executions: int = 1000):
    """
    Executes fn in multiple threads each with one set of the args in the
    args_list.
    :param fn: function to be executed
    :type fn:
    :param args_list:
    :type args_list: list(list)
    :param block_until_all_done: if is True, function will block until all the
    threads are done and will return the results of each thread's execution.
    :type block_until_all_done: bool
    :param max_concurrent_executions:
    :type max_concurrent_executions: int
    :return:
    If block_until_all_done is False, returns None. If block_until_all_done is
    True, function returns the dict of results.
        {
            index: execution result of fn with args_list[index]
        }
    :rtype: dict
    """
def in_thread(target, args=(), name: Incomplete | None = None, daemon: bool = True, silent: bool = False):
    """
    Executes the given function in background.
    :param target: function
    :param args: function arguments
    :param name: name of the thread
    :param daemon: run as daemon thread, do not block until thread is doe
    :param silent: swallows exceptions raised by target silently
    :return background thread
    """
def on_event(event, func, args=(), stop: Incomplete | None = None, check_stop_interval_s: float = 1.0, daemon: bool = True, silent: bool = False):
    """
    Executes the given function in a separate thread when event is set.
    That threat can be stopped by setting the optional stop event.
    The stop event is check regularly every check_interval_seconds.
    Exceptions will silently be swallowed when silent is True.

    :param event: event that triggers func
    :type event: threading.Event
    :param func: function to trigger
    :param args: function arguments
    :param stop: event to stop thread
    :type stop: threading.Event
    :param check_stop_interval_s: interval in seconds to check the stop event
    :type check_stop_interval_s: float
    :param daemon: event thread is a daemon thread if set to True, otherwise stop event must be given
    :param silent: swallows exceptions raised by target silently
    :return: thread
    """
