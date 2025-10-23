"""
Logging configuration for the application.

Provides a configured logger for use throughout the app.
"""
import logging
import sys
from pathlib import Path


def setup_logger(name: str = "llm-export-tools", level: int = logging.INFO) -> logging.Logger:
    """
    Set up and configure the application logger.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Format: [2024-10-23 14:30:22] INFO: Message here
    formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


# Create default logger instance
logger = setup_logger()

