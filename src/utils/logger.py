import logging
import sys
from typing import Optional


class LoggerSetup:
    @staticmethod
    def setup(
        level: str = "INFO",
        log_file: Optional[str] = None,
        log_format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ) -> None:
        """
        Configure logging for the application.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path to write logs to
            log_format: Format string for log messages
        """
        # Convert string level to logging constant
        numeric_level = getattr(logging, level.upper(), logging.INFO)

        handlers = []

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(console_handler)

        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(log_format))
            handlers.append(file_handler)

        # Configure root logger
        logging.basicConfig(
            level=numeric_level,
            handlers=handlers,
            format=log_format
        )
