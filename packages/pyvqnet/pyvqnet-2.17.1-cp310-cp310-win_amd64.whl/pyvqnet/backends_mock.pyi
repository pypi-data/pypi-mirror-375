from unittest.mock import MagicMock

class TorchMock(MagicMock):
    def __getattr__(self, name): ...
