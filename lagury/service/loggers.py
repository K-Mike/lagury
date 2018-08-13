import logging
import time
import os
import sys
import threading
from cloghandler import ConcurrentRotatingFileHandler


def set_logging(logger_path, debug=True, force=False, log_name_level=2):
    """
    Create multiprocessing-safe logger
    :param logger_path: path of the logger
    :param debug: (Optional) include debug messages in the output
    :param force: (Optional) force logger re-creation
    :param log_name_level: (Optional) number of path components to use as logger's name (1 stands for filename)
    :return: logging.logger object
    """
    logger_path = os.path.normpath(logger_path)
    logger_name = '_'.join(logger_path.split(os.sep)[-log_name_level:])

    logger = logging.getLogger(logger_name)

    if logger.hasHandlers() and not force:
        return logger
    else:
        logger.handlers = []

    logfile = ConcurrentRotatingFileHandler(
        logger_path,
        maxBytes=100 * 1024 * 1024,
        backupCount=10
    )
    logfile.setLevel((logging.DEBUG if debug else logging.INFO))

    handlers = [logfile]

    stream = logging.StreamHandler()
    stream.setLevel(logging.DEBUG)
    handlers.append(stream)

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def logging_timeit(logger, format_str, result_funcs=None):
    """
    Timeit logging decorator with argument-based format string

    :param logger: info-level logger
    :param format_str: format string for logger, use execution time as "_time" format argument
    :param result_funcs: dict of "format argument name / function of result" pairs
    """
    result_funcs = result_funcs or {}

    def decorator(func):
        def wrapper(*args, **kwargs):
            started_time = time.time()

            result = func(*args, **kwargs)
            result_args = {name: res_func(result) for name, res_func in result_funcs.items()}

            execution_time = time.time() - started_time

            kwargs.update(result_args)
            logger.info(format_str.format(*args, _time=execution_time, **kwargs))

            return result
        return wrapper
    return decorator


class StreamToLogger:
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


class PipeToLogger(threading.Thread):
    def __init__(self, logger, log_level=logging.INFO):
        """Setup the object with a logger and a log level and start the thread"""
        threading.Thread.__init__(self)
        self.daemon = False
        self.log_level = log_level
        self.logger = logger
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.start()

    def fileno(self):
        """Return the write file descriptor of the pipe"""
        return self.fdWrite

    def run(self):
        """Run the thread, logging everything"""
        for line in iter(self.pipeReader.readline, ''):
            self.logger.log(self.log_level, line.strip('\n'))

        self.pipeReader.close()

    def close(self):
        """Close the write end of the pipe"""
        os.close(self.fdWrite)


def wrap_sys_in_logger(logger):
    """Redirect system output to the given logger"""
    sys.stdout = StreamToLogger(logger, logging.INFO)
    sys.stderr = StreamToLogger(logger, logging.ERROR)
