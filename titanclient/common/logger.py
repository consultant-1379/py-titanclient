import logging
from pathlib import Path

from logging.handlers import RotatingFileHandler

from ..common.config import settings

logger = None


def init_logger():

    loglevel =  getattr(logging, settings.loglevel or "DEBUG")
    logger = logging.getLogger("titanclient")
    formatter = logging.Formatter("[%(asctime)s] - %(levelname)s:%(name)s:%(message)s")

    log_dir = Path(settings.logdir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "titanclient.log"

    logger.setLevel(loglevel)

    file_handler = RotatingFileHandler(
        f"{log_file.as_posix()}",
        maxBytes=5000000,
        backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(loglevel)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(loglevel)
    logger.addHandler(stream_handler)

    return logger


if logger is None:
    logger = init_logger()
