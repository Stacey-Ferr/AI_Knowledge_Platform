import logging
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from core.config import settings

load_dotenv()

class LogFormatter(logging.Formatter):
    """
        A custom formatter that returns log data as a dictionary
    """
    def format(self, record):
        log_dict = {
            "timestamp" : datetime.fromtimestamp(record.created).isoformat(),
            "level" : record.levelname,
            "logger" : record.name,
            "message" : record.getMessage(),
            "filename" : record.filename,
            "line" : record.lineno,
            "function" : record.funcName
        }

        return json.dumps(log_dict)

logger = logging.getLogger("app_logger")

log_level = settings.LOG_LEVEL.upper()
print("Log level is: ", log_level)
logger.setLevel(getattr(logging, log_level, logging.INFO))

handler = logging.StreamHandler()
handler.setFormatter(LogFormatter())
logger.addHandler(handler)