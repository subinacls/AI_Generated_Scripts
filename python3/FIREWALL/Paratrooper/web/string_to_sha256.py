import hashlib
import sys
from logger_manager import LoggerManager

# Ensure compatibility between Python 2 and 3
if sys.version_info[0] < 3:
    str_type = unicode  # In Python 2, use 'unicode' for string handling
else:
    str_type = str  # In Python 3, use 'str'

# Initialize the logger
logger = LoggerManager()

def shahash(plainvalue):
    """
    Converts a given string into its SHA-256 hash.

    :param plainvalue: The input string to be hashed.
    :return: The SHA-256 hash of the input string.
    """
    try:
        logger.log('Entering: shahash()', 'info')

        # Convert input to string (or unicode in Python 2) and compute SHA-256 hash
        hash_value = hashlib.sha256(str_type(plainvalue).strip().encode('utf-8')).hexdigest()

        logger.log('Exiting: shahash()', 'info')
        return hash_value

    except Exception as e:
        logger.log('Failed sha hashing: {}'.format(e), 'error')
        return None  # Return None to indicate an error occurred
