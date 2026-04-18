import logging
import sys
from pathlib import Path
from typing import Optional

from core.settings import settings


def get_log_level(level_str: str) -> int:
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
        level = get_log_level(settings.app.log_level)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter(
        format_str
        or "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if settings.app.log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if settings.app.log_to_file:
        try:
            log_dir = Path(settings.app.log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / f"{name}.log"

            file_handler = logging.FileHandler(
                log_file,
                encoding="utf-8",
                mode="a",
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            error_log_file = log_dir / f"{name}_error.log"
            error_file_handler = logging.FileHandler(
                error_log_file,
                encoding="utf-8",
                mode="a",
            )
            error_file_handler.setLevel(logging.ERROR)
            error_file_handler.setFormatter(formatter)
            logger.addHandler(error_file_handler)

        except Exception as e:
            print(f"无法创建日志文件处理器: {e}")

    logger.propagate = False

    if settings.app.debug:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)

    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
