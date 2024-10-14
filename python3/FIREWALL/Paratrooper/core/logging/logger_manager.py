# logger_manager.py

import logging

class LoggerManager:
    def __init__(self, name='MSFLogger', log_file='msfhandler.log', level=logging.DEBUG):
        """
        Initializes a logger with a specified name, log file, and log level.
        
        :param name: Name of the logger, defaults to 'MSFLogger'.
        :param log_file: Path to the log file where events will be recorded.
        :param level: The logging level (e.g., logging.DEBUG, logging.INFO).
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create console handler and set the level to debug
        ch = logging.StreamHandler()
        ch.setLevel(level)

        # Create file handler and set the level to debug
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)

        # Create a formatter and set it to both handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # Add handlers to the logger
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

    def log(self, message, level='info'):
        """
        Logs a message with a specific level.
        
        :param message: The message to log.
        :param level: The severity level ('debug', 'info', 'warning', 'error').
        """
        if level == 'debug':
            self.logger.debug(message)
        elif level == 'info':
            self.logger.info(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)
        else:
            self.logger.info(message)
