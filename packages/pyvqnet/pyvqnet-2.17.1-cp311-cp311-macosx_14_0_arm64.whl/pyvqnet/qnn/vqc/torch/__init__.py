from .qop import QModule, StateEncoder,QMachine
from .qcircuit import *
from .qmeasure import MeasureAll,Probability,\
    Samples,HermitianExpval,\
    VQC_Purity,VQC_DensityMatrixFromQstate,VQC_VarMeasure
from ...pq3.torch.qpanda_layer import TorchQpandaQuantumLayer,TorchQcloudQuantumLayer 
from .ddp import TorchDataParalledVQCLayer
from .adjoint_grad import QuantumLayerAdjoint
from ...pq3.torch.qpanda3_layer import HybirdVQCQpanda3QVMLayer ,\
    TorchQpanda3QuantumLayer,TorchQcloud3QuantumLayer,TorchHybirdVQCQpanda3QVMLayer,\
        TorchVQCQpandaForwardLayer, Qpanda3AdjointGradientQuantumLayer
