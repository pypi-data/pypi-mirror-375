from _typeshed import Incomplete
from dataclasses import dataclass

class HostInfo:
    hostname: Incomplete
    slots: Incomplete
    def __init__(self, hostname, slots) -> None: ...
    @staticmethod
    def from_string(host_string): ...

@dataclass
class SlotInfo:
    hostname: str
    rank: int
    local_rank: int
    cross_rank: int
    size: int
    local_size: int
    cross_size: int
    def to_response_string(self): ...
    def __init__(self, hostname, rank, local_rank, cross_rank, size, local_size, cross_size) -> None: ...

def parse_host_files(filename):
    """
    Transform the hostfile into a format of
    <IP address> or <host name>:<Number of GPUs>
    :param filename: Should be in <IP address> or <host name> slots=<number of GPUs>
    :return: Comma separated string of <IP address> or <host name>:<Number of GPUs>
    """
def parse_hosts_and_slots(hosts): ...
