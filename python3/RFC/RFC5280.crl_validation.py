import socket
import ssl
import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ExtensionOID
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

    def test_crl_validation(self):
        try:
            crl_dp_ext = self.cert.extensions.get_extension_for_oid(ExtensionOID.CRL_DISTRIBUTION_POINTS)
            crl_url = crl_dp_ext.value[0].full_name[0].value

            crl_pem = requests.get(crl_url).content
            crl = x509.load_pem_x509_crl(crl_pem, default_backend())

            issuer = self._get_issuer_certificate(self.cert.issuer)

            # Verify the CRL's signature, issuer, and validity period.
            assert crl.issuer == issuer.subject
            crl.signature_hash_algorithm.verify(crl.signature, crl.tbs_certlist_bytes, issuer.public_key())

            assert crl.last_update <= x509.datetime_from_utc_time(datetime.utcnow()) <= crl.next_update

            # Check that the CRL complies with any CRL distribution points specified in the certificate.
            # This example assumes the CRL distribution point is correct, as it is directly retrieved from the certificate.

            # Confirm that the CRL contains the correct extensions, such as CRL number and authority key identifier.
            crl_number_ext = crl.extensions.get_extension_for_oid(ExtensionOID.CRL_NUMBER)
            assert crl_number_ext is not None

            akid_ext = crl.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_KEY_IDENTIFIER)
            assert akid_ext is not None

            print("Success: CRL validation test passed.")
            return True
        except AssertionError:
            print("Error: CRL validation test failed.")
            return False

    def _get_issuer_certificate(self, issuer_name):
        store = certifi.where()
        with open(store, "rb") as store_file:
            cert_data = store_file.read()

        for cert in x509.split_pem_certificates(cert_data):
            cert = x509.load_pem_x509_certificate(cert, default_backend())
            if cert.subject == issuer_name:
                return cert

        raise ValueError("Issuer certificate not found")

#if __name__ == "__main__":
#    ip_or_hostname = input("Enter IP or hostname: ")
#    port = int(input("Enter port number: "))
tester = CertificateTester("www.example.com",443)
tester.test_crl_validation()
