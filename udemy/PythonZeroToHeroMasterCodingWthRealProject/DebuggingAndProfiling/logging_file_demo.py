import logging

logging.basicConfig(filename="example.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

logging.debug("this is a debug message!")
logging.info("this is an info message!")
logging.warning("this is a warning message!")
logging.error("this is an error message!")
logging.critical("this is a critical message!")