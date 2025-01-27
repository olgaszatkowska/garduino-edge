import logging

class TimeoutFilter(logging.Filter):
    def filter(self, record):
        if 'timeout' in record.getMessage().lower():
            return False
        return True

def setup_logging(name: str):
    logger = logging.getLogger(name)
    
    logger.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    
    timeout_filter = TimeoutFilter()
    console_handler.addFilter(timeout_filter)
    
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger
