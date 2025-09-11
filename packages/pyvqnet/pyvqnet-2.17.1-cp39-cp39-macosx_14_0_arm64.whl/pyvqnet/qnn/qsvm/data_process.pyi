def load_data(filename, with_lable: bool = False, dtype=..., delimiter: str = ',', comments: str = '#', skiprows: int = 1):
    """
    Import data (with labels)
    
    :param filename: file name
    :param dtype: data type
    :param delimiter: delimiter,default: ','
    :param with_lable:if data has labels.default: False
    :param comments:comments.default: '#'
    :param skiprows: skip rows numbers,default 1,skip first line.
    :return:
        data(array):data feature
        lable(array):data labels
    """
def input_normalize(vector_x): ...
def data_process(x, positive: int = 1, norm_method: str = 'maxnorm'):
    """
    Perform preprocessing on the feature data vectors of the training set and test set that can be encoded by quantum states
    Args:
        x: feature data vector
        positive: whether to map the original data to the first quadrant
        norm_method: normalization processing method
             'maxnorm': The vector is dimensionally increased, adding a new dimension so that the square sum of the new vector is the sum of the squares of the vector with the largest square sum in the original vector list, and then normalized
             'general': normalize directly
             Floating point number: The vector is dimensionally increased, adding a new dimension so that the square sum of the new vector is the input floating point number, and then normalized
    Returns:
        x: normalized x
    """
