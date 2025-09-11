import tensornetwork as tn
from typing import Any

def infer_new_size(a: tn.Node, b: tn.Node, include_old: bool = True) -> Any: ...
def infer_new_shape(a: tn.Node, b: tn.Node, include_old: bool = True) -> Any:
    """
    Get the new shape of two nodes, also supporting to return original shapes of two nodes.

    :Example:

    >>> a = tn.Node(np.ones([2, 3, 5]))
    >>> b = tn.Node(np.ones([3, 5, 7]))
    >>> a[1] ^ b[0]
    >>> a[2] ^ b[1]
    >>> tc.simplify.infer_new_shape(a, b)
    >>> ((2, 7), (2, 3, 5), (3, 5, 7))
    >>> # (shape of a, shape of b, new shape)

    :param a: node one
    :type a: tn.Node
    :param b: node two
    :type b: tn.Node
    :param include_old: Whether to include original shape of two nodes, default is True.
    :type include_old: bool
    :return: The new shape of the two nodes.
    :rtype: Union[Tuple[int, ...], Tuple[Tuple[int, ...], Tuple[int, ...], Tuple[int, ...]]]
    """
def pseudo_contract_between(a: tn.Node, b: tn.Node, **kws: Any) -> tn.Node:
    """
    Contract between Node ``a`` and ``b``, with correct shape only and no calculation

    :param a: [description]
    :type a: tn.Node
    :param b: [description]
    :type b: tn.Node
    :return: [description]
    :rtype: tn.Node
    """
