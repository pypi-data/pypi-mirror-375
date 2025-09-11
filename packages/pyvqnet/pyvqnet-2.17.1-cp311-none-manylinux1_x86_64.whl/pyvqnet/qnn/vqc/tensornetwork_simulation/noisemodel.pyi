import tensornetwork as tn
from . import Circuit as Circuit, DMCircuit as DMCircuit, gates as gates
from .abstractcircuit import AbstractCircuit as AbstractCircuit
from .channels import KrausList as KrausList, composedkraus as composedkraus
from .cons import backend as backend
from _typeshed import Incomplete
from typing import Any, Sequence

Gate = gates.Gate
Tensor = Any
logger: Incomplete

class NoiseConf:
    '''
    ``Noise Configuration`` class.

    .. code-block:: python

        error1 = tc.channels.generaldepolarizingchannel(0.1, 1)
        error2 = tc.channels.thermalrelaxationchannel(300, 400, 100, "ByChoi", 0)
        readout_error = [[0.9, 0.75], [0.4, 0.7]]

        noise_conf = NoiseConf()
        noise_conf.add_noise("x", error1)
        noise_conf.add_noise("h", [error1, error2], [[0], [1]])
        noise_conf.add_noise("readout", readout_error)
    '''
    nc: Incomplete
    has_quantum: bool
    has_readout: bool
    def __init__(self) -> None:
        """
        Establish a noise configuration.
        """
    def add_noise(self, gate_name: str, kraus: Sequence[KrausList], qubit: Sequence[Any] | None = None) -> None:
        """
        Add noise channels on specific gates and specific qubits in form of Kraus operators.

        :param gate_name: noisy gate
        :type gate_name: str
        :param kraus: noise channel
        :type kraus: Sequence[Gate]
        :param qubit: the list of noisy qubit, defaults to None, indicating applying the noise channel on all qubits
        :type qubit: Optional[Sequence[Any]], optional
        """

def apply_qir_with_noise(c: Any, qir: list[dict[str, Any]], noise_conf: NoiseConf, status: Tensor | None = None) -> Any:
    """

    :param c: A newly defined circuit
    :type c: AbstractCircuit
    :param qir: The qir of the clean circuit
    :type qir: List[Dict[str, Any]]
    :param noise_conf: Noise Configuration
    :type noise_conf: NoiseConf
    :param status: The status for Monte Carlo sampling, defaults to None
    :type status: 1D Tensor, optional
    :return: A newly constructed circuit with noise
    :rtype: AbstractCircuit
    """
def circuit_with_noise(c: AbstractCircuit, noise_conf: NoiseConf, status: Tensor | None = None) -> Any:
    """Noisify a clean circuit.

    :param c: A clean circuit
    :type c: AbstractCircuit
    :param noise_conf: Noise Configuration
    :type noise_conf: NoiseConf
    :param status: The status for Monte Carlo sampling, defaults to None
    :type status: 1D Tensor, optional
    :return: A newly constructed circuit with noise
    :rtype: AbstractCircuit
    """
def sample_expectation_ps_noisfy(c: Any, x: Sequence[int] | None = None, y: Sequence[int] | None = None, z: Sequence[int] | None = None, noise_conf: NoiseConf | None = None, nmc: int = 1000, shots: int | None = None, statusc: Tensor | None = None, status: Tensor | None = None, **kws: Any) -> Tensor:
    """
    Calculate sample_expectation_ps with noise configuration.

    :param c: The clean circuit
    :type c: Any
    :param x: sites to apply X gate, defaults to None
    :type x: Optional[Sequence[int]], optional
    :param y: sites to apply Y gate, defaults to None
    :type y: Optional[Sequence[int]], optional
    :param z: sites to apply Z gate, defaults to None
    :type z: Optional[Sequence[int]], optional
    :param noise_conf: Noise Configuration, defaults to None
    :type noise_conf: Optional[NoiseConf], optional
    :param nmc: repetition time for Monte Carlo sampling  for noisfy calculation, defaults to 1000
    :type nmc: int, optional
    :param shots: number of measurement shots, defaults to None, indicating analytical result
    :type shots: Optional[int], optional
    :param statusc: external randomness given by tensor uniformly from [0, 1], defaults to None,
        used for noisfy circuit sampling
    :type statusc: Optional[Tensor], optional
    :param status: external randomness given by tensor uniformly from [0, 1], defaults to None,
        used for measurement sampling
    :type status: Optional[Tensor], optional
    :return: sample expectation value with noise
    :rtype: Tensor
    """
def expectation_noisfy(c: Any, *ops: tuple[tn.Node, list[int]], noise_conf: NoiseConf | None = None, nmc: int = 1000, status: Tensor | None = None, **kws: Any) -> Tensor:
    """
    Calculate expectation value with noise configuration.

    :param c: The clean circuit
    :type c: Any
    :param noise_conf: Noise Configuration, defaults to None
    :type noise_conf: Optional[NoiseConf], optional
    :param nmc: repetition time for Monte Carlo sampling for noisfy calculation, defaults to 1000
    :type nmc: int, optional
    :param status: external randomness given by tensor uniformly from [0, 1], defaults to None,
        used for noisfy circuit sampling
    :type status: Optional[Tensor], optional
    :return: expectation value with noise
    :rtype: Tensor
    """
