'''
import os
import json
import yaml
import subprocess
import logging

# Assuming logger is set up
logger = logging.getLogger(__name__)
'''

class INITDecrypt:
    """
    This class handles the decryption of user-supplied datastreams using keys
    from trusted clients in the client database.
    """
    
    def __init__(self):
        pass

    @staticmethod
    def decryptwkey(datastream):
        """
        Attempts to decrypt the given datastream using known client keys from the trusted database.
        The decrypted data is attempted to be parsed as either YAML or JSON.
        If decryption or data validation fails, the client is logged as untrusted.
        """
        if bi.diag:
            logger.debug('Entered: initdecrypt().decryptwkey()')
            logger.debug('Rawdatastream: %s', shahash(datastream))
            logger.debug('Rawdatastream type: %s', type(datastream))

        try:
            for host in bi.clientdb['trusted'].keys():
                if bi.diag:
                    logger.debug('Datastream length: %d', len(datastream))
                    logger.debug('Decryption key attempted: %s', shahash(host))
                
                if len(datastream) <= 4000:
                    BadDBHandler().import_datalog((ip, datastream))
                    DBHandler().import_everyone_client(ip)
                    return 0

                try:
                    # Decrypt using OpenSSL and base64
                    cmd = f'echo {datastream} | base64 -d | openssl enc -aes-256-cbc -d -md sha256 -pass pass:{host} 2>/dev/null | base64 -d 2>/dev/null'
                    rdata = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.readlines()[0].strip()
                except Exception as decrypt_error:
                    if bi.diag:
                        logger.error('Openssl Command Execution failure: %s', decrypt_error)
                    BadDBHandler().import_datalog((ip, datastream))
                    DBHandler().import_everyone_client(ip)
                    return 0

                if bi.diag:
                    logger.debug('Unencrypted data length: %d', len(rdata))
                    logger.debug('Unencrypted data hash: %s', shahash(rdata))

                if len(rdata) >= 4000:
                    try:
                        # Attempt to load as YAML first
                        yaml_data = yaml.safe_load(rdata)
                        if bi.diag:
                            logger.debug('User supplied data constructed as YAML')
                        return host, yaml_data
                    except Exception:
                        # Fallback to JSON if YAML fails
                        try:
                            json_data = json.loads(rdata)
                            if bi.diag:
                                logger.debug('User supplied data constructed as JSON')
                            return host, json_data
                        except Exception as data_load_error:
                            if bi.diag:
                                logger.error('Failed to load client data: %s', data_load_error)
                            BadDBHandler().import_datalog((ip, datastream))
                            DBHandler().import_everyone_client(ip)
                            return 0
                else:
                    if bi.diag:
                        logger.debug('Data length was less than 1000')
                    BadDBHandler().import_datalog((ip, datastream))
                    DBHandler().import_everyone_client(ip)
                    return 0
        except Exception as decrypt_fail:
            if bi.diag:
                logger.error('General decryption failure: %s', decrypt_fail)
            BadDBHandler().import_datalog((ip, datastream))
            DBHandler().import_everyone_client(ip)
            return 0

        if bi.diag:
            logger.debug('Exiting: initdecrypt().decryptwkey()')

        return 0

    if bi.diag:
        logger.debug('Exiting: initdecrypt()')
