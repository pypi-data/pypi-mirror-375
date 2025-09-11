from pyvqnet.utils.utils import get_conv_outsize as get_conv_outsize, pair as pair, unwrap_padding as unwrap_padding

def deconv2d(x, kernel, pad=(0, 0), invert: bool = False): ...
def col2im_array(col, img_shape, kernel_size, stride: int = 1, pad: int = 0, to_matrix: bool = False):
    """
    Implements the col to image tools

    ## Parameters
    col: the convolution of image
    img_shape: the shape of image and the shape is N * C * H * W
    kernel_size: the filter size and the shape is KH * KW
    stride: the length of one step and the shape is SH * SW
    pad: pad with 0 and the shape is PH * PW
    to_matrix: convert or not into matrix
    """
def im2col_array(img, kernel_size, stride: int = 1, pad: int = 0, to_matrix: bool = False):
    """
    Implements the image to col tools

    ## Parameters
    img: the input img and the shape is N * C * H * W
    kernel_size: the filter and the shape is KH * KW
    stride: the length of one step and the shape is SH * SW
    pad: pad with 0 and the shape is PH * PW
    to_matrix: convert or not into matrix
    """
