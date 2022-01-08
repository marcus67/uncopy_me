import logging

DEFAULT_LOG_LEVEL = "INFO"
LOGGING_NAME = "uncopy_me"

logger = None


def start_loggging(p_loglevel:str = DEFAULT_LOG_LEVEL) -> logging.Logger:

    root_logger = logging.getLogger()
    root_logger.handlers = []

    handler = logging.StreamHandler()
    handler.setLevel(DEFAULT_LOG_LEVEL)
    root_logger.addHandler(handler)

    logger = logging.getLogger(LOGGING_NAME)
    logger.setLevel(DEFAULT_LOG_LEVEL)

    if p_loglevel is not None:
        logging_level = logging.getLevelName(p_loglevel)

        if p_loglevel != DEFAULT_LOG_LEVEL:

            fmt = "Changing logging level to {level}"
            logger.info(fmt.format(level=p_loglevel))

            handler.setLevel(logging_level)
            root_logger.setLevel(logging_level)
            logger.setLevel(logging_level)

    return logger
