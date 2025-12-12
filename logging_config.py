"""
logging_config.py - Centralized logging configuration for Alarmify

Provides structured logging with both console and file output.
Logs are saved to timestamped files in the 'logs' directory.

Features:
- Separate loggers for different modules (gui, alarm, spotify_api)
- Timestamped log files with rotation
- Console output for development
- Structured log format with timestamps and log levels

Usage:
    from logging_config import get_logger
    logger = get_logger(__name__)
    logger.info('Application started')
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


# Global log directory
LOG_DIR = Path(__file__).parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Global flag to track if logging is configured
_logging_configured = False


def setup_logging(log_level=logging.INFO):
    """
    Configure logging for the entire application.
    
    Sets up:
    - Console handler for development/debugging
    - Rotating file handler for persistent logs
    - Structured formatter with timestamps
    
    Args:
        log_level: Minimum log level to capture (default: INFO)
    """
    global _logging_configured
    
    if _logging_configured:
        return
    
    # Create logs directory if it doesn't exist
    LOG_DIR.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    log_filename = LOG_DIR / f'alarmify_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    # Define log format with timestamp, level, module, and message
    log_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(log_format, date_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers
    root_logger.handlers.clear()
    
    # Console handler - outputs to stdout
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler - outputs to rotating log file
    # Keeps current log + 5 backups, max 5MB per file
    file_handler = logging.handlers.RotatingFileHandler(
        log_filename,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Log startup message
    root_logger.info('='*60)
    root_logger.info('Alarmify logging system initialized')
    root_logger.info(f'Log file: {log_filename}')
    root_logger.info('='*60)
    
    _logging_configured = True


def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Ensure logging is configured
    if not _logging_configured:
        setup_logging()
    
    return logging.getLogger(name)


def get_log_files():
    """
    Get list of all log files in the logs directory.
    
    Returns:
        list[Path]: List of log file paths, sorted by modification time (newest first)
    """
    if not LOG_DIR.exists():
        return []
    
    log_files = list(LOG_DIR.glob('alarmify_*.log*'))
    # Sort by modification time, newest first
    log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return log_files


def get_current_log_file():
    """
    Get the path to the current log file.
    
    Returns:
        Path: Path to current log file, or None if logging not initialized
    """
    log_files = get_log_files()
    return log_files[0] if log_files else None


def read_log_file(log_file_path, max_lines=1000):
    """
    Read contents of a log file.
    
    Args:
        log_file_path: Path to log file
        max_lines: Maximum number of lines to read (default: 1000)
        
    Returns:
        str: Contents of the log file
    """
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Return last N lines
            return ''.join(lines[-max_lines:])
    except Exception as e:
        return f'Error reading log file: {e}'
