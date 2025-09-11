from _typeshed import Incomplete
from pyvqnet.distributed.runner.common.util import hosts as hosts, safe_shell_exec as safe_shell_exec, timeout as timeout
from pyvqnet.distributed.runner.common.utils import mpi_built as mpi_built, nccl_built as nccl_built
from pyvqnet.distributed.runner.mpiRun import mpi_run as mpi_run
from pyvqnet.distributed.runner.util import cache as cache, network as network, threads as threads
from pyvqnet.distributed.runner.util.remote import get_remote_command as get_remote_command

CACHE_FOLDER: Incomplete
CACHE_STALENESS_THRESHOLD_MINUTES: int
SSH_ATTEMPTS: int
SSH_CONNECT_TIMEOUT_S: int

def check_build(verbose): ...
def make_check_build_action(np_arg): ...
def parse_args(): ...
def run_controller(mpi_run, verbosity) -> None: ...
def run_commandline() -> None: ...
