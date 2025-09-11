from .quantumlayer import QpandaQCircuitVQCLayerLite,\
    QpandaQProgVQCLayer,QuantumBatchAsyncQcloudLayer,QuantumLayer,QuantumLayerV2,QuantumLayerV3,\
        grad,QuantumLayerAdjoint
from .measure import probs_measure,ProbsMeasure,quantum_measure,QuantumMeasure,\
    expval,expval_qcloud
from .ansatz import HardwareEfficientAnsatz
from .qembed import Quantum_Embedding
from .template import ComplexEntangelingTemplate,StronglyEntanglingTemplate,\
    BasicEntanglerTemplate,CRotCircuit,IQPEmbeddingCircuits,RandomTemplate,\
        SimplifiedTwoDesignTemplate,Controlled_Hadamard,CCZ,\
            FermionicSingleExcitation,FermionicDoubleExcitation,UCCSD,AngleEmbeddingCircuit,\
                BasicEmbeddingCircuit,CSWAPcircuit,RotCircuit,QuantumPoolingCircuit,\
                    FermionicSimulationGate,RandomTemplate,SimplifiedTwoDesignTemplate,\
                        UCCSD,BasisState
from .hybird_vqc_qpanda import HybirdVQCQpandaQVMLayer,VQCQpandaForwardLayer,HybirdVQCQpanda3QVMLayer