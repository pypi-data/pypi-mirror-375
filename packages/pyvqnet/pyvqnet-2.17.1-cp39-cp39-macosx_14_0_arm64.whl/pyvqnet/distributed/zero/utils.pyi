from _typeshed import Incomplete

log_levels: Incomplete

class LoggerFactory:
    @staticmethod
    def create_logger(name: Incomplete | None = None, level=...):
        """create a logger

        Args:
            name (str): name of the logger
            level: level of logger

        Raises:
            ValueError is name is None
        """

logger: Incomplete
