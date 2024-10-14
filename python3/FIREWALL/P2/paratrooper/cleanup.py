import os
import logging

# Setup logger
logger = logging.getLogger(__name__)

def cleanup():
    """
    Performs cleanup tasks, including removing named pipes and saving databases.
    """
    logger.info("Performing cleanup tasks...")
    try:
        os.remove('/tmp/ParatrooperINPUT')
        os.remove('/tmp/ParatrooperOUTPUT')
    except OSError as e:
        logger.error(f"Error during cleanup: {e}")
    logger.info("Cleanup completed.")
