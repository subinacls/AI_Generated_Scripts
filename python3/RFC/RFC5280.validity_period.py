import socket
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from datetime import datetime

class CertificateTester:
    def __init__(self, ip_or_hostname, port):
        self.ip_or_hostname = ip_or_hostname
        self.port = port
        self.cert = self._get_certificate()

    def _get_certificate(self):
        with socket.create_connection((self.ip_or_hostname, self.port)) as sock:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with context.wrap_socket(sock, server_hostname=self.ip_or_hostname) as ssl_sock:
                der_cert = ssl_sock.getpeercert(binary_form=True)
                pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)
                cert = x509.load_pem_x509_certificate(pem_cert.encode(), default_backend())

        return cert

    def test_validity_period(self):
        try:
            # Check the certificate's notBefore and notAfter fields to ensure that it is currently valid.
            current_time = datetime.utcnow()
            assert self.cert.not_valid_before <= current_time <= self.cert.not_valid_after

            print("Success: Validity period test passed.")
            return True
        except AssertionError:
            print("Error: Validity period test failed.")
            return False
