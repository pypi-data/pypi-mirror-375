""" Utilities for logging in Neurotorch """
import logging
import sys
import threading
import types
from typing import Iterable
from pathlib import Path
from logging.handlers import RotatingFileHandler
import atexit
import os
import io

logger = logging.getLogger("NeurotorchMZ")
""" The root logger for NeurotorchMZ. The level defaults to DEBUG to allow derived Handlers (e.g. StreamHandler, RotatingFileHandler) to set custom (higher) levels """

debugging: bool = False
""" If set to true, logs of level DEBUG are printed to the console"""

_fmt = logging.Formatter('[%(asctime)s %(levelname)s]: %(message)s')
_fmtFile = logging.Formatter('[%(asctime)s|%(levelname)s|%(module)s]: %(message)s')

stream_logging_handler = logging.StreamHandler(stream=sys.stdout)
""" The default logging handler to the user console """
stream_logging_handler.setFormatter(_fmt)
stream_logging_handler.setLevel(logging.ERROR)

file_logging_handler: RotatingFileHandler
""" The default file logging handler """

logger.setLevel(logging.DEBUG)
logger.addHandler(stream_logging_handler) 


class StdOutCatcher(io.IOBase):

    def writable(self) -> bool:
        return True

    def write(self, msg: str) -> int:
        global stream_logging_handler, file_logging_handler
        stream_logging_handler.stream.write(msg)
        if hasattr(sys.modules[__name__], "file_logging_handler"):
            file_logging_handler.stream.write(msg)
        self.flush()
        return len(msg)

    def flush(self):
        global stream_logging_handler, file_logging_handler
        super().flush()
        stream_logging_handler.stream.flush()
        if hasattr(sys.modules[__name__], "file_logging_handler"):
            file_logging_handler.stream.flush()

logged_std_out = StdOutCatcher()
""" io.TextIOBase object used to catch stream output for the logger """

def init_file_handler(path: Path) -> None:
    """ Should be called from the settings handler when the AppData Path is set to initialize the file handler for logging """
    global file_logging_handler, _fmtFile, logger
    file_logging_handler = RotatingFileHandler(path, mode="a", maxBytes=(1024**2), backupCount=10)
    file_logging_handler.setFormatter(_fmtFile)
    file_logging_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_logging_handler)
    if "NEUROTORCH_DEBUG" in os.environ:
        start_debugging()

def log_exceptions_hook(exc_type: type[BaseException], exc_value: BaseException, exc_traceback: types.TracebackType | None = None) -> None:
    global logger
    logger.exception(f"{exc_type.__name__}:", exc_info=(exc_type, exc_value, exc_traceback))
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

def thread_exceptions_hook(except_hook_args: threading.ExceptHookArgs):
    global logger
    exc_type, exc_value, exc_traceback, thread = except_hook_args.exc_type, except_hook_args.exc_value, except_hook_args.exc_traceback, except_hook_args.thread
    logger.exception(f"{exc_type.__name__} in thread '{thread.name if thread is not None else ''}':", 
                     exc_info=(exc_type, exc_value if exc_value is not None else BaseException(), exc_traceback))
    sys.__excepthook__(exc_type, exc_value if exc_value is not None else BaseException(), exc_traceback)

def start_debugging():
    """ Starts the debugging of not started yet """
    global debugging
    if debugging:
        return
    debugging = True
    stream_logging_handler.setLevel(logging.DEBUG)
    logger.debug(f"Started debugging")

sys.excepthook = log_exceptions_hook
threading.excepthook = thread_exceptions_hook

atexit.register(lambda: logger.info("Stopping Neurotorch"))