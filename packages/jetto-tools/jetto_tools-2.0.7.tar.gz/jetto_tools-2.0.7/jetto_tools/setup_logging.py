import logging
import time

TRACE_LEVEL_NUM = 5
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        # Yes, logger takes its '*args' as 'args'.
        self._log(TRACE_LEVEL_NUM, message, args, **kws)
        logging.Logger.trace = trace
logging.Logger.trace = trace
logging.TRACE = TRACE_LEVEL_NUM

class PrettyFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    light_grey = "\x1b[38;5;251m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    format = "%(asctime)s [%(levelname)s] %(message)s @%(filename)s:%(lineno)d"
    default_time_format = "%H:%M:%S"

    FORMATS = {
        logging.TRACE: light_grey + format + reset,
        logging.DEBUG: light_grey + format + reset,
        logging.INFO: format,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        formatter.formatTime = self.formatTime
        return formatter.format(record)

    def formatTime(self, record, datefmt=None, print_ms=False):
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime(self.default_time_format, ct)
            if print_ms:
                s = self.default_msec_format % (t, record.msecs)
            else:
                s = t
        return s

def test_messages():
    logger = logging.getLogger('qualikiz_tools.testlogger')
    logger.setLevel(logging.TRACE)
    logger.trace('Trace message')
    logger.debug('Debug message')
    logger.info('Info message')
    logger.warning('Warning message')
    logger.error('Error message')
    logger.critical('Critical message')


# Log to console by default, and output it all
logger = logging.getLogger('jetto_tools')
ch = logging.StreamHandler()
ch.setLevel(logging.TRACE)
ch.setFormatter(PrettyFormatter())
logger.addHandler(ch)

if __name__ == '__main__':
    test_messages()
