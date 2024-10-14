'''
import datetime
import sys
from logger_manager import LoggerManager

# Ensure compatibility between Python 2 and 3 for builtins
if sys.version_info[0] < 3:
    import __builtin__ as bi  # Python 2
else:
    import builtins as bi     # Python 3

# Initialize logger
logger = LoggerManager()
'''

def datenow():
    """
    Function to get the current date in 'YYYY-MM-DD' format.
    :return: Current date as a string.
    """
    try:
        logger.log('Entering: datenow()', 'info')
        
        current_date = str(datetime.datetime.now()).split()[0].strip()
        
        logger.log(f"Current date: {current_date}", 'debug')
        logger.log('Exiting: datenow()', 'info')
        
        return current_date

    except Exception as e:
        logger.log(f"Failed to get current date: {e}", 'error')
        return None  # Return None to indicate an error occurred


def datetimestamp():
    """
    Function to get the current date and time in 'YYYY-MM-DD HH:MM:SS' format.
    :return: Current date and timestamp as a string.
    """
    try:
        logger.log('Entering: datetimestamp()', 'info')
        
        current_timestamp = str(datetime.datetime.now())
        
        logger.log(f"Current timestamp: {current_timestamp}", 'debug')
        logger.log('Exiting: datetimestamp()', 'info')
        
        return current_timestamp

    except Exception as e:
        logger.log(f"Failed to get current timestamp: {e}", 'error')
        return None  # Return None to indicate an error occurred
