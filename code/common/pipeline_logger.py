import logging
import sys


class PipelineLogger:
    """
    Simple singleton logging instance for all Python components.
    """

    _log = None

    @staticmethod
    def get_logger() -> logging.Logger:
        if not PipelineLogger._log:
            PipelineLogger._log = logging.getLogger()
            PipelineLogger._log.setLevel(logging.DEBUG)

            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            PipelineLogger._log.addHandler(handler)
        return PipelineLogger._log

    @staticmethod
    def add_file_logger(log_level: str, log_path: str):
        log = PipelineLogger.get_logger()
        log_level_enum = logging.getLevelName(log_level)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(log_level_enum)
        log.addHandler(file_handler)
        log.debug(f"Logging at level {log_level} into file: {log_path}")
