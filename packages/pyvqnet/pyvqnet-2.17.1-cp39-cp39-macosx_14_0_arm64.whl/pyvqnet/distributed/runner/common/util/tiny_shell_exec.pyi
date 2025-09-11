from _typeshed import Incomplete
from pyvqnet.distributed.runner.common.util import safe_shell_exec as safe_shell_exec

def execute(command, env: Incomplete | None = None):
    """
    Executes the command and returns stdout and stderr as a string, together with the exit code.
    :param command: command to execute
    :param env: environment variables to use
    :return: (output, exit code) or None on failure
    """
