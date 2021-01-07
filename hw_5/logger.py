import logging

logging.basicConfig(
    filename="requests.log",
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def logger(event, severity):
    if severity == "error":
        logging.error(event)

    elif severity == "info":
        logging.info(event)

    elif severity == "warning":
        logging.warning(event)
