"""Logging configuration for synthbiodata."""

import logging
import sys
from typing import Optional

def setup_logger(name: str = "synthbiodata", level: Optional[int] = None) -> logging.Logger:
    """Set up a logger with a consistent format.
    
    Args:
        name: The name of the logger
        level: The logging level. If None, uses INFO for production, DEBUG for development
        
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only add handler if logger doesn't already have one
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Set level if provided, otherwise use default
    if level is not None:
        logger.setLevel(level)
    elif logger.level == logging.NOTSET:  # Only set if not already set
        logger.setLevel(logging.INFO)
    
    return logger

# Create default logger
logger = setup_logger()
