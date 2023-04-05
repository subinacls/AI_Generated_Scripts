import socket
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ec

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

    def test_public_key_and_algorithm(self):
        try:
            # Ensure that the subjectPublicKeyInfo field contains a supported public key algorithm.
            public_key = self.cert.public_key()
            supported_algorithms = (rsa.RSAPublicKey, ec.EllipticCurvePublicKey)
            assert isinstance(public_key, supported_algorithms)

            # Verify that the public key meets the requirements for its algorithm, including key length and format.
            if isinstance(public_key, rsa.RSAPublicKey):
                key_size = public_key.key_size
                assert key_size >= 2048
            elif isinstance(public_key, ec.EllipticCurvePublicKey):
                curve_name = public_key.curve.name
                assert curve_name in ('secp256r1', 'secp384r1', 'secp521r1')

            print("Success: Public key and algorithm test passed.")
            return True
        except AssertionError:
            print("Error: Public key and algorithm test failed.")
            return False

#if __name__ == "__main__":
#    ip_or_hostname = input("Enter IP or hostname: ")
#    port = int(input("Enter port number: "))
tester = CertificateTester("www.example.com",443)
tester.test_public_key_and_algorithm()
