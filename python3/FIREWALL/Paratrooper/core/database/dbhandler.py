'''
import os
import numpy as np
import datetime
from hashlib import sha256
from logger_manager import LoggerManager

# Initialize logger
logger = LoggerManager()
'''

class DBHandler:
    """
    This class handles the modification of the clientdb object.
    Supported operations include opening, saving, importing, and validating clients.
    """

    def __init__(self):
        logger.log('DBHandler initialized', 'info')
        self.clientdb = None

    @staticmethod
    def log_rotate():
        """
        Function to generate a log rotation timestamp format for file naming.
        """
        return datetime.datetime.now().strftime('%Y%m%d')

    def save_clientdb(self):
        """
        Saves the clientdb to disk as a numpy file.
        """
        logger.log('Saving client database...', 'info')
        try:
            logfilename = f'paratrooper-clientdb.{self.log_rotate()}.npy'
            np.save(logfilename, self.clientdb)  # Save client database to disk
            logger.log(f'Successfully saved client database to {logfilename}', 'info')
        except Exception as e:
            logger.log(f"Failed to save client database: {e}", 'error')

    def open_clientdb(self):
        """
        Opens the clientdb from disk, or initializes it if not found.
        """
        logfilename = f'paratrooper-clientdb.{self.log_rotate()}.npy'
        logger.log(f'Attempting to open client database {logfilename}...', 'info')
        try:
            if os.path.exists(logfilename):
                self.clientdb = np.load(logfilename, allow_pickle=True).item()  # Load the client database
                logger.log(f'Client database loaded with {len(self.clientdb)} entries', 'info')
            else:
                logger.log(f'Client database {logfilename} not found, initializing new database...', 'warning')
                self.init_clientdb()
                self.save_clientdb()
        except Exception as e:
            logger.log(f"Failed to open client database: {e}", 'error')
            self.init_clientdb()
            self.save_clientdb()

    def init_clientdb(self):
        """
        Initializes an empty client database with default structure.
        """
        logger.log('Initializing new client database...', 'info')
        try:
            self.clientdb = {
                'invalid': [],
                'approved': {},
                'trusted': {},
                'rejected': [],
                'everyone': {},
                'msfshell': {}
            }
            logger.log('Client database initialized', 'info')
        except Exception as e:
            logger.log(f"Failed to initialize client database: {e}", 'error')

    def import_trusted_client(self, client_ip, client_data, raw_data):
        """
        Imports a trusted client's IP and data into the client database.
        """
        logger.log(f'Importing trusted client {client_ip}...', 'info')
        try:
            self.clientdb['approved'][client_ip] = self.shahash(client_data)  # Hash and store client data
            self.clientdb['invalid'].append(self.shahash(raw_data))  # Hash and store raw data
            IPsetBuilder.add_trusted_ips(client_ip)  # Add trusted IP to the IPSet
            logger.log(f'Trusted client {client_ip} successfully imported', 'info')
        except Exception as e:
            logger.log(f"Failed to import trusted client {client_ip}: {e}", 'error')

    def import_rejected_client(self, client_ip):
        """
        Imports a rejected client's IP into the client database.
        """
        logger.log(f'Importing rejected client {client_ip}...', 'info')
        try:
            if client_ip in self.clientdb['rejected']:
                logger.log(f"Client {client_ip} is already rejected", 'warning')
            else:
                self.clientdb['rejected'].append(client_ip)
                IPsetBuilder.add_rejected_ips(client_ip)
                logger.log(f"Rejected client {client_ip} successfully added", 'info')
        except Exception as e:
            logger.log(f"Failed to import rejected client {client_ip}: {e}", 'error')

    def import_everyone_client(self, client_ip):
        """
        Imports a client's IP into the 'everyone' group.
        """
        logger.log(f'Importing client {client_ip} to everyone group...', 'info')
        try:
            if client_ip in self.clientdb['rejected']:
                logger.log(f"Client {client_ip} is in the rejected list, cannot be added to everyone", 'error')
                return
            if client_ip in self.clientdb['everyone']:
                self.clientdb['everyone'][client_ip] += 1
                logger.log(f"Incremented access counter for {client_ip} in everyone group", 'info')
            else:
                self.clientdb['everyone'][client_ip] = 1
                logger.log(f"Added {client_ip} to everyone group", 'info')

            # Reject if access count exceeds a certain limit (example: 3)
            if self.clientdb['everyone'][client_ip] >= 3:
                logger.log(f"Client {client_ip} exceeded access attempts, moving to rejected list", 'warning')
                self.import_rejected_client(client_ip)
                del self.clientdb['everyone'][client_ip]  # Remove from everyone list
                IPsetBuilder.add_rejected_ips(client_ip)

        except Exception as e:
            logger.log(f"Failed to import client {client_ip} to everyone group: {e}", 'error')

    def validate_client(self, raw_data, client_data, client_ip):
        """
        Validates a client's authentication data.
        """
        logger.log(f'Validating client {client_ip}...', 'info')
        try:
            suuid = self.clientdb['trusted'].keys()
            cuuid = list(client_data.keys())[0]  # Assume client_data is a dict, get first key (System UUID)
            logger.log(f"Client UUID: {cuuid}", 'info')

            # Hash the raw data
            raw_hash = self.shahash(raw_data)
            if raw_hash in self.clientdb['invalid']:
                logger.log(f"Client {client_ip} sent invalid data (duplicate or invalid hash detected)", 'warning')
                self.import_rejected_client(client_ip)
                return 0

            if cuuid in suuid:  # System UUID is in trusted list
                cvalues = client_data[cuuid]
                if cvalues == self.clientdb['trusted'][cuuid]:
                    logger.log(f"Client {client_ip} validated successfully", 'info')
                    del self.clientdb['everyone'][client_ip]  # Remove from 'everyone' list
                    return 1
                else:
                    logger.log(f"Client {client_ip} failed validation due to mismatched data", 'warning')
            else:
                logger.log(f"Client {client_ip} has unknown UUID", 'warning')

            self.import_everyone_client(client_ip)
        except Exception as e:
            logger.log(f"Client validation failed: {e}", 'error')
            self.import_everyone_client(client_ip)

        return 0

    @staticmethod
    def shahash(plainvalue):
        """
        Generates SHA-256 hash of a given value.
        """
        return sha256(str(plainvalue).strip().encode('utf-8')).hexdigest()
