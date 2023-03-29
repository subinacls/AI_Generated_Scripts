import ssl
import unittest
from typing import List
import logging
import socket
import time
import argparse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Test SSL/TLS on a remote server.")
parser.add_argument("remote_server", help="Remote server IP or hostname")
parser.add_argument("remote_port", type=int, help="Remote server port")
args = parser.parse_args()

REMOTE_SERVER = args.remote_server
REMOTE_PORT = args.remote_port

class SSLTLSTestCase(unittest.TestCase):

    def _get_openssl_cipher_list(self):
        context = ssl.create_default_context()
        context.set_ciphers('DEFAULT:aNULL:eNULL:LOW:EXPORT:SSLv2')
        cipher_list = context.get_ciphers()
        return [cipher["name"] for cipher in cipher_list]

    def test_remote_server_supported_ciphers(self):
        supported_protocols = [
            ssl.PROTOCOL_TLSv1_1,
            ssl.PROTOCOL_TLSv1_2,
        ]
        cipher_list = self._get_openssl_cipher_list()
        supported_ciphers = []
        for protocol in supported_protocols:
          counter = 0
          for cipher in cipher_list:
            context = ssl.SSLContext(protocol)
            try:
                context.set_ciphers(cipher+':'+cipher)
            except Exception as e:
               counter+=1
               continue
            try:
                with socket.create_connection((REMOTE_SERVER, REMOTE_PORT), timeout=30) as sock:
                    with context.wrap_socket(sock, server_hostname=REMOTE_SERVER) as ssock:
                        cipher_name = ssock.cipher()[0]
                        supported_ciphers.append(cipher_name)
                        logger.debug(f"Remote server supports protocol:cipher: {protocol}:{cipher_name}")
                counter+=1
            except socket.gaierror as sockgai:
                time.sleep(10)
                pass
            except (ssl.SSLError, ConnectionError, socket.timeout) as e:
                pass
            counter+=1
          counter+=1

        self.assertTrue(len(supported_ciphers) > 0, "Remote server does not support any tested ciphers")

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

# Tested against python 3.11 or >
# Example: python3 python_ssl_TLSScanner.py www.google.com 443
