import socket
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ExtensionOID

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

    def test_certificate_extensions(self):
        try:
            # Verify that all critical extensions are recognized and processed correctly.
            for ext in self.cert.extensions:
                if ext.critical:
                    assert ext.oid in ExtensionOID

            # Check non-critical extensions for proper format and encoding.
            # This is implicitly done by the cryptography library when loading the certificate.

            # Ensure that specific extensions comply with their respective requirements.
            key_usage = self.cert.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE)
            if key_usage:
                assert key_usage.value.digital_signature

            ext_key_usage = self.cert.extensions.get_extension_for_oid(ExtensionOID.EXTENDED_KEY_USAGE)
            if ext_key_usage:
                assert any(usage in ext_key_usage.value for usage in [x509.oid.ExtendedKeyUsageOID.SERVER_AUTH, x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH])

            basic_constraints = self.cert.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
            if basic_constraints:
                assert not basic_constraints.value.ca

            subject_alt_name = self.cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            if subject_alt_name:
                assert len(subject_alt_name.value) > 0

            print("Success: Certificate extensions test passed.")
            return True
        except AssertionError:
            print("Error: Certificate extensions test failed.")
            return False

#if __name__ == "__main__":
#    ip_or_hostname = input("Enter IP or hostname: ")
#    port = int(input("Enter port number: "))
tester = CertificateTester("www.example.com", 443)
tester.test_certificate_extensions()
