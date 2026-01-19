#!/usr/bin/env python3
"""
DailyNewsBot - Unified Logging Configuration
=============================================
Configures logging with file rotation and console output.
"""

import logging
import logging.handlers
from pathlib import Path
import sys


def setup_logging(name: str = "DailyNewsBot", log_dir: str = "logs") -> logging.Logger:
    """
    Configure logging with file rotation and console output.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
    
    Returns:
        Configured logger instance
    """
    Path(log_dir).mkdir(exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler with rotation (10MB max, 5 backups)
    log_file = Path(log_dir) / "bot.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get a child logger with the specified name."""
    base_logger = logging.getLogger("DailyNewsBot")
    if name:
        return base_logger.getChild(name)
    return base_logger


if __name__ == "__main__":
    # Test logging
    logger = setup_logging()
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    print(f"\nLogs written to: logs/bot.log")
