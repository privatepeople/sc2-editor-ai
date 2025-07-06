# Python Standard Library imports
import logging
import logging.handlers
import os
from pathlib import Path


class ApplicationLogging:
    """A class to handle application logging with file rotation and console output."""

    def __init__(
        self,
        name: str = "app",
        level: int = logging.INFO,
        log_file: str | Path = Path(__file__).parents[1] / "logs" / "app.log",
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 7,
        console_output: bool = True,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        formatter = logging.Formatter(
            "%(levelname)s - %(asctime)s - %(pathname)s - %(funcName)s - %(message)s"
        )

        # Create log directory if it doesn't exist
        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

        # Create file handler with rotation
        if log_file:
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_file, maxBytes=max_file_size, backupCount=backup_count
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Create console handler
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
