from enum import Enum
from pyvqnet import tensor as tensor

class Format(str, Enum):
    NCHW = 'NCHW'
    NHWC = 'NHWC'
    NCL = 'NCL'
    NLC = 'NLC'
FormatT = str | Format

def get_spatial_dim(fmt: FormatT): ...
def get_channel_dim(fmt: FormatT): ...
def nchw_to(x: tensor.QTensor, fmt: Format): ...
def nhwc_to(x: tensor.QTensor, fmt: Format): ...
