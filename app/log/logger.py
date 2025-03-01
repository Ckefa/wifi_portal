import logging


def getLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formater = logging.Formatter(
        "%(asctime)s $ %(name)s $ %(levelname)s $ %(message)s\n")

    # Define logging handlers
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formater)

    file_handler = logging.FileHandler(filename="log/logs/wifi_portal.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formater)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger

