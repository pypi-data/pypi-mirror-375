from ...tensor import QTensor as QTensor
from .qcircuit import MultiControlledX as MultiControlledX, PauliZ as PauliZ, QFT as QFT, QMachine as QMachine, RZ as RZ, VQC_BasisEmbedding as VQC_BasisEmbedding, cnot as cnot, controlledphaseshift as controlledphaseshift, crz as crz, multi_control_rz as multi_control_rz, multicontrolledx as multicontrolledx, phaseshift as phaseshift, rz as rz, swap as swap, toffoli as toffoli
from .qop import QModule as QModule

def vqnet_add_k_fourier_adjoint(qm, k, wires) -> None: ...
def vqnet_add_k_fourier(qm, k, wires) -> None: ...
def vqnet_add_k_phase_fourier(qm, k, wires) -> None: ...
def vqnet_add_k_phase_fourier_control(qm, k, wires, control_wires) -> None: ...
def vqnet_add_k_phase_fourier_adjoint(qm, k, wires) -> None: ...
def vqc_qft_add_to_register(q_machine, m, k) -> None:
    """
    Adding a number to a register

    .. math:: \text{Sum(k)}\x0bert m \rangle = \x0bert m + k \rangle.

    The procedure to implement this unitary operation is the following:
    (1). Convert the state from the computational basis into the Fourier basis by applying the QFT to the :math:`\x0bert m \rangle` state via the `QFT` operator.
    (2). Rotate the :math:`j`-th qubit by the angle :math:`\x0crac{2k\\pi}{2^{j}}` using the :math:`R_Z` gate, which leads to the new phases, :math:`\x0crac{2(m + k)\\pi}{2^{j}}`.
    (3). Apply the QFT inverse to return to the computational basis and obtain :math:`m+k`.

    :param q_machine: quantum machine for simulation. 
    :param m: classic integar to embedded in register.
    :param k: classic integar to added to the register.

    Example::

        import numpy as np
        from pyvqnet.qnn.vqc import QMachine,Samples, vqc_qft_add_to_register
        dev = QMachine(4)
        vqc_qft_add_to_register(dev,3, 7)
        ma = Samples()
        y = ma(q_machine=dev)
        print(y)
        #[[1,0,1,0]]
    """
def vqc_qft_mul(q_machine, m, k, wires_m, wires_k, wires_solution) -> None:
    """
    Apply Multiplying qubits quantum opertation.

    .. math:: \text{Mul}\x0bert m \rangle \x0bert k \rangle \x0bert 0 \rangle = \x0bert m \rangle \x0bert k \rangle \x0bert m\\cdot k \rangle

    :param q_machine: quantum machine for simulation. 
    :param m: classic integar to embedded in register as the lhs.
    :param k: classic integar to embedded in the register as the rhs.
    :param wires_m: index of qubits to encode m.
    :param wires_k: index of qubits to encode k.
    :param wires_solution: index of qubits to encode solution.


    Example::

        import numpy as np
        from pyvqnet.qnn.vqc import QMachine,Samples, vqc_qft_mul
        wires_m = [0, 1, 2]           # qubits needed to encode m
        wires_k = [3, 4, 5]           # qubits needed to encode k
        wires_solution = [6, 7, 8, 9, 10]  # qubits needed to encode the solution
        
        dev = QMachine(len(wires_m) + len(wires_k) + len(wires_solution))

        vqc_qft_mul(dev,3, 7, wires_m, wires_k, wires_solution)


        ma = Samples(wires=wires_solution)
        y = ma(q_machine=dev)
        print(y)
        #[[1,0,1,0,1]]

    """
def vqnet_add_k_fourier_control(qm, k, wires, control) -> None: ...
def vqc_qft_add_two_register(q_machine, m, k, wires_m, wires_k, wires_solution) -> None:
    """
    Adding two different registers.

    .. math:: \text{Sum}_2\x0bert m \rangle \x0bert k \rangle \x0bert 0 \rangle = \x0bert m \rangle \x0bert k \rangle \x0bert m+k \rangle

    In this case, we can understand the third register (which is initially
    at :math:`0`) as a counter that will tally as many units as :math:`m` and
    :math:`k` combined. The binary decomposition will
    make this simple. If we have :math:`\x0bert m \rangle = \x0bert \\overline{q_0q_1q_2} \rangle`, we will
    have to add :math:`1` to the counter if :math:`q_2 = 1` and nothing
    otherwise. In general, we should add :math:`2^{n-i-1}` units if the :math:`i`-th
    qubit is in state :math:`\x0bert 1 \rangle` and 0 otherwise.

    :param q_machine: quantum machine for simulation. 
    :param m: classic integar to embedded in register as the lhs.
    :param k: classic integar to embedded in the register as the rhs.
    :param wires_m: index of qubits to encode m.
    :param wires_k: index of qubits to encode k.
    :param wires_solution: index of qubits to encode solution.

    Example::

        import numpy as np
        from pyvqnet.qnn.vqc import QMachine,Samples, vqc_qft_add_two_register
        wires_m = [0, 1, 2]           # qubits needed to encode m
        wires_k = [3, 4, 5]           # qubits needed to encode k
        wires_solution = [6, 7, 8, 9, 10]  # qubits needed to encode the solution

        dev = QMachine(len(wires_m) + len(wires_k) + len(wires_solution))

        vqc_qft_add_two_register(dev,3, 7, wires_m, wires_k, wires_solution)

        ma = Samples(wires=wires_solution)
        y = ma(q_machine=dev)
        print(y)
        #[[1,0,1,0]]

    """
def MAJ(qm, a, b, c) -> None: ...
def MAJ_CONTROL(qm, a, b, c, control) -> None: ...
def MAJ_dagger(qm, a, b, c) -> None: ...
def UMA_CONTROL(qm, a, b, c, control) -> None: ...
def UMA(qm, a, b, c) -> None: ...
def UMA_dagger(qm, a, b, c) -> None: ...
def QAdder(qm: QMachine, m: int, k: int, adder1: list, adder2: list, c: list | int, is_carry: list | int):
    """
    
    Use MAJ and UMA to calculate two positive integer addition.
    The result will store in `adder1`, and carry is store in `is_carry`.

    :param qm:qmachine.
    :param m: adder opertaor1.
    :param k: adder opertaor2.
    :param adder1: qubits index to x embedding m.
    :param adder2: qubits index to x embedding k.
    :param c: Ancillary qubit index.
    :param is_carry: qubits index to store carry.
    """
def shift(qm: QMachine, a: list): ...
def shift_dagger(qm: QMachine, a: list): ...
def QMultiplier(qm, lhs, rhs, a, b, k, d) -> None:
    """
    
    Use MAJ and UMA to calculate two positive integer multiplier.
    The result will store in `d` .

    :param qm:qmachine.
    :param m: multiplier opertaor1.
    :param k: multiplier opertaor2.
    :param a: qubits index to x embedding m.
    :param b: qubits index to x embedding k.
    :param k: Ancillary qubit index.
    :param d: qubits index to store result.

    Example::

        from pyvqnet.qnn.vqc import QMultiplier,QMachine,Samples
        import numpy as np

        wires_m = [0,1]
        wires_k = [2,3]
        wires_s = [4,5,6]
        wires_c = [7,8,9,10]
        dev = QMachine(len(wires_m) + len(wires_k) + len(wires_c) + len(wires_s))
    
        QMultiplier(dev,2,3,wires_m,wires_k,wires_s,wires_c)

        m = Samples(wires=wires_c)
        y = m(q_machine=dev)

    """
