import logging
from paratrooper.decryption import INITDecrypt
from paratrooper.clientdb import DBHandler
from paratrooper.badguydb import BadDBHandler

# Setup logger
logger = logging.getLogger(__name__)

class DataRouter:
    """
    Routes data based on certain conditions.
    """

    @staticmethod
    def offload(dataset):
        ip, data = dataset
        logger.info(f"Offloading data from {ip}")
        
        decrypted_data = INITDecrypt.decryptwkey(data, 'some-key')
        if decrypted_data:
            # Perform validation
            valid = DBHandler().validate_client(data, decrypted_data, ip)
            if valid:
                logger.info(f"Client {ip} is authenticated.")
                DBHandler().import_trusted_client(ip, decrypted_data, data)
            else:
                logger.warning(f"Client {ip} failed validation.")
                BadDBHandler().import_datalog(dataset)
                DBHandler().import_everyone_client(ip)
        else:
            logger.error(f"Failed to decrypt data from {ip}.")
            BadDBHandler().import_datalog(dataset)
            DBHandler().import_everyone_client(ip)
