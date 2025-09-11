from _typeshed import Incomplete

class OriginIR_Parser:
    opname: str
    blank: str
    qid: str
    cid: str
    comma: str
    lbracket: str
    rbracket: str
    parameter: str
    regexp_1q_str: Incomplete
    regexp_2q_str: Incomplete
    regexp_3q_str: Incomplete
    regexp_2q1P_str: Incomplete
    regexp_1q1p_str: Incomplete
    regexp_1q2p_str: Incomplete
    regexp_1q3P_str: Incomplete
    regexp_measure_str: Incomplete
    regexp_barrier_str: Incomplete
    regexp_control_str: Incomplete
    regexp_control: Incomplete
    regexp_1q: Incomplete
    regexp_2q: Incomplete
    regexp_3q: Incomplete
    regexp_1q1p: Incomplete
    regexp_1q2p: Incomplete
    regexp_1q3p: Incomplete
    regexp_meas: Incomplete
    regexp_2q1p: Incomplete
    regexp_barrier: Incomplete
    regexp_qid: Incomplete
    def __init__(self) -> None: ...
    @staticmethod
    def handle_1q(line): ...
    @staticmethod
    def handle_2q(line): ...
    @staticmethod
    def handle_3q(line): ...
    @staticmethod
    def handle_1q1p(line): ...
    @staticmethod
    def handle_2q1p(line): ...
    @staticmethod
    def handle_1q2p(line): ...
    @staticmethod
    def handle_1q3p(line): ...
    @staticmethod
    def handle_measure(line): ...
    @staticmethod
    def handle_barrier(line): ...
    @staticmethod
    def handle_control(line):
        '''
        Parses the provided line to extract control qubits information and the type of control operation (CONTROL/ENDCONTROL).

        Returns:
        - tuple: A tuple where the first element is the control operation type ("CONTROL" or "ENDCONTROL")
                 and the second element is a list containing the parsed control qubits.
        
        Note:
        This function assumes that the `regexp_control` regular expression is defined and matches
        the CONTROL or ENDCONTROL pattern in the OriginIR language.
        '''
    @staticmethod
    def parse_line(line): ...

def opcode_to_line(opcode): ...

class OriginIR_BaseParser:
    n_qubit: Incomplete
    n_cbit: Incomplete
    program_body: Incomplete
    raw_originir: Incomplete
    def __init__(self) -> None: ...
    def parse(self, originir_str) -> None: ...
    def to_extended_originir(self): ...
    @property
    def originir(self): ...
