import logging
from pathlib import Path

from zero_sum.config import config

# MARK: Init
logger = logging.getLogger("zero_sum")
logger.setLevel(config.LOG_LEVEL)

# Create a formatter with timestamps and module name
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# create log handler if config is set to use file logging
file_handler = None
if config.USE_FILE_LOGGING:
    file_handler = logging.FileHandler(config.LOG_PATH)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


# MARK: callbacks
def update_log_level(old, new):
    logger.setLevel(new)
    logger.info(f"Log level updated to {new}")


config.on_change(config.LOG_LEVEL, update_log_level)


def update_use_file_logging(old, new):
    global file_handler
    if new == old:
        return
    info_strs = [f"File logging set to {new}"]
    if new:
        if not config.LOG_PATH.parent.exists():
            config.LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            info_strs.append(f"Created log directory at {config.LOG_PATH.parent}")
        if not config.LOG_PATH.exists():
            config.LOG_PATH.touch()
            info_strs.append(f"Created new log file at {config.LOG_PATH}")
        file_handler = logging.FileHandler(config.LOG_PATH)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        if file_handler:
            logger.removeHandler(file_handler)
            file_handler.close()
            info_strs.append(
                f"Removed file logging handler at {file_handler.baseFilename}"
            )
            file_handler = None
    for info_str in info_strs:
        logger.info(info_str)


config.on_change(config.USE_FILE_LOGGING, update_use_file_logging)


def update_log_path(old, new):
    if new == old:
        return
    global file_handler
    info_strs = []
    if file_handler:
        logger.removeHandler(file_handler)
        info_strs.append(f"Removed file logging handler at {file_handler.baseFilename}")
    if new:
        # create dir if it doesn't exist
        if not new.parent.exists():
            new.parent.mkdir(parents=True, exist_ok=True)
            info_strs.append(f"Created new directory at {new.parent}")
        file_handler = logging.FileHandler(config.LOG_PATH)
        file_handler.setFormatter(formatter)
        if config.USE_FILE_LOGGING:
            logger.addHandler(file_handler)
        info_strs.append(f"File logging updated to {new}")
    for info_str in info_strs:
        logger.info(info_str)


config.on_change(config.LOG_PATH, update_log_path)


logger.info(
    f"Logging initialized. File logging: {config.USE_FILE_LOGGING}, Log path: {config.LOG_PATH}"
)
