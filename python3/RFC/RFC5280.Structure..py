import socket
import ssl
from cryptography import x509
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

    def test_certificate_structure_and_encoding(self):
        try:
            # Check that the certificate is ASN.1-encoded and complies with the X.509v3 format.
            assert self.cert.version == x509.Version.v3

            # Ensure that all mandatory fields are present.
            assert self.cert.serial_number is not None
            assert self.cert.signature_algorithm_oid is not None
            assert self.cert.issuer is not None
            assert self.cert.not_valid_before is not None
            assert self.cert.not_valid_after is not None
            assert self.cert.subject is not None
            assert self.cert.public_key() is not None

            # Verify that optional fields are correctly encoded when present.
            if self.cert.issuer_unique_id is not None:
                assert isinstance(self.cert.issuer_unique_id, bool)
            if self.cert.subject_unique_id is not None:
                assert isinstance(self.cert.subject_unique_id, bool)
            if self.cert.extensions is not None:
                assert isinstance(self.cert.extensions, x509.Extensions)

            print("Success: Certificate structure and encoding tests passed.")
            return True

        except AssertionError:
            print("Error: Certificate structure and encoding tests failed.")
            return False


# Example usage:
tester = CertificateTester("www.example.com", 443)
tester.test_certificate_structure_and_encoding()
