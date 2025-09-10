import logging

class CustomFilter(logging.Filter):
    def filter(self, record):
        return 'important' in record.getMessage()

logger = logging.getLogger('filtered_logger')
logger.setLevel(logging.DEBUG)

logger.addFilter(CustomFilter())

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)

logger.debug("this is a debug message")
logger.info("this is an info message")