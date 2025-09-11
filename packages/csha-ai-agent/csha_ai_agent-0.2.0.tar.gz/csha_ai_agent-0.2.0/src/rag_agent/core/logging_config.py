import logging
from logging.handlers import RotatingFileHandler

file_handler = RotatingFileHandler(
    "ai_agent_output.log",
    maxBytes=10_000_000,
    backupCount=5,
    encoding="utf-8",
)

stream_handler = logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[file_handler, stream_handler]
)

