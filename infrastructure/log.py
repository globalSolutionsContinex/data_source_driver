import logging
from infrastructure import files
from logging.handlers import RotatingFileHandler


def get_logger_file_handler(log_formatter, logging_level):
    directory = "logs"
    files.create_directory_if_not_exists(directory)
    file_name = "data_source_flow.log"
    log_file_name = directory + "/" + file_name
    handler = RotatingFileHandler(log_file_name, maxBytes=100000000, backupCount=7)
    handler.setFormatter(log_formatter)
    handler.setLevel(logging.INFO)
    return handler


def get_logger_stdout_handler(log_formatter, logging_level):
    handler = logging.StreamHandler()
    handler.setFormatter(log_formatter)
    handler.setLevel(logging.INFO)
    return handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    if not len(logger.handlers):
        log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging_level = logging.INFO
        logger.setLevel(logging_level)
        logger.propagate = False
        file_handler = get_logger_file_handler(log_formatter, logging_level)
        logger.addHandler(file_handler)
        stdout_handler = get_logger_stdout_handler(log_formatter, logging_level)
        logger.addHandler(stdout_handler)
    return logger
