from ....nn.torch import TorchModule as TorchModule
from ....tensor import QTensor as QTensor
from ..qmeasure import HermitianExpval as NHermitianExpval, MeasureAll as NMeasureAll, Probability as NProbability, Samples as NSamples, VQC_VarMeasure as VQC_VarMeasure
from _typeshed import Incomplete
from pyvqnet.backends_mock import TorchMock as TorchMock

class HermitianExpval(TorchModule, NHermitianExpval):
    def __init__(self, obs, name: str = '') -> None: ...

class MeasureAll(TorchModule, NMeasureAll):
    def __init__(self, obs, name: str = '') -> None: ...

class Probability(TorchModule, NProbability):
    def __init__(self, wires, name: str = '') -> None: ...

class Samples(TorchModule, NSamples):
    def __init__(self, wires: Incomplete | None = None, obs: Incomplete | None = None, shots: int = 1, name: str = '') -> None: ...

def VQC_Purity(state, qubits_idx, num_wires, use_tn: bool = False): ...
def VQC_DensityMatrixFromQstate(state, indices, use_tn: bool = False): ...
