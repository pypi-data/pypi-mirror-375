from _typeshed import Incomplete

class CombinationMap:
    n_qubits: int
    def __init__(self) -> None: ...
    def get_combinations(self): ...

class QuantumNeuron:
    """
    Class for the quantum perceptron algorithm: An aritifical neuron implemented on an actual quantum processor

    Example::
        perceptron = QuantumNeuron()

        training_label, test_label = perceptron.gen_4bitstring_data()

        trained_para = perceptron.train(training_label, test_label)

        perceptron.pred(test_label, trained_para)
    """
    n_qubits: int
    qvm: Incomplete
    qubits: Incomplete
    cubits: Incomplete
    trial_num: int
    cmap: Incomplete
    training_data_cir_map: Incomplete
    test_data_cir_map: Incomplete
    random_sample_neg_num: int
    def __init__(self) -> None: ...
    def get_gate_combinations(self): ...
    def random_split_data(self, cir_dicts, label_dicts): ...
    def gen_4bitstring_data(self):
        """
        generate 4 bit bitstring data for pattern recognition
        generate pattern 0 :
            [
            [1.0000000, 1.0000000, 1.0000000, 1.0000000],
            [1.0000000, 1.0000000, 0.0000000, 1.0000000],
            [1.0000000, 0.0000000, 0.0000000, 0.0000000],
            [1.0000000, 1.0000000, 0.0000000, 1.0000000]
            ]
        generate pattern 1 :
            [
            [1.0000000, 1.0000000, 0.0000000, 1.0000000],
            [1.0000000, 0.0000000, 0.0000000, 0.0000000],
            [1.0000000, 1.0000000, 0.0000000, 1.0000000],
            [1.0000000, 1.0000000, 1.0000000, 1.0000000]
            ]
        """
    def Hypergraph_state_cicuits(self, z_position, control_z_positon, control_2_z_positon, control_3_z_positon, flag): ...
    def active_function(self, input_circuits, weight_circuits): ...
    def get_predict(self, in_vector, w_vector, input_dataset, weight_dataset, label: int = 0): ...
    def update(self, in_vector, w_vector, pred, input_dataset, weight_dataset, training_label): ...
    def gen_candidate_circuits(self, control_z_combinations_list): ...
    def get_circuit_state(self, data_circuits_input, data_circuits_weight): ...
    def train(self, training_label, test_label: Incomplete | None = None):
        """
        use bitstring train data and label to find the best quantum circuits.

        :param training_label: dict contains bitstring data and corresponding labels 0 or 1.
        :param test_label: dict contains bitstring data and corresponding labels 0 or 1 for test,default:None.
        :return: found weight vector.
        """
    def pred(self, test_label, found_weight):
        """
        Use test data and found_weight to evaliation
        :param test_label: a dict contains test data bitstring and labels 0 or 1.
        :param found_weights: found weights from train()

        """
