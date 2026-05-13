import logging
import sys

# Centralized logging configuration
def setup_logging():
    # Base logger for the entire application
    logger = logging.getLogger("app")
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console Handler
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Avoid double logging if parent loggers have handlers
        logger.propagate = False
        
    return logger

# Initialize the 'app' logger
logger = setup_logging()

# Function to get a logger that inherits from 'app'
def get_logger(name: str):
    if not name.startswith("app.") and name != "app":
        name = f"app.{name}"
    return logging.getLogger(name)
