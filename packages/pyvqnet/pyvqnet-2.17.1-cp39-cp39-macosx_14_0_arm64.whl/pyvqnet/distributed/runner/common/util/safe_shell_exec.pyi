from _typeshed import Incomplete
from pyvqnet.distributed.runner.util.threads import in_thread as in_thread, on_event as on_event

GRACEFUL_TERMINATION_TIME_S: int

def terminate_executor_shell_and_children(pid) -> None: ...
def prefix_connection(src_connection, dst_stream, prefix, index, prefix_output_with_timestamp):
    """
    Prefixes the given source connection with timestamp, a prefix and an index.
    Each line of the source will be prefix in this format, if index and prefix are not None:
        {time}[{index}]<{prefix}>:{line}
    The dst_stream must be text streams.

    :param src_connection: source pipe connection
    :param dst_stream: destination text stream
    :param prefix: prefix string
    :param index: index value
    :param prefix_output_with_timestamp: prefix lines in dst_stream with timestamp
    :return: None
    """
def execute(command, env: Incomplete | None = None, stdout: Incomplete | None = None, stderr: Incomplete | None = None, index: Incomplete | None = None, events: Incomplete | None = None, prefix_output_with_timestamp: bool = False):
    """
    Execute the given command and forward stdout and stderr of the command to the given
    stdout and stderr text streams, or sys.stdout and sys.stderr, respectively, if None given.
    Prefixes each line with index and timestamp if index is not None. The timestamp
    can be disabled with prefix_output_with_timestamp set False.
    The command will be terminated when any of the given events are set.

    :param command: command to execute
    :param env: environment variables to execute command with
    :param stdout: stdout text stream, sys.stdout if None
    :param stderr: stderr text stream, sys.stderr if None
    :param index: index used to prepend text streams
    :param events: events to terminate the command
    :param prefix_output_with_timestamp: prepend text streams with timestamp if True
    :return: command's exit code
    """
