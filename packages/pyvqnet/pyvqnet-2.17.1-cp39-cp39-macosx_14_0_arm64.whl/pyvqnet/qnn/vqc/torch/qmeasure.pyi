from ....dtype import C_DTYPE as C_DTYPE, kcomplex64 as kcomplex64
from ....nn.torch import TorchModule as TorchModule
from ..qmeasure import HermitianExpval as NHermitianExpval, MeasureAll as NMeasureAll, Probability as NProbability, Samples as NSamples, VQC_DensityMatrixFromQstate as VQC_DensityMatrixFromQstate, VQC_Purity as VQC_Purity, VQC_VarMeasure as VQC_VarMeasure
from .utils import complex_dtype_to_float_dtype as complex_dtype_to_float_dtype
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
