import logging
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

from core.settings import settings


def _get_log_level(level_str: str) -> int:
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return level_map.get(level_str.upper(), logging.INFO)


def setup_logger(
    name: str = "minimax_api_plan",
    level: Optional[int] = None,
    format_str: Optional[str] = None,
) -> logging.Logger:
    if level is None:
        level = _get_log_level(settings.log.level)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter(
        format_str
        or "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if settings.log.file_enabled:
        log_path = Path(settings.log.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            log_path,
            when="D",
            backupCount=settings.log.rotation_days,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
