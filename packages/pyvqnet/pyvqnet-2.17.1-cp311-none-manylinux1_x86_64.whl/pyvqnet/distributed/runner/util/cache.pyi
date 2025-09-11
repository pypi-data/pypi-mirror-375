class Cache:
    """
    Cache the function calls
    """
    def __init__(self, cache_folder, cache_staleness_threshold_in_minutes, parameters_hash) -> None: ...
    def get(self, key): ...
    def put(self, key, val) -> None: ...

def use_cache():
    """
    If used to decorate a function and if fn_cache is set, it will store the
    output of the function if the output is not None. If a function output
    is None, the execution result will not be cached.
    :return:
    """
