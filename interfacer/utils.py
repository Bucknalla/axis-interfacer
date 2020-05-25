import logging
from colorlog import ColoredFormatter
import os
class log(object):
    def __init__(self, name, enable=False, testing=False):
        self.logger = self.init_logger(name, enable, testing=testing)

    def init_logger(self, dunder_name, enable, testing) -> logging.Logger:


        stdout_formatter = ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG':    'purple',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red',
            }
        )


        logger = logging.getLogger(__package__+'.'+dunder_name)

        if not enable:
            logger.disabled = True
        if not os.path.exists('.log'):
            os.makedirs('.log')        
        logger.setLevel(logging.DEBUG)

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler('.log/interfacer.log')
        c_handler.setLevel(logging.ERROR)
        f_handler.setLevel(logging.INFO)

        f_format = logging.Formatter('%(asctime)s - %(name)-20s - %(levelname)-8s - %(message)s')
        c_handler.setFormatter(stdout_formatter)
        f_handler.setFormatter(f_format)

        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

        return logger

if __name__ == '__main__':
    logger = log('test', enable=True, testing=True)
    # logger.logger.disabled = False
    logger.logger.debug('debug')
    logger.logger.warning('warning')

    logger.logger.error('error')
    logger.logger.debug('Ouch!')

