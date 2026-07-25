from pathlib import Path
import sys

from loguru import logger

from app.config import settings


def setup_logging():

    logs_dir = Path("logs")
    logs_dir.mkdir(
        exist_ok=True,
    )

    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level:<8}</level> | "
        "<cyan>{name}</cyan>:"
        "<cyan>{function}</cyan>:"
        "<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        level="INFO",
        format=log_format,
        colorize=True,
    )

    logger.add(
        logs_dir / "app.log",
        level="INFO",
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        encoding="utf-8",
        format=log_format,
    )

    logger.add(
        logs_dir / "error.log",
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        format=log_format,
    )

    if settings.debug:

        logger.add(
            logs_dir / "debug.log",
            level="DEBUG",
            rotation="10 MB",
            retention="3 days",
            compression="zip",
            encoding="utf-8",
            format=log_format,
        )