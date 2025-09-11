import pyqpanda3.core as pq

__all__ = ['expval', 'QuantumMeasure', 'ProbsMeasure', 'DensityMatrixFromQstate', 'VN_Entropy', 'Mutal_Info', 'Hermitian_expval', 'Purity']

def expval(machine: pq.CPUQVM, prog: pq.QProg, pauli_str_dict: dict):
    """expval(machine,prog,pauli_str_dict,qlists)
    Expectation value of the supplied Hamiltonian observables

    if the observables are :math:`0.7Z\\otimes X\\otimes I+0.2I\\otimes Z\\otimes I`,
    then ``Hamiltonian`` ``dict`` would be ``{{'Z0, X1':0.7} ,{'Z1':0.2}}`` .

 

    :param machine: machine created by qpanda
    :param prog: quantum program created by qpanda
    :param pauli_str_dict: Hamiltonian observables
    :return: expectation

    Example::

        import pyqpanda3.core as pq
        from pyvqnet.qnn.pq3.measure import expval
        input = [0.56, 0.1]
        m_machine = pq.CPUQVM()

        m_qlist = range(3)
        cir = pq.QCircuit(3)
        cir<<pq.RZ(m_qlist[0],input[0])
        cir<<pq.CNOT(m_qlist[0],m_qlist[1])
        cir<<pq.RY(m_qlist[1],input[1])
        cir<<pq.CNOT(m_qlist[0],m_qlist[2])
        m_prog = pq.QProg(cir)

        pauli_dict  = {'Z0 X1':10,'Y2':-0.543}
        exp2 = expval(m_machine,m_prog,pauli_dict)
        print(exp2)
 
    """
ExpVal = expval
QuantumMeasure = quantum_measure
ProbsMeasure = probs_measure
DensityMatrixFromQstate = densitymatrixfromqstate
Hermitian = hermitian
Hermitian_expval = hermitian_expval
VN_Entropy = vn_entropy
Mutal_Info = mutal_info
Purity = purity
