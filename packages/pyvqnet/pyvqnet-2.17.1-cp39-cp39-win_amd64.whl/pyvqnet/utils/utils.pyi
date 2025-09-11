import numpy as np
from _typeshed import Incomplete
from collections import abc as abc
from importlib import import_module as import_module
from inspect import getfullargspec as getfullargspec, ismodule as ismodule

to_1tuple: Incomplete
to_2tuple: Incomplete
to_3tuple: Incomplete
to_4tuple: Incomplete
to_ntuple: Incomplete

def default_noise_config(qvm, q):
    """
    default noise model config for NoiseQuantumLayer
    """
def validate_compatible_grad(g: list[float] | np.ndarray | float | None): ...
def validate_compatible_output(output_data, batch_or_not: False):
    """
    convert output to vqnet comatible format
    """
def validate_compatible_input(input_data):
    """
    convert input
    """
def get_circuit_symbols(circuit):
    """Returns a list of the sympy.Symbols that are present in `circuit`.

    Args:
        circuit: A `cirq.Circuit` object.

    Returns:
        Python `list` containing the symbols found in the circuit.

    Raises:
        TypeError: If `circuit` is not of type `cirq.Circuit`.
    """
def bind_cirq_symbol(arry_like, symbols_list):
    """
    bind cirq paramters with value
    """
def merge_cirq_paramsolver(pr1, pr2):
    """
    merge two paramsolvers
    """
def pair(x): ...
def get_conv_outsize(input_size, kernel_size, stride, pad): ...
def get_deconv_outsize(size, k, s, p): ...
def unwrap_padding(x, padding): ...
def transpose_kernel(kernel): ...
def normalize(x, axis: int = -1, order: int = 2):
    """ Normalize the dataset X """
def compare_torch_result(vqnet_rlt, torch_rlt, rtol: float = 1e-05, atol: float = 1e-05): ...
