# backend/app/core/logging.py
import logging
import sys

# ANSI escape color constants
GREY = "\x1b[38;20m"
CYAN = "\x1b[36;20m"
YELLOW = "\x1b[33;20m"
RED = "\x1b[31;20m"
BOLD_RED = "\x1b[31;1m"
GREEN = "\x1b[32;20m"
RESET = "\x1b[0m"


class ColorFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: GREY + "%(asctime)s [%(levelname)s] (%(name)s): %(message)s" + RESET,
        logging.INFO: CYAN + "%(asctime)s [INFO] " + RESET + "%(message)s",
        logging.WARNING: YELLOW + "%(asctime)s [WARN] " + RESET + "%(message)s",
        logging.ERROR: RED + "%(asctime)s [ERROR] " + RESET + "%(message)s",
        logging.CRITICAL: BOLD_RED + "%(asctime)s [CRITICAL] " + RESET + "%(message)s",
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)


def setup_logging(log_level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColorFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    # Silence chatty third-party libraries
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
