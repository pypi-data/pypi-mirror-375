"""
Init for qnn
"""
# pylint: disable=redefined-builtin

from .quantumlayer import NoiseQuantumLayer,QuantumLayer,QuantumLayerWithQProg,\
    QuantumLayerMultiProcess,QuantumLayerV2,grad,\
         QuantumBatchAsyncQcloudLayer, QuantumBatchAsyncQcloudLayerES, \
        QuantumLayerV3,\
        QpandaQCircuitVQCLayer,QpandaQCircuitVQCLayerLite,QpandaQProgVQCLayer


from .template import AmplitudeEmbeddingCircuit,AngleEmbeddingCircuit,\
        RotCircuit,StronglyEntanglingTemplate, BasicEntanglerTemplate
        
from . import pqc, qae, qdrl, qgan, qlinear, qcnn, qvc, utils, svm, qp, qlstm, qmlp, qrnn
from .opt import SPSA, insert_pauli_for_mt, get_metric_tensor, Gradient_Prune_Instance, quantum_fisher
from .pq3 import Quantum_Embedding,FermionicSimulationGate,QuantumPoolingCircuit,\
    ComplexEntangelingTemplate,BasisState,HybirdVQCQpandaQVMLayer
 

from .pq_utils import PQ_QCLOUD_UTILS
from .measure import expval, expval_qcloud, ProbsMeasure,QuantumMeasure,\
    DensityMatrixFromQstate,VN_Entropy,Mutal_Info,Hermitian_expval,Purity
