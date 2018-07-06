import logging
import sys
import ConfigParser

def singleton(cls):
    instances = {}
    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance()


class StreamToLogger(object):
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

@singleton
class Logger():
    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read('config.ini')
        level = config.get('LOGGER', 'level').strip()

        logging.basicConfig(level=level,
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%d-%m-%y %H:%M:%S',
                            filename=config.get('LOGGER', 'filepath'),
                            filemode='w')
        self.logger = logging.getLogger('tc')
        stdout_logger = logging.getLogger('STDOUT')
        sl = StreamToLogger(stdout_logger, logging.INFO)
        sys.stdout = sl
        stderr_logger = logging.getLogger('STDERR')
        sl = StreamToLogger(stderr_logger, logging.ERROR)
        sys.stderr = sl
