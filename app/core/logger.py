"""
日志配置 - 使用 loguru
"""
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


# 移除默认 handler
logger.remove()

# 控制台输出
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>",
    level=settings.LOG_LEVEL,
    colorize=True,
)

# 文件输出 - 普通日志（按天滚动）
log_dir = Path(settings.LOG_DIR)
log_dir.mkdir(exist_ok=True)

logger.add(
    log_dir / "app_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.LOG_LEVEL,
    rotation="00:00",
    retention="30 days",
    encoding="utf-8",
)

# 文件输出 - 错误日志
logger.add(
    log_dir / "error_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="00:00",
    retention="90 days",
    encoding="utf-8",
)

__all__ = ["logger"]
