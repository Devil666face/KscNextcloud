from loguru import logger

logger.add(
    "user.log",
    backtrace=True,
    diagnose=True,
    enqueue=True,
    encoding="utf-8",
)
