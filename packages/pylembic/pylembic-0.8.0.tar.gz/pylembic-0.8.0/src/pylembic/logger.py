import logging

from pylembic.formatter import CustomFormatter


def configure_logger(verbose: bool = False) -> logging.Logger:
    """Configure the logger with a custom formatter and verbosity level.

    Args:
        verbose (bool): Whether to enable verbose logging.

    Returns:
        logging.Logger: The configured logger.
    """
    logger = logging.getLogger(__name__)

    # Avoid adding multiple handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    if not verbose:
        # Effectively disables logging
        logger.setLevel(logging.CRITICAL + 1)
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = CustomFormatter(datefmt="%d %b %Y | %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
