import logging
import sys


def setup_logging(
        level: int = logging.INFO,
        log_file: str = '.'
):
    logger = logging.getLogger()
    logger.setLevel(level)

    # Avoid duplicate logs if called twice
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    if log_file == '.':
        log_handler = logging.StreamHandler(sys.stdout)
    else:
        log_handler = logging.FileHandler(log_file)

    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    return logger
