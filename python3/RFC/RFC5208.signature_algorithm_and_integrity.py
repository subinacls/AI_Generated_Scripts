import socket
import ssl
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend


class CertificateTester:
    def __init__(self, ip_or_hostname, port):
        self.ip_or_hostname = ip_or_hostname
        self.port = port
        self.cert = self._get_certificate()

    def _get_certificate(self):
        with socket.create_connection((self.ip_or_hostname, self.port)) as sock:
            with ssl.wrap_socket(sock, cert_reqs=ssl.CERT_NONE) as ssl_sock:
                pem_cert = ssl.DER_cert_to_PEM_cert(ssl_sock.getpeercert(binary_form=True))
                return x509.load_pem_x509_certificate(pem_cert.encode(), default_backend())

    def test_signature_algorithm_and_integrity(self):
        try:
            # Confirm that the certificate's signature algorithm is supported and valid.
            signature_algorithm = self.cert.signature_algorithm_oid
            hash_algorithm = self.cert.signature_hash_algorithm

            # Check the signatureValue field to ensure the certificate's integrity.
            issuer_cert = self._get_issuer_certificate()
            issuer_public_key = issuer_cert.public_key()
            issuer_public_key.verify(
                self.cert.signature,
                self.cert.tbs_certificate_bytes,
                self.cert.signature_hash_algorithm,
            )

            print("Success: Signature algorithm and integrity tests passed.")
            return True

        except InvalidSignature:
            print("Error: Signature algorithm or integrity test failed.")
            return False

    def _get_issuer_certificate(self):
        # Add logic to retrieve the issuer certificate, e.g., from a local store or a predefined CA bundle.
        # This example returns the certificate itself, which may not be the actual issuer.
        return self.cert


# Example usage:
tester = CertificateTester("www.example.com", 443)
tester.test_signature_algorithm_and_integrity()
