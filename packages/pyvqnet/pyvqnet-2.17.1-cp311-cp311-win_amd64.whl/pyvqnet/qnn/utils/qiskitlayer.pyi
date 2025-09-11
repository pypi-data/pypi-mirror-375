from _typeshed import Incomplete
from pyvqnet.qnn.utils.compatible_layer import Compatiblelayer as Compatiblelayer
from pyvqnet.tensor.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor
from pyvqnet.utils.utils import validate_compatible_grad as validate_compatible_grad, validate_compatible_input as validate_compatible_input, validate_compatible_output as validate_compatible_output

CoreTensor: Incomplete

class QiskitLayer(Compatiblelayer):
    """

    a wrapper to use qiskit circuits to forward and backward in the form of vqnet.
    qiskit_circuits is a class define the qiskit QuantumCircuits and its run function.
    following examples show how it works.

    :param qiskit_circuits: a class defines the qiskit circuits's definition,backend,run functions.
    :param para_num: `int` - Number of para_num
    :return: a class can run qiskit model

    Example::

        class QuantumCircuit:
            def __init__(self, n_qubits, backend, shots):
                # --- Circuit definition ---
                self.n_qubits = n_qubits
                self._circuit = qiskit.QuantumCircuit(n_qubits)

                all_qubits = [i for i in range(n_qubits)]

                self.theta = [qiskit.circuit.Parameter('theta1'),
                                qiskit.circuit.Parameter('theta2'),
                                qiskit.circuit.Parameter('theta3'),
                                qiskit.circuit.Parameter('theta4')]


                all_qubits = [i for i in range(n_qubits)]

                self.input = [qiskit.circuit.Parameter('input1'),
                                qiskit.circuit.Parameter('input2'),
                                qiskit.circuit.Parameter('input3'),
                                qiskit.circuit.Parameter('input4')]

                self._circuit.h(all_qubits)
                self._circuit.barrier()
                self._circuit.rz(self.input[0], 0)
                self._circuit.rz(self.input[1], 1)
                self._circuit.rz(self.input[2], 2)
                self._circuit.rz(self.input[3], 3)

                self._circuit.ry(self.theta[0], all_qubits)
                self._circuit.ry(self.theta[1], all_qubits)
                self._circuit.ry(self.theta[2], all_qubits)
                self._circuit.ry(self.theta[3], all_qubits)
                self._circuit.measure_all()

                self.backend = backend
                self.shots = shots

            def run(self,x,w):

                params = dict(zip(self.input, x))
                c1 = self._circuit.assign_parameters(params)

                params = dict(zip(self.theta, w))
                c2 = c1.assign_parameters(params)

                job = self.backend.run(c2,shots=self.shots)
                result = job.result().get_counts()

                probs = {}
                for i in range(2**self.n_qubits):
                    probs[i] = 0

                for k in result.keys():
                    k_dec = int(k,2)

                    probs[k_dec] = result[k]/self.shots

                probabilities = np.array(list(probs.values()))
                return probabilities

        simulator = qiskit.Aer.get_backend('aer_simulator')
        num_qubits  = 4
        num_slots = 100
        para_num = 4

        circuit = QuantumCircuit(num_qubits, simulator, num_slots)

        qlayer = QiskitLayer(circuit,para_num)
        x = tensor.ones([2,4])
        x.requires_grad = True
        y = qlayer(x)
        y.backward()

    """
    def __init__(self, qiskit_circuits, para_num) -> None: ...
    def forward(self, x): ...

class QiskitLayerV2(Compatiblelayer):
    """
        a wrapper to use qiskit circuits to forward and backward in the form of vqnet.
        qiskit_circuits is a class define the qiskit QuantumCircuits and its run function.
        following examples show how it works.

        :param qiskit_circuits: a class defines the qiskit circuits's definition,
         backend,run functions.
        :param para_num: `int` - Number of para_num
        :return a module can run qiskit circuits

        Example::

            import qiskit

            class QISKIT_VQC:

                def __init__(self, n_qubits, backend, shots):
                    # --- Circuit definition ---
                    qctl = QuantumRegister(4)
                    qc = ClassicalRegister(1)
                    self.qc = qc
                    self.n_qubits = n_qubits

                    all_qubits = [i for i in range(n_qubits)]
                    self.all_qubits= all_qubits

                    #self._circuit.measure(0,0)
                    self.backend = backend
                    self.shots = shots

                def run(self,**kwargs):

                    x  = kwargs['x']
                    weights  = kwargs['w']

                    weights = weights.astype(np.float64)
                    x = x.astype(np.float64)

                    sum_feature = np.power(np.sum([t**2 for t in x]),0.5)
                    normalize_feat = x/sum_feature

                    self._circuit = qiskit.QuantumCircuit(QuantumRegister(4))

                    self.theta = weights.reshape([4,6])
                    self._circuit.initialize(normalize_feat, [0,1,2,3])

                    for i in range(self.n_qubits):
                        self._circuit.rz(self.theta[i,0], i)
                        self._circuit.ry(self.theta[i,1], i)
                        self._circuit.rz(self.theta[i,2], i)

                    for d in range(3, 6):
                        for i in range(self.n_qubits-1):
                            self._circuit.cnot(i, i + 1)
                        self._circuit.cnot(self.n_qubits-1, 0)
                        for i in range(self.n_qubits):
                            self._circuit.ry(self.theta[i,d], i)

                    #simulator = qiskit.Aer.get_backend('statevector_simulator')
                    result = qiskit.execute(self._circuit,self.backend).result()
                    pauliZ = Pauli('IIIZ')

                    result_statevec = Statevector(result.get_statevector())
                    Expectation = np.real(result_statevec.expectation_value(pauliZ,))
                    return Expectation

            #define qiskit circuits class
            simulator = qiskit.Aer.get_backend('statevector_simulator')
            circuit = QISKIT_VQC(4, simulator, 1000)

            class Model_qiskit(Module):
                def __init__(self):
                    super(Model_qiskit, self).__init__()
                    self.qvc = QiskitLayerV2(circuit,24)

                def forward(self, x):

                    return self.qvc(x)*0.5 + 0.5

    """
    def __init__(self, qiskit_circuits, para_num) -> None: ...
    def forward(self, x): ...
