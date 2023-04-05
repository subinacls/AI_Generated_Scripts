import socket
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ExtensionOID
from cryptography.x509.ocsp import OCSPResponseStatus
import certifi
import requests

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

    def test_certificate_revocation(self):
        try:
            ocsp_ext = self.cert.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
            ocsp_url = None

            for access_description in ocsp_ext.value:
                if access_description.access_method == x509.oid.AuthorityInformationAccessOID.OCSP:
                    ocsp_url = access_description.access_location.value

            if not ocsp_url:
                raise ValueError("OCSP URL not found in certificate")

            issuer = self._get_issuer_certificate(self.cert.issuer)
            ocsp_request = x509.ocsp.load_der_ocsp_request(x509.ocsp.OCSPRequestBuilder().add_certificate(self.cert, issuer, x509.hashes.SHA1()).build().public_bytes(default_backend()))

            response = requests.post(ocsp_url, data=ocsp_request, headers={'Content-Type': 'application/ocsp-request'})
            ocsp_response = x509.ocsp.load_der_ocsp_response(response.content)

            assert ocsp_response.response_status == OCSPResponseStatus.SUCCESSFUL

            single_response = ocsp_response.response_bytes[0]
            assert single_response.cert_status == x509.ocsp.OCSPCertStatus.GOOD

            print("Success: Certificate revocation test passed.")
            return True
        except AssertionError:
            print("Error: Certificate revocation test failed.")
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

if __name__ == "__main__":
    ip_or_hostname = input("Enter IP or hostname: ")
    port = int(input("Enter port number: "))
    tester = CertificateTester(ip_or_hostname, port)
    tester.test_certificate_revocation()
