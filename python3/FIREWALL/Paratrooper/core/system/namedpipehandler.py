'''
import os
import uuid
import logging
from os import mkfifo, remove

# Initialize logger
logger = logging.getLogger(__name__)
'''

##### NAMED PIPE FUNCTIONALITY #####
'''
This section manages the creation of named pipes for administrative tasks such as loading and saving
client databases or running system commands. These named pipes act as interfaces for inter-process communication.
'''

# Static named pipe for this server
'''
INWARD FACING NAMED PIPE FILENAME
'''
bi.fifoinfile = '/tmp/' + str(uuid.uuid5(uuid.NAMESPACE_DNS, 'ParatrooperINPUT'))

'''
OUTWARD FACING NAMED PIPE FILENAME
'''
bi.fifooutfile = '/tmp/' + str(uuid.uuid5(uuid.NAMESPACE_DNS, 'ParatrooperOUTPUT'))


##### FIFO GENERATOR #####
def makefifo(filename):
    """
    Creates a named pipe (FIFO) if it doesn't already exist.
    
    Args:
    - filename (str): The full path of the named pipe to be created.
    
    Raises:
    - OSError: If creating or removing the FIFO fails.
    """
    logger.info(f"Entering makefifo() for {filename}")

    # Check if the FIFO already exists
    if os.path.exists(filename):
        logger.warning(f"FIFO pipe '{filename}' already exists. Exiting.")
        return

    # Attempt to create the FIFO
    try:
        logger.info(f"Creating named pipe: {filename}")
        mkfifo(filename)
        logger.info(f"Successfully created FIFO: {filename}")
    except Exception as e:
        logger.error(f"Failed to create FIFO: {e}. Attempting to recover by removing and recreating.")
        
        # Attempt to remove the existing file and retry creating the FIFO
        try:
            if os.path.exists(filename):
                remove(filename)
                logger.info(f"Successfully removed existing FIFO: {filename}. Retrying creation.")
            mkfifo(filename)
            logger.info(f"Successfully recreated FIFO: {filename}")
        except Exception as e2:
            logger.error(f"Failed to recreate FIFO after recovery attempt: {e2}")
    
    logger.info("Exiting makefifo()")
