import logging
import os
from logging.handlers import TimedRotatingFileHandler


def setup_logger(dir_path):
    """Configure and return a logger instance using singleton pattern"""
    logs_dir = os.path.join(dir_path, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Configure logging
    logger = logging.getLogger('bot')
    logger.setLevel(logging.INFO)
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # File handler with monthly rotation
    file_handler = TimedRotatingFileHandler(
        os.path.join(logs_dir, 'bot.log'),
        when='midnight',
        interval=30,  # Monthly rotation
        backupCount=2  # Keep last 2 months
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger


def get_logger():
    return logging.getLogger('bot')
