import numpy as np
import os
import logging

# Setup logger
logger = logging.getLogger(__name__)

class BadDBHandler:
    """
    Handles the badguy database.
    """

    def __init__(self):
        self.baddb = {}

    def open_datalog(self):
        """
        Opens the badguy datalog from disk.
        """
        try:
            if os.path.exists('badguy.db.npy'):
                self.baddb = np.load('badguy.db.npy', allow_pickle=True).item()
                logger.info("Badguy datalog loaded.")
            else:
                logger.warning("No datalog found. Creating a new one.")
                self.datalog_init()
        except Exception as e:
            logger.error(f"Failed to load datalog: {e}")
            raise e

    def save_datalog(self):
        """
        Saves the badguy datalog to disk.
        """
        try:
            np.save('badguy.db.npy', self.baddb)
            logger.info("Datalog saved to disk.")
        except Exception as e:
            logger.error(f"Failed to save datalog: {e}")
            raise e

    def datalog_init(self):
        """
        Initializes the datalog structure.
        """
        self.baddb = {'IP': {}, 'DATA': {}}
        logger.info("Initialized empty datalog.")

    def import_datalog(self, dataset):
        """
        Imports data to the badguy database.
        """
        ip, data = dataset
        logger.debug(f"Importing datalog for IP {ip}")
        if ip not in self.baddb['IP']:
            self.baddb['IP'][ip] = []
        self.baddb['IP'][ip].append(data)
        self.save_datalog()
