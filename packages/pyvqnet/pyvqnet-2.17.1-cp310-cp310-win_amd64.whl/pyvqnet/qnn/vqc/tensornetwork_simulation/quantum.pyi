from .backends import get_backend as get_backend
from .cons import backend as backend, contractor as contractor, dtypestr as dtypestr, npdtype as npdtype, rdtypestr as rdtypestr
from .utils import arg_alias as arg_alias, is_m1mac as is_m1mac
from _typeshed import Incomplete
from tensornetwork.network_components import AbstractNode, Edge as Edge
from typing import Any, Callable, Collection, Sequence

Tensor = Any
Graph = Any
logger: Incomplete

def quantum_constructor(out_edges: Sequence[Edge], in_edges: Sequence[Edge], ref_nodes: Collection[AbstractNode] | None = None, ignore_edges: Collection[Edge] | None = None) -> QuOperator:
    '''
    Constructs an appropriately specialized QuOperator.
    If there are no edges, creates a QuScalar. If the are only output (input)
    edges, creates a QuVector (QuAdjointVector). Otherwise creates a QuOperator.

    :Example:

    .. code-block:: python

        def show_attributes(op):
            print(f"op.is_scalar() \t\t-> {op.is_scalar()}")
            print(f"op.is_vector() \t\t-> {op.is_vector()}")
            print(f"op.is_adjoint_vector() \t-> {op.is_adjoint_vector()}")
            print(f"len(op.out_edges) \t-> {len(op.out_edges)}")
            print(f"len(op.in_edges) \t-> {len(op.in_edges)}")

    >>> psi_node = tn.Node(np.random.rand(2, 2))
    >>>
    >>> op = qu.quantum_constructor([psi_node[0]], [psi_node[1]])
    >>> show_attributes(op)
    op.is_scalar()          -> False
    op.is_vector()          -> False
    op.is_adjoint_vector()  -> False
    len(op.out_edges)       -> 1
    len(op.in_edges)        -> 1
    >>> # psi_node[0] -> op.out_edges[0]
    >>> # psi_node[1] -> op.in_edges[0]

    >>> op = qu.quantum_constructor([psi_node[0], psi_node[1]], [])
    >>> show_attributes(op)
    op.is_scalar()          -> False
    op.is_vector()          -> True
    op.is_adjoint_vector()  -> False
    len(op.out_edges)       -> 2
    len(op.in_edges)        -> 0
    >>> # psi_node[0] -> op.out_edges[0]
    >>> # psi_node[1] -> op.out_edges[1]

    >>> op = qu.quantum_constructor([], [psi_node[0], psi_node[1]])
    >>> show_attributes(op)
    op.is_scalar()          -> False
    op.is_vector()          -> False
    op.is_adjoint_vector()  -> True
    len(op.out_edges)       -> 0
    len(op.in_edges)        -> 2
    >>> # psi_node[0] -> op.in_edges[0]
    >>> # psi_node[1] -> op.in_edges[1]

    :param out_edges: A list of output edges.
    :type out_edges: Sequence[Edge]
    :param in_edges: A list of input edges.
    :type in_edges: Sequence[Edge]
    :param ref_nodes: Reference nodes for the tensor network (needed if there is a.
        scalar component).
    :type ref_nodes: Optional[Collection[AbstractNode]], optional
    :param ignore_edges: Edges to ignore when checking the dimensionality of the
        tensor network.
    :type ignore_edges: Optional[Collection[Edge]], optional
    :return: The new created QuOperator object.
    :rtype: QuOperator
    '''
def identity(space: Sequence[int], dtype: Any = None) -> QuOperator:
    """
    Construct a 'QuOperator' representing the identity on a given space.
    Internally, this is done by constructing 'CopyNode's for each edge, with
    dimension according to 'space'.

    :Example:

    >>> E = qu.identity((2, 3, 4))
    >>> float(E.trace().eval())
    24.0

    >>> tensor = np.random.rand(2, 2)
    >>> psi = qu.QuVector.from_tensor(tensor)
    >>> E = qu.identity((2, 2))
    >>> psi.eval()
    array([[0.03964233, 0.99298281],
           [0.38564989, 0.00950596]])
    >>> (E @ psi).eval()
    array([[0.03964233, 0.99298281],
           [0.38564989, 0.00950596]])
    >>>
    >>> (psi.adjoint() @ E @ psi).eval()
    array(1.13640257)
    >>> psi.norm().eval()
    array(1.13640257)

    :param space: A sequence of integers for the dimensions of the tensor product
        factors of the space (the edges in the tensor network).
    :type space: Sequence[int]
    :param dtype: The data type by np.* (for conversion to dense). defaults None to tc dtype.
    :type dtype: Any type
    :return: The desired identity operator.
    :rtype: QuOperator
    """
def check_spaces(edges_1: Sequence[Edge], edges_2: Sequence[Edge]) -> None:
    '''
    Check the vector spaces represented by two lists of edges are compatible.
    The number of edges must be the same and the dimensions of each pair of edges
    must match. Otherwise, an exception is raised.

    :param edges_1: List of edges representing a many-body Hilbert space.
    :type edges_1: Sequence[Edge]
    :param edges_2: List of edges representing a many-body Hilbert space.
    :type edges_2: Sequence[Edge]

    :raises ValueError: Hilbert-space mismatch: "Cannot connect {} subsystems with {} subsystems", or
        "Input dimension {} != output dimension {}."
    '''
def eliminate_identities(nodes: Collection[AbstractNode]) -> tuple[dict, dict]:
    """
    Eliminates any connected CopyNodes that are identity matrices.
    This will modify the network represented by `nodes`.
    Only identities that are connected to other nodes are eliminated.

    :param nodes: Collection of nodes to search.
    :type nodes: Collection[AbstractNode]
    :return: The Dictionary mapping remaining Nodes to any replacements, Dictionary specifying all dangling-edge
        replacements.
    :rtype: Dict[Union[CopyNode, AbstractNode], Union[Node, AbstractNode]], Dict[Edge, Edge]
    """

class QuOperator:
    """
    Represents a linear operator via a tensor network.
    To interpret a tensor network as a linear operator, some of the dangling
    edges must be designated as `out_edges` (output edges) and the rest as
    `in_edges` (input edges).
    Considered as a matrix, the `out_edges` represent the row index and the
    `in_edges` represent the column index.
    The (right) action of the operator on another then consists of connecting
    the `in_edges` of the first operator to the `out_edges` of the second.
    Can be used to do simple linear algebra with tensor networks.
    """
    __array_priority__: float
    out_edges: Incomplete
    in_edges: Incomplete
    ignore_edges: Incomplete
    ref_nodes: Incomplete
    def __init__(self, out_edges: Sequence[Edge], in_edges: Sequence[Edge], ref_nodes: Collection[AbstractNode] | None = None, ignore_edges: Collection[Edge] | None = None) -> None:
        """
        Creates a new `QuOperator` from a tensor network.
        This encapsulates an existing tensor network, interpreting it as a linear
        operator.
        The network is checked for consistency: All dangling edges must either be
        in `out_edges`, `in_edges`, or `ignore_edges`.

        :param out_edges: The edges of the network to be used as the output edges.
        :type out_edges: Sequence[Edge]
        :param in_edges: The edges of the network to be used as the input edges.
        :type in_edges: Sequence[Edge]
        :param ref_nodes: Nodes used to refer to parts of the tensor network that are
            not connected to any input or output edges (for example: a scalar
            factor).
        :type ref_nodes: Optional[Collection[AbstractNode]], optional
        :param ignore_edges: Optional collection of dangling edges to ignore when
            performing consistency checks.
        :type ignore_edges: Optional[Collection[Edge]], optional
        :raises ValueError: At least one reference node is required to specify a scalar. None provided!
        """
    @classmethod
    def from_tensor(cls, tensor: Tensor, out_axes: Sequence[int] | None = None, in_axes: Sequence[int] | None = None) -> QuOperator:
        '''
        Construct a `QuOperator` directly from a single tensor.
        This first wraps the tensor in a `Node`, then constructs the `QuOperator`
        from that `Node`.

        :Example:

        .. code-block:: python

            def show_attributes(op):
                print(f"op.is_scalar() \\t\\t-> {op.is_scalar()}")
                print(f"op.is_vector() \\t\\t-> {op.is_vector()}")
                print(f"op.is_adjoint_vector() \\t-> {op.is_adjoint_vector()}")
                print(f"op.eval() \\n{op.eval()}")

        >>> psi_tensor = np.random.rand(2, 2)
        >>> psi_tensor
        array([[0.27260127, 0.91401091],
               [0.06490953, 0.38653646]])
        >>> op = qu.QuOperator.from_tensor(psi_tensor, out_axes=[0], in_axes=[1])
        >>> show_attributes(op)
        op.is_scalar()          -> False
        op.is_vector()          -> False
        op.is_adjoint_vector()  -> False
        op.eval()
        [[0.27260127 0.91401091]
         [0.06490953 0.38653646]]

        :param tensor: The tensor.
        :type tensor: Tensor
        :param out_axes: The axis indices of `tensor` to use as `out_edges`.
        :type out_axes: Optional[Sequence[int]], optional
        :param in_axes: The axis indices of `tensor` to use as `in_edges`.
        :type in_axes: Optional[Sequence[int]], optional
        :return: The new operator.
        :rtype: QuOperator
        '''
    @classmethod
    def from_local_tensor(cls, tensor: Tensor, space: Sequence[int], loc: Sequence[int], out_axes: Sequence[int] | None = None, in_axes: Sequence[int] | None = None) -> QuOperator: ...
    @property
    def nodes(self) -> set[AbstractNode]:
        """All tensor-network nodes involved in the operator."""
    @property
    def in_space(self) -> list[int]: ...
    @property
    def out_space(self) -> list[int]: ...
    def is_scalar(self) -> bool:
        """
        Returns a bool indicating if QuOperator is a scalar.
        Examples can be found in the `QuOperator.from_tensor`.
        """
    def is_vector(self) -> bool:
        """
        Returns a bool indicating if QuOperator is a vector.
        Examples can be found in the `QuOperator.from_tensor`.
        """
    def is_adjoint_vector(self) -> bool:
        """
        Returns a bool indicating if QuOperator is an adjoint vector.
        Examples can be found in the `QuOperator.from_tensor`.
        """
    def check_network(self) -> None:
        """
        Check that the network has the expected dimensionality.
        This checks that all input and output edges are dangling and that
        there are no other dangling edges (except any specified in
        `ignore_edges`). If not, an exception is raised.
        """
    def adjoint(self) -> QuOperator:
        """
        The adjoint of the operator.
        This creates a new `QuOperator` with complex-conjugate copies of all
        tensors in the network and with the input and output edges switched.

        :return: The adjoint of the operator.
        :rtype: QuOperator
        """
    def copy(self) -> QuOperator:
        """
        The deep copy of the operator.

        :return: The new copy of the operator.
        :rtype: QuOperator
        """
    def trace(self) -> QuOperator:
        """The trace of the operator."""
    def norm(self) -> QuOperator:
        """
        The norm of the operator.
        This is the 2-norm (also known as the Frobenius or Hilbert-Schmidt
        norm).
        """
    def partial_trace(self, subsystems_to_trace_out: Collection[int]) -> QuOperator:
        """
        The partial trace of the operator.
        Subsystems to trace out are supplied as indices, so that dangling edges
        are connected to each other as:
        `out_edges[i] ^ in_edges[i] for i in subsystems_to_trace_out`
        This does not modify the original network. The original ordering of the
        remaining subsystems is maintained.

        :param subsystems_to_trace_out: Indices of subsystems to trace out.
        :type subsystems_to_trace_out: Collection[int]
        :return: A new QuOperator or QuScalar representing the result.
        :rtype: QuOperator
        """
    def __matmul__(self, other: QuOperator | Tensor) -> QuOperator:
        '''
        The action of this operator on another.
        Given `QuOperator`s `A` and `B`, produces a new `QuOperator` for `A @ B`,
        where `A @ B` means: "the action of A, as a linear operator, on B".
        Under the hood, this produces copies of the tensor networks defining `A`
        and `B` and then connects the copies by hooking up the `in_edges` of
        `A.copy()` to the `out_edges` of `B.copy()`.
        '''
    def __rmatmul__(self, other: QuOperator | Tensor) -> QuOperator: ...
    def __mul__(self, other: QuOperator | AbstractNode | Tensor) -> QuOperator:
        """
        Scalar multiplication of operators.
        Given two operators `A` and `B`, one of the which is a scalar (it has no
        input or output edges), `A * B` produces a new operator representing the
        scalar multiplication of `A` and `B`.
        For convenience, one of `A` or `B` may be a number or scalar-valued tensor
        or `Node` (it will automatically be wrapped in a `QuScalar`).
        Note: This is a special case of `tensor_product()`.
        """
    def __rmul__(self, other: QuOperator | AbstractNode | Tensor) -> QuOperator:
        """
        Scalar multiplication of operators.
        See `.__mul__()`.
        """
    def tensor_product(self, other: QuOperator) -> QuOperator:
        """
        Tensor product with another operator.
        Given two operators `A` and `B`, produces a new operator `AB` representing
        :math:`A ⊗ B`. The `out_edges` (`in_edges`) of `AB` is simply the
        concatenation of the `out_edges` (`in_edges`) of `A.copy()` with that of
        `B.copy()`:
        `new_out_edges = [*out_edges_A_copy, *out_edges_B_copy]`
        `new_in_edges = [*in_edges_A_copy, *in_edges_B_copy]`

        :Example:

        >>> psi = qu.QuVector.from_tensor(np.random.rand(2, 2))
        >>> psi_psi = psi.tensor_product(psi)
        >>> len(psi_psi.subsystem_edges)
        4
        >>> float(psi_psi.norm().eval())
        2.9887872748523585
        >>> psi.norm().eval() ** 2
        2.9887872748523585

        :param other: The other operator (`B`).
        :type other: QuOperator
        :return: The result (`AB`).
        :rtype: QuOperator
        """
    def __or__(self, other: QuOperator) -> QuOperator:
        """
        Tensor product of operators.
        Given two operators `A` and `B`, `A | B` produces a new operator representing the
        tensor product of `A` and `B`.
        """
    def contract(self, final_edge_order: Sequence[Edge] | None = None) -> QuOperator:
        """
        Contract the tensor network in place.
        This modifies the tensor network representation of the operator (or vector,
        or scalar), reducing it to a single tensor, without changing the value.

        :param final_edge_order: Manually specify the axis ordering of the final tensor.
        :type final_edge_order: Optional[Sequence[Edge]], optional
        :return: The present object.
        :rtype: QuOperator
        """
    def eval(self, final_edge_order: Sequence[Edge] | None = None) -> Tensor:
        '''
        Contracts the tensor network in place and returns the final tensor.
        Note that this modifies the tensor network representing the operator.
        The default ordering for the axes of the final tensor is:
        `*out_edges, *in_edges`.
        If there are any "ignored" edges, their axes come first:
        `*ignored_edges, *out_edges, *in_edges`.

        :param final_edge_order: Manually specify the axis ordering of the final tensor.
            The default ordering is determined by `out_edges` and `in_edges` (see above).
        :type final_edge_order: Optional[Sequence[Edge]], optional
        :raises ValueError: Node count \'{}\' > 1 after contraction!
        :return: The final tensor representing the operator.
        :rtype: Tensor
        '''
    def eval_matrix(self, final_edge_order: Sequence[Edge] | None = None) -> Tensor:
        """
        Contracts the tensor network in place and returns the final tensor
        in two dimentional matrix.
        The default ordering for the axes of the final tensor is:
        (:math:`\\prod` dimension of out_edges, :math:`\\prod` dimension of in_edges)

        :param final_edge_order: Manually specify the axis ordering of the final tensor.
            The default ordering is determined by `out_edges` and `in_edges` (see above).
        :type final_edge_order: Optional[Sequence[Edge]], optional
        :raises ValueError: Node count '{}' > 1 after contraction!
        :return: The two-dimentional tensor representing the operator.
        :rtype: Tensor
        """

class QuVector(QuOperator):
    """Represents a (column) vector via a tensor network."""
    def __init__(self, subsystem_edges: Sequence[Edge], ref_nodes: Collection[AbstractNode] | None = None, ignore_edges: Collection[Edge] | None = None) -> None:
        """
        Constructs a new `QuVector` from a tensor network.
        This encapsulates an existing tensor network, interpreting it as a (column) vector.

        :param subsystem_edges: The edges of the network to be used as the output edges.
        :type subsystem_edges: Sequence[Edge]
        :param ref_nodes: Nodes used to refer to parts of the tensor network that are
            not connected to any input or output edges (for example: a scalar factor).
        :type ref_nodes: Optional[Collection[AbstractNode]], optional
        :param ignore_edges: Optional collection of edges to ignore when performing consistency checks.
        :type ignore_edges: Optional[Collection[Edge]], optional
        """
    @classmethod
    def from_tensor(cls, tensor: Tensor, subsystem_axes: Sequence[int] | None = None) -> QuVector:
        '''
        Construct a `QuVector` directly from a single tensor.
        This first wraps the tensor in a `Node`, then constructs the `QuVector`
        from that `Node`.

        :Example:

        .. code-block:: python

            def show_attributes(op):
                print(f"op.is_scalar() \\t\\t-> {op.is_scalar()}")
                print(f"op.is_vector() \\t\\t-> {op.is_vector()}")
                print(f"op.is_adjoint_vector() \\t-> {op.is_adjoint_vector()}")
                print(f"op.eval() \\n{op.eval()}")

        >>> psi_tensor = np.random.rand(2, 2)
        >>> psi_tensor
        array([[0.27260127, 0.91401091],
               [0.06490953, 0.38653646]])
        >>> op = qu.QuVector.from_tensor(psi_tensor, [0, 1])
        >>> show_attributes(op)
        op.is_scalar()          -> False
        op.is_vector()          -> True
        op.is_adjoint_vector()  -> False
        op.eval()
        [[0.27260127 0.91401091]
         [0.06490953 0.38653646]]

        :param tensor: The tensor for constructing a "QuVector".
        :type tensor: Tensor
        :param subsystem_axes: Sequence of integer indices specifying the order in which
            to interpret the axes as subsystems (output edges). If not specified,
            the axes are taken in ascending order.
        :type subsystem_axes: Optional[Sequence[int]], optional
        :return: The new constructed QuVector from the given tensor.
        :rtype: QuVector
        '''
    @property
    def subsystem_edges(self) -> list[Edge]: ...
    @property
    def space(self) -> list[int]: ...
    def projector(self) -> QuOperator:
        """
        The projector of the operator.
        The operator, as a linear operator, on the adjoint of the operator.

        Set :math:`A` is the operator in matrix form, then the projector of operator is defined as: :math:`A A^\\dagger`

        :return: The projector of the operator.
        :rtype: QuOperator
        """
    def reduced_density(self, subsystems_to_trace_out: Collection[int]) -> QuOperator:
        """
        The reduced density of the operator.

        Set :math:`A` is the matrix of the operator, then the reduced density is defined as:

        .. math::

            \\mathrm{Tr}_{subsystems}(A A^\\dagger)

        Firstly, take the projector of the operator, then trace out the subsystems
        to trace out are supplied as indices, so that dangling edges are connected
        to each other as:
        `out_edges[i] ^ in_edges[i] for i in subsystems_to_trace_out`
        This does not modify the original network. The original ordering of the
        remaining subsystems is maintained.

        :param subsystems_to_trace_out: Indices of subsystems to trace out.
        :type subsystems_to_trace_out: Collection[int]
        :return: The QuOperator of the reduced density of the operator with given subsystems.
        :rtype: QuOperator
        """

class QuAdjointVector(QuOperator):
    """Represents an adjoint (row) vector via a tensor network."""
    def __init__(self, subsystem_edges: Sequence[Edge], ref_nodes: Collection[AbstractNode] | None = None, ignore_edges: Collection[Edge] | None = None) -> None:
        """
        Constructs a new `QuAdjointVector` from a tensor network.
        This encapsulates an existing tensor network, interpreting it as an adjoint
        vector (row vector).

        :param subsystem_edges: The edges of the network to be used as the input edges.
        :type subsystem_edges: Sequence[Edge]
        :param ref_nodes: Nodes used to refer to parts of the tensor network that are
            not connected to any input or output edges (for example: a scalar factor).
        :type ref_nodes: Optional[Collection[AbstractNode]], optional
        :param ignore_edges: Optional collection of edges to ignore when performing consistency checks.
        :type ignore_edges: Optional[Collection[Edge]], optional
        """
    @classmethod
    def from_tensor(cls, tensor: Tensor, subsystem_axes: Sequence[int] | None = None) -> QuAdjointVector:
        '''
        Construct a `QuAdjointVector` directly from a single tensor.
        This first wraps the tensor in a `Node`, then constructs the `QuAdjointVector` from that `Node`.

        :Example:

        .. code-block:: python

            def show_attributes(op):
                print(f"op.is_scalar() \\t\\t-> {op.is_scalar()}")
                print(f"op.is_vector() \\t\\t-> {op.is_vector()}")
                print(f"op.is_adjoint_vector() \\t-> {op.is_adjoint_vector()}")
                print(f"op.eval() \\n{op.eval()}")

        >>> psi_tensor = np.random.rand(2, 2)
        >>> psi_tensor
        array([[0.27260127, 0.91401091],
               [0.06490953, 0.38653646]])
        >>> op = qu.QuAdjointVector.from_tensor(psi_tensor, [0, 1])
        >>> show_attributes(op)
        op.is_scalar()          -> False
        op.is_vector()          -> False
        op.is_adjoint_vector()  -> True
        op.eval()
        [[0.27260127 0.91401091]
         [0.06490953 0.38653646]]

        :param tensor: The tensor for constructing an QuAdjointVector.
        :type tensor: Tensor
        :param subsystem_axes: Sequence of integer indices specifying the order in which
            to interpret the axes as subsystems (input edges). If not specified,
            the axes are taken in ascending order.
        :type subsystem_axes: Optional[Sequence[int]], optional
        :return: The new constructed QuAdjointVector give from the given tensor.
        :rtype: QuAdjointVector
        '''
    @property
    def subsystem_edges(self) -> list[Edge]: ...
    @property
    def space(self) -> list[int]: ...
    def projector(self) -> QuOperator:
        """
        The projector of the operator.
        The operator, as a linear operator, on the adjoint of the operator.

        Set :math:`A` is the operator in matrix form, then the projector of operator is defined as: :math:`A^\\dagger A`

        :return: The projector of the operator.
        :rtype: QuOperator
        """
    def reduced_density(self, subsystems_to_trace_out: Collection[int]) -> QuOperator:
        """
        The reduced density of the operator.

        Set :math:`A` is the matrix of the operator, then the reduced density is defined as:

        .. math::

            \\mathrm{Tr}_{subsystems}(A^\\dagger A)

        Firstly, take the projector of the operator, then trace out the subsystems
        to trace out are supplied as indices, so that dangling edges are connected
        to each other as:
        `out_edges[i] ^ in_edges[i] for i in subsystems_to_trace_out`
        This does not modify the original network. The original ordering of the
        remaining subsystems is maintained.

        :param subsystems_to_trace_out: Indices of subsystems to trace out.
        :type subsystems_to_trace_out: Collection[int]
        :return: The QuOperator of the reduced density of the operator with given subsystems.
        :rtype: QuOperator
        """

class QuScalar(QuOperator):
    """Represents a scalar via a tensor network."""
    def __init__(self, ref_nodes: Collection[AbstractNode], ignore_edges: Collection[Edge] | None = None) -> None:
        """
        Constructs a new `QuScalar` from a tensor network.
        This encapsulates an existing tensor network, interpreting it as a scalar.

        :param ref_nodes: Nodes used to refer to the tensor network (need not be
            exhaustive - one node from each disconnected subnetwork is sufficient).
        :type ref_nodes: Collection[AbstractNode]
        :param ignore_edges: Optional collection of edges to ignore when performing consistency checks.
        :type ignore_edges: Optional[Collection[Edge]], optional
        """
    @classmethod
    def from_tensor(cls, tensor: Tensor) -> QuScalar:
        '''
        Construct a `QuScalar` directly from a single tensor.
        This first wraps the tensor in a `Node`, then constructs the `QuScalar` from that `Node`.

        :Example:

        .. code-block:: python

            def show_attributes(op):
                print(f"op.is_scalar() \\t\\t-> {op.is_scalar()}")
                print(f"op.is_vector() \\t\\t-> {op.is_vector()}")
                print(f"op.is_adjoint_vector() \\t-> {op.is_adjoint_vector()}")
                print(f"op.eval() \\n{op.eval()}")

        >>> op = qu.QuScalar.from_tensor(1.0)
        >>> show_attributes(op)
        op.is_scalar()          -> True
        op.is_vector()          -> False
        op.is_adjoint_vector()  -> False
        op.eval()
        1.0

        :param tensor: The tensor for constructing a new QuScalar.
        :type tensor: Tensor
        :return: The new constructed QuScalar from the given tensor.
        :rtype: QuScalar
        '''

def generate_local_hamiltonian(*hlist: Sequence[Tensor], matrix_form: bool = True) -> QuOperator | Tensor:
    """
    Generate a local Hamiltonian operator based on the given sequence of Tensor.
    Note: further jit is recommended.
    For large Hilbert space, sparse Hamiltonian is recommended

    :param hlist: A sequence of Tensor.
    :type hlist: Sequence[Tensor]
    :param matrix_form: Return Hamiltonian operator in form of matrix, defaults to True.
    :type matrix_form: bool, optional
    :return: The Hamiltonian operator in form of QuOperator or matrix.
    :rtype: Union[QuOperator, Tensor]
    """
def tn2qop(tn_mpo: Any) -> QuOperator:
    """
    Convert MPO in TensorNetwork package to QuOperator.

    :param tn_mpo: MPO in the form of TensorNetwork package
    :type tn_mpo: ``tn.matrixproductstates.mpo.*``
    :return: MPO in the form of QuOperator
    :rtype: QuOperator
    """
def quimb2qop(qb_mpo: Any) -> QuOperator:
    """
    Convert MPO in Quimb package to QuOperator.

    :param tn_mpo: MPO in the form of Quimb package
    :type tn_mpo: ``quimb.tensor.tensor_gen.*``
    :return: MPO in the form of QuOperator
    :rtype: QuOperator
    """
def op2tensor(fn: Callable[..., Any], op_argnums: int | Sequence[int] = 0) -> Callable[..., Any]: ...
@op2tensor
def entropy(rho: Tensor | QuOperator, eps: float = 1e-12) -> Tensor:
    """
    Compute the entropy from the given density matrix ``rho``.

    :Example:

    .. code-block:: python

        @partial(tc.backend.jit, jit_compile=False, static_argnums=(1, 2))
        def entanglement1(param, n, nlayers):
            c = tc.Circuit(n)
            c = tc.templates.blocks.example_block(c, param, nlayers)
            w = c.wavefunction()
            rm = qu.reduced_density_matrix(w, int(n / 2))
            return qu.entropy(rm)

        @partial(tc.backend.jit, jit_compile=False, static_argnums=(1, 2))
        def entanglement2(param, n, nlayers):
            c = tc.Circuit(n)
            c = tc.templates.blocks.example_block(c, param, nlayers)
            w = c.get_quvector()
            rm = w.reduced_density([i for i in range(int(n / 2))])
            return qu.entropy(rm)

    >>> param = tc.backend.ones([6, 6])
    >>> tc.backend.trace(param)
    >>> entanglement1(param, 6, 3)
    1.3132654
    >>> entanglement2(param, 6, 3)
    1.3132653

    :param rho: The density matrix in form of Tensor or QuOperator.
    :type rho: Union[Tensor, QuOperator]
    :param eps: Epsilon, default is 1e-12.
    :type eps: float
    :return: Entropy on the given density matrix.
    :rtype: Tensor
    """
def trace_product(*o: Tensor | QuOperator) -> Tensor:
    """
    Compute the trace of several inputs ``o`` as tensor or ``QuOperator``.

    .. math ::

        \\operatorname{Tr}(\\prod_i O_i)

    :Example:

    >>> o = np.ones([2, 2])
    >>> h = np.eye(2)
    >>> qu.trace_product(o, h)
    2.0
    >>> oq = qu.QuOperator.from_tensor(o)
    >>> hq = qu.QuOperator.from_tensor(h)
    >>> qu.trace_product(oq, hq)
    array([[2.]])
    >>> qu.trace_product(oq, h)
    array([[2.]])
    >>> qu.trace_product(o, hq)
    array([[2.]])

    :return: The trace of several inputs.
    :rtype: Tensor
    """
def reduced_density_matrix(state: Tensor | QuOperator, cut: int | list[int], p: Tensor | None = None) -> Tensor | QuOperator:
    """
    Compute the reduced density matrix from the quantum state ``state``.

    :param state: The quantum state in form of Tensor or QuOperator.
    :type state: Union[Tensor, QuOperator]
    :param cut: the index list that is traced out, if cut is a int,
        it indicates [0, cut] as the traced out region
    :type cut: Union[int, List[int]]
    :param p: probability decoration, default is None.
    :type p: Optional[Tensor]
    :return: The reduced density matrix.
    :rtype: Union[Tensor, QuOperator]
    """
def free_energy(rho: Tensor | QuOperator, h: Tensor | QuOperator, beta: float = 1, eps: float = 1e-12) -> Tensor:
    """
    Compute the free energy of the given density matrix.

    :Example:

    >>> rho = np.array([[1.0, 0], [0, 0]])
    >>> h = np.array([[-1.0, 0], [0, 1]])
    >>> qu.free_energy(rho, h, 0.5)
    -0.9999999999979998
    >>> hq = qu.QuOperator.from_tensor(h)
    >>> qu.free_energy(rho, hq, 0.5)
    array([[-1.]])

    :param rho: The density matrix in form of Tensor or QuOperator.
    :type rho: Union[Tensor, QuOperator]
    :param h: Hamiltonian operator in form of Tensor or QuOperator.
    :type h: Union[Tensor, QuOperator]
    :param beta: Constant for the optimization, default is 1.
    :type beta: float, optional
    :param eps: Epsilon, default is 1e-12.
    :type eps: float, optional

    :return: The free energy of the given density matrix with the Hamiltonian operator.
    :rtype: Tensor
    """
def renyi_entropy(rho: Tensor | QuOperator, k: int = 2) -> Tensor:
    """
    Compute the Rényi entropy of order :math:`k` by given density matrix.

    :param rho: The density matrix in form of Tensor or QuOperator.
    :type rho: Union[Tensor, QuOperator]
    :param k: The order of Rényi entropy, default is 2.
    :type k: int, optional
    :return: The :math:`k` th order of Rényi entropy.
    :rtype: Tensor
    """
def renyi_free_energy(rho: Tensor | QuOperator, h: Tensor | QuOperator, beta: float = 1, k: int = 2) -> Tensor:
    """
    Compute the Rényi free energy of the corresponding density matrix and Hamiltonian.

    :Example:

    >>> rho = np.array([[1.0, 0], [0, 0]])
    >>> h = np.array([[-1.0, 0], [0, 1]])
    >>> qu.renyi_free_energy(rho, h, 0.5)
    -1.0
    >>> qu.free_energy(rho, h, 0.5)
    -0.9999999999979998

    :param rho: The density matrix in form of Tensor or QuOperator.
    :type rho: Union[Tensor, QuOperator]
    :param h: Hamiltonian operator in form of Tensor or QuOperator.
    :type h: Union[Tensor, QuOperator]
    :param beta: Constant for the optimization, default is 1.
    :type beta: float, optional
    :param k: The order of Rényi entropy, default is 2.
    :type k: int, optional
    :return: The :math:`k` th order of Rényi entropy.
    :rtype: Tensor
    """
def taylorlnm(x: Tensor, k: int) -> Tensor:
    """
    Taylor expansion of :math:`ln(x+1)`.

    :param x: The density matrix in form of Tensor.
    :type x: Tensor
    :param k: The :math:`k` th order, default is 2.
    :type k: int, optional
    :return: The :math:`k` th order of Taylor expansion of :math:`ln(x+1)`.
    :rtype: Tensor
    """
def truncated_free_energy(rho: Tensor, h: Tensor, beta: float = 1, k: int = 2) -> Tensor:
    """
    Compute the truncated free energy from the given density matrix ``rho``.

    :param rho: The density matrix in form of Tensor.
    :type rho: Tensor
    :param h: Hamiltonian operator in form of Tensor.
    :type h: Tensor
    :param beta: Constant for the optimization, default is 1.
    :type beta: float, optional
    :param k: The :math:`k` th order, defaults to 2
    :type k: int, optional
    :return: The :math:`k` th order of the truncated free energy.
    :rtype: Tensor
    """
def trace_distance(rho: Tensor, rho0: Tensor, eps: float = 1e-12) -> Tensor:
    """
    Compute the trace distance between two density matrix ``rho`` and ``rho2``.

    :param rho: The density matrix in form of Tensor.
    :type rho: Tensor
    :param rho0: The density matrix in form of Tensor.
    :type rho0: Tensor
    :param eps: Epsilon, defaults to 1e-12
    :type eps: float, optional
    :return: The trace distance between two density matrix ``rho`` and ``rho2``.
    :rtype: Tensor
    """
def fidelity(rho: Tensor, rho0: Tensor) -> Tensor:
    """
    Return fidelity scalar between two states rho and rho0.

    .. math::

        \\operatorname{Tr}(\\sqrt{\\sqrt{rho} rho_0 \\sqrt{rho}})

    :param rho: The density matrix in form of Tensor.
    :type rho: Tensor
    :param rho0: The density matrix in form of Tensor.
    :type rho0: Tensor
    :return: The sqrtm of a Hermitian matrix ``a``.
    :rtype: Tensor
    """
@op2tensor
def gibbs_state(h: Tensor, beta: float = 1) -> Tensor:
    """
    Compute the Gibbs state of the given Hamiltonian operator ``h``.

    :param h: Hamiltonian operator in form of Tensor.
    :type h: Tensor
    :param beta: Constant for the optimization, default is 1.
    :type beta: float, optional
    :return: The Gibbs state of ``h`` with the given ``beta``.
    :rtype: Tensor
    """
@op2tensor
def double_state(h: Tensor, beta: float = 1) -> Tensor:
    """
    Compute the double state of the given Hamiltonian operator ``h``.

    :param h: Hamiltonian operator in form of Tensor.
    :type h: Tensor
    :param beta: Constant for the optimization, default is 1.
    :type beta: float, optional
    :return: The double state of ``h`` with the given ``beta``.
    :rtype: Tensor
    """
@op2tensor
def mutual_information(s: Tensor, cut: int | list[int]) -> Tensor:
    """
    Mutual information between AB subsystem described by ``cut``.

    :param s: The density matrix in form of Tensor.
    :type s: Tensor
    :param cut: The AB subsystem.
    :type cut: Union[int, List[int]]
    :return: The mutual information between AB subsystem described by ``cut``.
    :rtype: Tensor
    """
def count_s2d(srepr: tuple[Tensor, Tensor], n: int) -> Tensor:
    """
    measurement shots results, sparse tuple representation to dense representation
    count_vector to count_tuple

    :param srepr: [description]
    :type srepr: Tuple[Tensor, Tensor]
    :param n: number of qubits
    :type n: int
    :return: [description]
    :rtype: Tensor
    """
counts_v2t = count_s2d

def count_d2s(drepr: Tensor, eps: float = 1e-07) -> tuple[Tensor, Tensor]:
    """
    measurement shots results, dense representation to sparse tuple representation
    non-jittable due to the non fixed return shape
    count_tuple to count_vector

    :Example:

    >>> tc.quantum.counts_d2s(np.array([0.1, 0, -0.3, 0.2]))
    (array([0, 2, 3]), array([ 0.1, -0.3,  0.2]))

    :param drepr: [description]
    :type drepr: Tensor
    :param eps: cutoff to determine nonzero elements, defaults to 1e-7
    :type eps: float, optional
    :return: [description]
    :rtype: Tuple[Tensor, Tensor]
    """
count_t2v = count_d2s

def sample_int2bin(sample: Tensor, n: int) -> Tensor:
    """
    int sample to bin sample

    :param sample: in shape [trials] of int elements in the range [0, 2**n)
    :type sample: Tensor
    :param n: number of qubits
    :type n: int
    :return: in shape [trials, n] of element (0, 1)
    :rtype: Tensor
    """
def sample_bin2int(sample: Tensor, n: int) -> Tensor:
    """
    bin sample to int sample

    :param sample: in shape [trials, n] of elements (0, 1)
    :type sample: Tensor
    :param n: number of qubits
    :type n: int
    :return: in shape [trials]
    :rtype: Tensor
    """
def sample2count(sample: Tensor, n: int, jittable: bool = True) -> tuple[Tensor, Tensor]:
    """
    sample_int to count_tuple

    :param sample: _description_
    :type sample: Tensor
    :param n: _description_
    :type n: int
    :param jittable: _description_, defaults to True
    :type jittable: bool, optional
    :return: _description_
    :rtype: Tuple[Tensor, Tensor]
    """
def count_vector2dict(count: Tensor, n: int, key: str = 'bin') -> dict[Any, int]:
    '''
    convert_vector to count_dict_bin or count_dict_int

    :param count: tensor in shape [2**n]
    :type count: Tensor
    :param n: number of qubits
    :type n: int
    :param key: can be "int" or "bin", defaults to "bin"
    :type key: str, optional
    :return: _description_
    :rtype: _type_
    '''
def count_tuple2dict(count: tuple[Tensor, Tensor], n: int, key: str = 'bin') -> dict[Any, int]:
    '''
    count_tuple to count_dict_bin or count_dict_int

    :param count: count_tuple format
    :type count: Tuple[Tensor, Tensor]
    :param n: number of qubits
    :type n: int
    :param key: can be "int" or "bin", defaults to "bin"
    :type key: str, optional
    :return: count_dict
    :rtype: _type_
    '''
def measurement_counts(state: Tensor, counts: int | None = 8192, format: str = 'count_vector', is_prob: bool = False, random_generator: Any | None = None, status: Tensor | None = None, jittable: bool = False) -> Any:
    '''
    Simulate the measuring of each qubit of ``p`` in the computational basis,
    thus producing output like that of ``qiskit``.

    Six formats of measurement counts results:

    "sample_int": # np.array([0, 0])

    "sample_bin": # [np.array([1, 0]), np.array([1, 0])]

    "count_vector": # np.array([2, 0, 0, 0])

    "count_tuple": # (np.array([0]), np.array([2]))

    "count_dict_bin": # {"00": 2, "01": 0, "10": 0, "11": 0}

    "count_dict_int": # {0: 2, 1: 0, 2: 0, 3: 0}

    :Example:

    >>> n = 4
    >>> w = tc.backend.ones([2**n])
    >>> tc.quantum.measurement_results(w, counts=3, format="sample_bin", jittable=True)
    array([[0, 0, 1, 0],
        [0, 1, 1, 0],
        [0, 1, 1, 1]])
    >>> tc.quantum.measurement_results(w, counts=3, format="sample_int", jittable=True)
    array([ 7, 15, 11])
    >>> tc.quantum.measurement_results(w, counts=3, format="count_vector", jittable=True)
    array([0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1])
    >>> tc.quantum.measurement_results(w, counts=3, format="count_tuple")
    (array([1, 2, 8]), array([1, 1, 1]))
    >>> tc.quantum.measurement_results(w, counts=3, format="count_dict_bin")
    {\'0001\': 1, \'0011\': 1, \'1101\': 1}
    >>> tc.quantum.measurement_results(w, counts=3, format="count_dict_int")
    {3: 1, 6: 2}

    :param state: The quantum state, assumed to be normalized, as either a ket or density operator.
    :type state: Tensor
    :param counts: The number of counts to perform.
    :type counts: int
    :param format: defaults to be "direct", see supported format above
    :type format: str
    :param is_prob: if True, the `state` is directly regarded as a probability list,
        defaults to be False
    :type is_prob: bool
    :param random_generator: random_generator, defaults to None
    :type random_generator: Optional[Any]
    :param status: external randomness given by tensor uniformly from [0, 1],
        if set, can overwrite random_generator
    :type status: Optional[Tensor]
    :param jittable: if True, jax backend try using a jittable count, defaults to False
    :type jittable: bool
    :return: The counts for each bit string measured.
    :rtype: Tuple[]
    '''
measurement_results = measurement_counts

def sample2all(sample: Tensor, n: int, format: str = 'count_vector', jittable: bool = False) -> Any:
    '''
    transform ``sample_int`` or ``sample_bin`` form results to other forms specified by ``format``

    :param sample: measurement shots results in ``sample_int`` or ``sample_bin`` format
    :type sample: Tensor
    :param n: number of qubits
    :type n: int
    :param format: see the doc in the doc in :py:meth:`tensorcircuit.quantum.measurement_results`,
        defaults to "count_vector"
    :type format: str, optional
    :param jittable: only applicable to count transformation in jax backend, defaults to False
    :type jittable: bool, optional
    :return: measurement results specified as ``format``
    :rtype: Any
    '''
def spin_by_basis(n: int, m: int, elements: tuple[int, int] = (1, -1)) -> Tensor:
    """
    Generate all n-bitstrings as an array, each row is a bitstring basis.
    Return m-th col.

    :Example:

    >>> qu.spin_by_basis(2, 1)
    array([ 1, -1,  1, -1])

    :param n: length of a bitstring
    :type n: int
    :param m: m<n,
    :type m: int
    :param elements: the binary elements to generate, default is (1, -1).
    :type elements: Tuple[int, int], optional
    :return: The value for the m-th position in bitstring when going through
        all bitstring basis.
    :rtype: Tensor
    """
def correlation_from_samples(index: Sequence[int], results: Tensor, n: int) -> Tensor:
    '''
    Compute :math:`\\prod_{i\\in \\\\text{index}} s_i (s=\\pm 1)`,
    Results is in the format of "sample_int" or "sample_bin"

    :param index: list of int, indicating the position in the bitstring
    :type index: Sequence[int]
    :param results: sample tensor
    :type results: Tensor
    :param n: number of qubits
    :type n: int
    :return: Correlation expectation from measurement shots
    :rtype: Tensor
    '''
def correlation_from_counts(index: Sequence[int], results: Tensor) -> Tensor:
    '''
    Compute :math:`\\prod_{i\\in \\\\text{index}} s_i`,
    where the probability for each bitstring is given as a vector ``results``.
    Results is in the format of "count_vector"

    :Example:

    >>> prob = tc.array_to_tensor(np.array([0.6, 0.4, 0, 0]))
    >>> qu.correlation_from_counts([0, 1], prob)
    (0.20000002+0j)
    >>> qu.correlation_from_counts([1], prob)
    (0.20000002+0j)

    :param index: list of int, indicating the position in the bitstring
    :type index: Sequence[int]
    :param results: probability vector of shape 2^n
    :type results: Tensor
    :return: Correlation expectation from measurement shots.
    :rtype: Tensor
    '''
