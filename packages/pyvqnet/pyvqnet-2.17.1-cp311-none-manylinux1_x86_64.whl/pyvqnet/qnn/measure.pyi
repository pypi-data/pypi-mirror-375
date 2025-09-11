__all__ = ['expval', 'QuantumMeasure', 'ProbsMeasure']

def expval(machine, prog, pauli_str_dict: dict, qlists): ...
ExpVal = expval
QuantumMeasure = quantum_measure
ProbsMeasure = probs_measure
