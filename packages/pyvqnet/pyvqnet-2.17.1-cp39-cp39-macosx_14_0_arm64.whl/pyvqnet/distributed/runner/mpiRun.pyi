from _typeshed import Incomplete
from pyvqnet.distributed.runner.common.util import hosts as hosts, safe_shell_exec as safe_shell_exec, tiny_shell_exec as tiny_shell_exec

def mpi_available(env: Incomplete | None = None): ...
def is_mpich(env: Incomplete | None = None): ...
def mpi_run(settings, nics, env, command, stdout: Incomplete | None = None, stderr: Incomplete | None = None) -> None:
    """
    Runs mpi_run.

    Args:
        settings: Settings for running MPI.
                  Note: settings.num_proc and settings.hosts must not be None.
        nics: Interfaces to include by MPI.
        env: Environment dictionary to use for running command.
        command: Command and arguments to run as a list of string.
        stdout: Stdout of the mpi process.
                Only used when settings.run_func_mode is True.
        stderr: Stderr of the mpi process.
                Only used when settings.run_func_mode is True.
    """
