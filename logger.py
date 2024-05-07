import logging
import colorlog


def init_logger(verbose, no_color):
    logger = logging.getLogger('logger')
    if not logger.handlers:
        if verbose == 0:
            logger.setLevel(logging.WARNING)
        elif verbose == 1:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logger.level)

        if no_color:
            formatter = logging.Formatter('%(levelname)s - %(message)s')
        else:
            formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(levelname)-8s%(reset)s %(message)s',
                datefmt=None,
                reset=True,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red',
                },
                secondary_log_colors={},
                style='%'
            )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(module_name):
    return logging.getLogger('logger').getChild(module_name)
