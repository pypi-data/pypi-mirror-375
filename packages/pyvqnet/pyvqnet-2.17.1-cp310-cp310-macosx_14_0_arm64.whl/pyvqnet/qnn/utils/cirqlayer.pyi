from _typeshed import Incomplete
from pyvqnet.qnn.utils.compatible_layer import Compatiblelayer as Compatiblelayer
from pyvqnet.tensor.tensor import AutoGradNode as AutoGradNode, QTensor as QTensor
from pyvqnet.utils.utils import bind_cirq_symbol as bind_cirq_symbol, get_circuit_symbols as get_circuit_symbols, merge_cirq_paramsolver as merge_cirq_paramsolver, validate_compatible_grad as validate_compatible_grad, validate_compatible_input as validate_compatible_input, validate_compatible_output as validate_compatible_output

CoreTensor: Incomplete

class CirqLayer(Compatiblelayer):
    """

    a wrapper to use cirq circuits to forward and backward in the form of vqnet.
    cirq_vqc is a class define the cirq quantum cirquits and its `run` function.
    following examples show how it works.

    this layer only support both input and weights as parameters in circuits.

    :param cirq_vqc: a class defines the cirq circuits's definition,backend,run functions.
    :param para_num: `int` - Number of para_num
    :return: a class can run cirq quantum circuits model.

    Example::

        from pyvqnet.utils.utils import get_circuit_symbols
        class cirq_qvc:

        def __init__(self,simulator = cirq.Simulator (),shots = 1000):

            self._circuit = cirq.Circuit()

            ###define qubits

            q0 = cirq.NamedQubit ('q0')

            ###define varational parameters
            param1 = sympy.symbols('x1')
            param = sympy.symbols('x0')
            param2 = sympy.symbols('x2')
            param3 = sympy.symbols('p1')
            param4 = sympy.symbols('p2')
            param5 = sympy.symbols('p3')
            ###define circuits
            circuit = cirq.Circuit()
            circuit.append(cirq.H(q0))
            circuit.append(cirq.ry(param3)(q0))
            circuit.append(cirq.ry(param4)(q0))
            circuit.append(cirq.ry(param5)(q0))
            circuit.append(cirq.ry(param)(q0))
            circuit.append(cirq.ry(param1)(q0))
            circuit.append(cirq.ry(param2)(q0))
            circuit.append(cirq.measure(q0))
            self._circuit = circuit

            ###define backend
            self._backend = simulator
            ##defien shots
            self._shots = shots

            ###get symbols list
            self._param_symbols_list,self._input_symbols_list = list(
                sorted(get_circuit_symbols(self._circuit)))

        def run(self,symbol_lists):

            ### run simulator
            rlt = self._backend.run(self._circuit,symbol_lists,repetitions = self._shots)

            result = rlt.histogram(key = 'q0')
            counts = np.array(list(result.values()))
            states = np.array(list(result.keys())).astype(float)

            # Compute probabilities for each state
            probabilities = counts / self._shots
            # Get state expectation
            expectation = np.sum(states * probabilities)
            return expectation

        #define cirq circuits class

        cirq_cir = cirq_qvc()

        hybrid = CirqLayer(cirq_cir,para_num = 3)
        x = QTensor([[0.3,0.3,0.3],[0.3,0.3,0.3]])
        x.requires_grad = True
        y = hybrid(x)
        print(y)
        y.backward()
        print(hybrid.m_para.grad)
        print(x.grad)

    """
    def __init__(self, cirq_vqc, para_num) -> None: ...
    def forward(self, x): ...
