import inspect
import logging


def customlogger(logLevel=logging.DEBUG):
    """
    gets the name of the class/method from where this method is called.
    A list of named tuples FrameInfo(frame, filename, lineno, function, 
    code_context, index) is returned.
    so, 1,3 is filename and function respectively.

    """
    loggerName = inspect.stack()[1][3]
    logger = logging.getLogger(loggerName)

    # by default, log all messages
    logger.setLevel(logging.DEBUG)

    fileHandler = logging.FileHandler("logs/automation.log", mode='a')
    fileHandler.setLevel(logLevel)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    return logger


class CustomLogger:
    log = customlogger(logging.DEBUG)
