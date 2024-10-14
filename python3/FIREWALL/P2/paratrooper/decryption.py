import subprocess
import json
import yaml
import logging

# Setup logger
logger = logging.getLogger(__name__)

class INITDecrypt:
    """
    Handles the decryption of the client data stream.
    """

    @staticmethod
    def decryptwkey(datastream, key):
        """
        Decrypts a datastream using a provided key.
        """
        logger.debug(f"Decrypting data with key {key}")
        try:
            result = subprocess.check_output(
                f'echo {datastream} | openssl enc -aes-256-cbc -d -md sha256 -pass pass:{key}',
                shell=True
            )
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return yaml.safe_load(result)
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
