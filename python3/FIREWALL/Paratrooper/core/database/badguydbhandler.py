'''
import os
import datetime
import numpy as np  # Assuming numpy is used for saving/loading data
from logger_manager import LoggerManager
from hashlib import sha256

# Initialize logger
logger = LoggerManager()
'''

class BadDBHandler:
    """
    Handles the badguy database.
    Manages logging and saving unknown clients' data to a JSON-like structure using numpy or similar.
    """

    def __init__(self):
        logger.log('Initializing BadDBHandler...', 'info')
        self.baddb = {'IP': {}, 'DATA': {}}  # Initialize bad guy database structure in memory

    @staticmethod
    def log_rotate():
        """
        Function to generate a log rotation timestamp format for the log files.
        """
        return datetime.datetime.now().strftime('%Y%m%d')

    def datalog_init(self):
        """
        Initialize the bad guy data log structure in memory.
        """
        logger.log('Initializing bad guy data log...', 'info')
        self.baddb = {'IP': {}, 'DATA': {}}

    def save_datalog(self):
        """
        Save the current bad guy database to disk as a numpy file.
        """
        logger.log('Saving bad guy data log...', 'info')
        try:
            logfilename = f'paratrooper-datalog.{self.log_rotate()}.npy'
            np.save(logfilename, self.baddb)  # Save the data using numpy
            logger.log(f'Saved bad guy data log to {logfilename}', 'info')
        except Exception as e:
            logger.log(f"Failed to save bad guy data log: {e}", 'error')

    def open_datalog(self):
        """
        Load the bad guy database from disk if it exists; otherwise, initialize and save it.
        """
        logfilename = f'paratrooper-datalog.{self.log_rotate()}.npy'
        logger.log(f'Attempting to open bad guy data log {logfilename}...', 'info')
        try:
            if os.path.exists(logfilename):
                self.baddb = np.load(logfilename, allow_pickle=True).item()  # Load the dictionary from the file
                logger.log(f'Successfully loaded bad guy data log from {logfilename}', 'info')
            else:
                logger.log(f'Data log {logfilename} not found, initializing new log...', 'warning')
                self.datalog_init()
                self.save_datalog()
        except Exception as e:
            logger.log(f"Failed to load bad guy data log: {e}", 'error')
            self.datalog_init()
            self.save_datalog()

    def import_datalog(self, bidataset):
        """
        Import new data into the bad guy database.
        :param bidataset: Tuple containing IP address and data.
        """
        logger.log('Importing data into bad guy database...', 'info')
        try:
            biip = str(bidataset[0])  # IP address
            bidata = str(bidataset[1])  # Data
            datahash = self.shahash(bidata)  # Hash of the data
            dateset = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Timestamp

            # Process the 'DATA' section
            if datahash not in self.baddb['DATA']:
                self.baddb['DATA'][datahash] = {}
            if biip not in self.baddb['DATA'][datahash]:
                self.baddb['DATA'][datahash][biip] = [bidata, dateset, dateset, 1]  # New entry
            else:
                self.baddb['DATA'][datahash][biip][2] = dateset  # Update 'last seen' time
                self.baddb['DATA'][datahash][biip][3] += 1  # Increment seen counter

            # Process the 'IP' section
            if biip not in self.baddb['IP']:
                self.baddb['IP'][biip] = {}
            if datahash not in self.baddb['IP'][biip]:
                self.baddb['IP'][biip][datahash] = 1  # First entry for this IP and datahash
            else:
                self.baddb['IP'][biip][datahash] += 1  # Increment counter

            logger.log(f'Successfully imported data for IP: {biip} and hash: {datahash}', 'info')
        except Exception as e:
            logger.log(f"Failed to import data into bad guy database: {e}", 'error')

    @staticmethod
    def shahash(plainvalue):
        """
        Generate SHA-256 hash of a given value.
        """
        return sha256(str(plainvalue).strip().encode('utf-8')).hexdigest()

