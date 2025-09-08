"""Logging utilities for fitscube."""

from __future__ import annotations

import io
import logging

logging.captureWarnings(True)

# Following guide from gwerbin/multiprocessing_logging.py
# https://gist.github.com/gwerbin/e9ab7a88fef03771ab0bf3a11cf921bc

formatter = logging.Formatter(
    fmt="[%(threadName)s] %(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# pylint: disable=W0621
class TqdmToLogger(io.StringIO):
    """
    Output stream for TQDM which will output to logger module instead of
    the StdOut.
    """

    logger = None
    level = None
    buf = ""

    def __init__(self, logger: logging.Logger | None, level: int | None = None) -> None:
        super().__init__()
        self.logger = logger
        self.level = level or logging.INFO

    def write(self, buf: str) -> int:
        self.buf = buf.strip("\r\n\t ")
        return len(buf)

    def flush(self) -> None:
        if self.logger is not None and isinstance(self.level, int):
            self.logger.log(self.level, self.buf)


logger = logging.getLogger("fitscube")


def set_verbosity(verbosity: int) -> None:
    """Set the logger verbosity.

    Args:
        logger (logging.Logger): The logger
        verbosity (int): Verbosity level
    """
    if verbosity == 0:
        level = logging.WARNING
    elif verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG
    else:
        level = logging.CRITICAL

    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(level)
    logger.addHandler(ch)


TQDM_OUT = TqdmToLogger(logger, level=logging.INFO)
