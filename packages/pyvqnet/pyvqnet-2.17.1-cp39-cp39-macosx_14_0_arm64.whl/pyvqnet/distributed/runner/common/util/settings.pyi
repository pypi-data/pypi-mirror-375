from _typeshed import Incomplete

class BaseSettings:
    num_proc: Incomplete
    verbose: Incomplete
    ssh_port: Incomplete
    ssh_identity_file: Incomplete
    extra_mpi_args: Incomplete
    tcp_flag: Incomplete
    binding_args: Incomplete
    key: Incomplete
    start_timeout: Incomplete
    output_filename: Incomplete
    run_func_mode: Incomplete
    nics: Incomplete
    elastic: Incomplete
    prefix_output_with_timestamp: Incomplete
    def __init__(self, num_proc: Incomplete | None = None, verbose: int = 0, ssh_port: Incomplete | None = None, ssh_identity_file: Incomplete | None = None, extra_mpi_args: Incomplete | None = None, tcp_flag: Incomplete | None = None, binding_args: Incomplete | None = None, key: Incomplete | None = None, start_timeout: Incomplete | None = None, output_filename: Incomplete | None = None, run_func_mode: Incomplete | None = None, nics: Incomplete | None = None, elastic: bool = False, prefix_output_with_timestamp: bool = False) -> None:
        """
        :param num_proc: number of vqnet processes (-np)
        :type num_proc: int
        :param verbose: level of verbosity
        :type verbose: int
        :param ssh_port: SSH port on all the hosts
        :type ssh_port: int
        :param ssh_identity_file: SSH identity (private key) file
        :type ssh_identity_file: string
        :param extra_mpi_args: Extra MPI arguments to pass to mpirun
        :type extra_mpi_args: string
        :param tcp_flag: TCP only communication flag
        :type tcp_flag: boolean
        :param binding_args: Process binding arguments
        :type binding_args: string
        :param key: used for encryption of parameters passed across the hosts
        :type key: str
        :param start_timeout: has to finish all the checks before this timeout runs out.
        :type start_timeout: vqnet.runner.common.util.timeout.Timeout
        :param output_filename: optional filename to redirect stdout / stderr by process
        :type output_filename: string
        :param run_func_mode: whether it is run function mode
        :type run_func_mode: boolean
        :param nics: specify the NICs to be used for tcp network communication.
        :type nics: Iterable[str]
        :param elastic: enable elastic auto-scaling and fault tolerance mode
        :type elastic: boolean
        :param prefix_output_with_timestamp: shows timestamp in stdout/stderr forwarding on the driver
        :type prefix_output_with_timestamp: boolean
        """

class Settings(BaseSettings):
    hosts: Incomplete
    def __init__(self, hosts: Incomplete | None = None, **kwargs) -> None:
        """
        :param hosts: string, comma-delimited, of hostname[s] with slots number[s]
        :type hosts: string
        """
