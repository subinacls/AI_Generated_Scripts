import socket
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ExtensionOID, NameOID
import certifi

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

    def _get_issuer_certificate(self, issuer_name):
        store = certifi.where()
        with open(store, "rb") as store_file:
            cert_data = store_file.read()

        for cert in x509.split_pem_certificates(cert_data):
            cert = x509.load_pem_x509_certificate(cert, default_backend())
            if cert.subject == issuer_name:
                return cert

        raise ValueError("Issuer certificate not found")

    def test_certificate_path_validation(self):
        try:
            cert_chain = [self.cert]
            while cert_chain[-1].issuer != cert_chain[-1].subject:
                issuer_cert = self._get_issuer_certificate(cert_chain[-1].issuer)
                cert_chain.append(issuer_cert)

            for idx, cert in enumerate(cert_chain[:-1]):
                issuer_cert = cert_chain[idx + 1]

                # Verify the certificate chain up to a trusted root CA, including proper chaining of the issuer and subject fields.
                assert cert.issuer == issuer_cert.subject

                # Check that the certificate path complies with the basic constraints extension (i.e., path length constraints and the CA field).
                basic_constraints = issuer_cert.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
                assert basic_constraints.value.ca
                if basic_constraints.value.path_length is not None:
                    assert idx <= basic_constraints.value.path_length

                # Validate that the key usage extension permits the intended use of the certificate (e.g., digital signatures, key encipherment, etc.).
                key_usage = cert.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE)
                assert key_usage.value.key_cert_sign

                # Process any policy constraints and policy mappings present in the certificate chain.
                # This example omits the policy constraints and policy mappings validation, as it requires deeper knowledge of the specific policies and organization requirements.

            print("Success: Certificate path validation test passed.")
            return True
        except AssertionError:
            print("Error: Certificate path validation test failed.")
            return False

#if __name__ == "__main__":
#    ip_or_hostname = input("Enter IP or hostname: ")
#    port = int(input("Enter port number: "))
tester = CertificateTester("www.example.com",443)
tester.test_certificate_path_validation()
