from .cons import (
    backend,
    set_backend,
    set_dtype,
    set_contractor,
    get_backend,
    get_dtype,
    get_contractor,
    set_function_backend,
    set_function_dtype,
    set_function_contractor,
    runtime_backend,
    runtime_dtype,
    runtime_contractor,
)  # prerun of set hooks

from . import gates
from . import basecircuit
from .gates import Gate
from .circuit import Circuit, expectation
from .mpscircuit import MPSCircuit
from .densitymatrix import DMCircuit as DMCircuit_reference
from .densitymatrix import DMCircuit2

DMCircuit = DMCircuit2  # compatibility issue to still expose DMCircuit2
from .gates import num_to_tensor, array_to_tensor

from . import interfaces

from . import quantum
from .quantum import QuOperator, QuVector, QuAdjointVector, QuScalar
from .utils import get_expectation,run_prob_list,get_expectation_real, get_sample

set_backend("torch")