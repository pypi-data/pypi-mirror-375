from unittest.mock import MagicMock

class QubitReorderMock(MagicMock):
    def __getattr__(self, name): ...
