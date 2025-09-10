import logging
import os
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pillar.client import Pillar


class Logger:
    """
    Logger for the Pillar SDK.

    This class handles logging for the Pillar SDK. It uses a standard Python logger
    for output and will eventually send critical logs to the Pillar API.
    """

    def __init__(
        self,
        pillar: "Pillar",
        logger: logging.Logger | None = None,
        disabled: bool = False,
    ):
        """
        Initialize the Logger with a Pillar client and optional Python logger.

        Args:
            pillar: The Pillar client to use for logging.
            logger: An optional Python logger to use. If None, logs are only
                   processed for future Pillar API integration.
            disabled: If True, all logging operations will be disabled.
        """
        self.pillar = pillar
        self._logger = logger
        self._disabled = disabled

    def set_logger(self, logger: logging.Logger | None = None) -> None:
        """
        Set or update the Python logger used by this Logger.

        Args:
            logger: A Python logging.Logger instance, or None to disable logging.
        """
        self._logger = logger

    def disable(self) -> None:
        """Completely disable all logging operations."""
        self._disabled = True
        self._logger = None

    def enable(self) -> None:
        """Enable logging operations."""
        self._disabled = False

    def _log(self, level: int, message: str, trace: str | None = None, **kwargs) -> None:
        """
        Log a message.

        Args:
            level: The logging level
            message: The message to log
            trace: Optional stack trace information
        """
        # If logging is disabled, do nothing
        if self._disabled:
            return

        # Log to the Python logger if one is set
        if self._logger:
            try:
                self._logger.log(level, message, **kwargs)
                if trace:
                    self._logger.log(level, trace, **kwargs)
            except Exception as e:
                # Avoid crashing if Python logger fails
                try:
                    # Try to use standard logging as fallback
                    logging.error(f"Failed to log using custom logger: {e}")
                except Exception:
                    pass

        # Forward to the Pillar client's _log method for future API integration
        try:
            self.pillar._log(level, message, trace, **kwargs)
        except Exception:
            # Silently ignore errors in the client's _log method
            pass

    def debug(self, message: str, **kwargs) -> None:
        """Log a debug message."""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log an info message."""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log a warning message."""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """
        Log an error message with stack trace.

        This automatically captures the current exception traceback
        if there is an active exception being handled.
        """
        trace = traceback.format_exc()
        trace_to_log = None if trace == "NoneType: None\n" else trace  # No active exception
        self._log(logging.ERROR, message, trace_to_log, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """
        Log a critical message with stack trace.

        This automatically captures the current exception traceback
        if there is an active exception being handled.
        """
        trace = traceback.format_exc()
        trace_to_log = None if trace == "NoneType: None\n" else trace  # No active exception
        self._log(logging.CRITICAL, message, trace_to_log, **kwargs)


def create_logger(
    name: str = "pillar",
    log_level: int = logging.WARNING,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: str | None = None,
    console: bool = True,
) -> logging.Logger:
    """
    Create a properly configured logger for use with Pillar.

    This utility function makes it easy to create a logger that can be passed
    to a Pillar instance for debugging and monitoring.

    Args:
        name: Name of the logger (default: "pillar")
        log_level: Minimum log level to capture (default: logging.WARNING)
        log_format: Format string for log messages
        log_file: Optional file path to write logs to
        console: Whether to output logs to console (default: True)

    Returns:
        A configured logging.Logger instance

    Example:
        ```python
        from pillar.logging import create_logger
        from pillar.client import Pillar

        # Create a logger that writes to both console and file
        logger = create_logger(
            name="my_app",
            log_level=logging.DEBUG,
            log_file="pillar.log"
        )

        # Pass it to Pillar on initialization
        pillar = Pillar(
            api_key="...",
            debug_logger=logger
        )

        # Or set it later
        pillar.set_logger(logger)
        ```
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Add handlers
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
