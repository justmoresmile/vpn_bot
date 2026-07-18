import sys

from loguru import logger


logger.remove()


logger.add(
    sys.stdout,
    level="INFO",
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level}</level> | "
        "{name}:{function}:{line} | "
        "{message}"
    ),
)


logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    encoding="utf-8",
)