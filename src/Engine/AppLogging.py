import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_log_dir() -> Path:
    app_data = os.getenv("APPDATA")
    if not app_data:
        raise ValueError("APPDATA environment variable not found")

    log_dir = Path(app_data) / "ElchWorks" / "ElchiTools" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(level: int = logging.INFO) -> None:
    log_file = get_log_dir() / "elchitools.log"

    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(name)s: %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")

    file_handler = RotatingFileHandler(log_file, maxBytes=2_000_000, backupCount=5, encoding="utf-8", )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.getLogger("matplotlib").setLevel(logging.WARNING)
