from ... import tensor as tensor
from ...tensor import QTensor as QTensor
from _typeshed import Incomplete

def forward_tn_wrapper(qop, q_machine, unsqueeze_params) -> None: ...

gate_map: Incomplete
op_map: Incomplete

def quantum_gate_op_tn(q_machine, params, wires, name, use_dagger) -> None: ...
