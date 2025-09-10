import logging
from logging.handlers import TimedRotatingFileHandler
import os
from config.loader import cfg
from datetime import datetime
import pytz

# Define color codes
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"  # Green
COLOR_YELLOW = "\033[93m"  # Yellow
COLOR_ORANGE = "\033[38;5;208m"  # Orange
COLOR_RED = "\033[91m"  # Red


class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style="%", color=True):
        super().__init__(fmt, datefmt, style)
        self.color = color

    def format(self, record):
        color = COLOR_RESET
        if record.levelno == logging.INFO:
            color = COLOR_GREEN
        elif record.levelno == logging.DEBUG:
            color = COLOR_YELLOW
        elif record.levelno == logging.WARNING:
            color = COLOR_ORANGE
        elif record.levelno == logging.ERROR:
            color = COLOR_RED

        message = super().format(record)
        if self.color:
            message = f"{color}{message}{COLOR_RESET}"
        return message


log_dir = cfg["log"]["logdir"]
log_file_name = cfg["log"]["logfile"]
verbose = cfg["log"]["verbose"]

basedir = os.path.abspath(os.path.dirname(__file__))
log_folder = os.path.join(basedir, log_dir)
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

logname = os.path.join(log_folder, log_file_name)
handler = TimedRotatingFileHandler(logname, when="midnight")
handler.setLevel(logging.DEBUG if verbose else logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if verbose else logging.INFO)

# Set timezone
hcm_timezone = pytz.timezone("Asia/Ho_Chi_Minh")

# Create custom formatter instance for file logging without color
formatter_file = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)

# Apply formatter to handler for file logging
handler.setFormatter(formatter_file)
logger.addHandler(handler)

# Create another custom formatter instance for console logging with color
formatter_console = ColoredFormatter(
    "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s", color=True
)

# Create StreamHandler for console logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

# Apply formatter to console handler
console_handler.setFormatter(formatter_console)
logger.addHandler(console_handler)
