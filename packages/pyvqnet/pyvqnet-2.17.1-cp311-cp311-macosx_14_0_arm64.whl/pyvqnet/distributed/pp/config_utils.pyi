import json
from functools import reduce as reduce

class ScientificNotationEncoder(json.JSONEncoder):
    """
    This class overrides ``json.dumps`` default formatter.

    This version keeps everything as normal except formats numbers bigger than 1e3 using scientific notation.

    Just pass ``cls=ScientificNotationEncoder`` to ``json.dumps`` to activate it

    """
    def iterencode(self, o, _one_shot: bool = False, level: int = 0): ...

class DeepSpeedConfigObject:
    """
    For json serialization
    """
    def repr(self): ...

def get_scalar_param(param_dict, param_name, param_default_value): ...
def get_list_param(param_dict, param_name, param_default_value): ...
def get_dict_param(param_dict, param_name, param_default_value): ...
def dict_raise_error_on_duplicate_keys(ordered_pairs):
    """Reject duplicate keys."""
