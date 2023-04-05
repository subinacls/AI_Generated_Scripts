import socket
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.name import Name


class CertificateTester:
    def __init__(self, ip_or_hostname, port, user_ca_cert=None):
        self.ip_or_hostname = ip_or_hostname
        self.port = port
        self.cert = self._get_certificate()
        self.user_ca_cert = user_ca_cert

    def _get_certificate(self):
        with socket.create_connection((self.ip_or_hostname, self.port)) as sock:
            with ssl.wrap_socket(sock, cert_reqs=ssl.CERT_NONE) as ssl_sock:
                pem_cert = ssl.DER_cert_to_PEM_cert(ssl_sock.getpeercert(binary_form=True))
                return x509.load_pem_x509_certificate(pem_cert.encode(), default_backend())

    def check_name_against_constraints(name, permitted_subtrees, excluded_subtrees):
        for rdn in name.rdns:
            for attribute in rdn:
                for subtree in excluded_subtrees:
                    if attribute.oid == subtree.name_constraint:
                        if subtree.name_constraint == x509.NameConstraintsOID.DNS_NAME and attribute.value.endswith(subtree.value):
                            return False
                        if subtree.name_constraint == x509.NameConstraintsOID.RFC822_NAME and attribute.value.endswith(subtree.value):
                            return False
        for rdn in name.rdns:
            for attribute in rdn:
                for subtree in permitted_subtrees:
                    if attribute.oid == subtree.name_constraint:
                        if subtree.name_constraint == x509.NameConstraintsOID.DNS_NAME and attribute.value.endswith(subtree.value):
                            return True
                        if subtree.name_constraint == x509.NameConstraintsOID.RFC822_NAME and attribute.value.endswith(subtree.value):
                            return True
        return False

    def test_distinguished_names_and_constraints(self):
        try:
            # Validate the format and encoding of the issuer and subject DNs.
            assert isinstance(self.cert.issuer, Name)
            assert isinstance(self.cert.subject, Name)
            # Verify that the certificate complies with any name constraints imposed by the issuing CA.
            issuer_cert = self._get_issuer_certificate()
            name_constraints = issuer_cert.extensions.get_extension_for_class(x509.NameConstraints)
            if name_constraints:
                permitted_subtrees = name_constraints.value.permitted_subtrees
                excluded_subtrees = name_constraints.value.excluded_subtrees
                assert check_name_against_constraints(self.cert.subject, permitted_subtrees, excluded_subtrees)
            print("Success: Distinguished names and constraints tests passed.")
            return True
        except AssertionError:
            print("Error: Distinguished names or constraints tests failed.")
            return False

    def _get_issuer_certificate(self, self.user_ca_cert):
        if self.user_ca_cert and os.path.exists(self.user_ca_cert):
            # Load user-provided CA certificate.
            with open(self.user_ca_cert, 'rb') as f:
                pem_data = f.read()
                ca_cert = x509.load_pem_x509_certificate(pem_data, default_backend())
        else:
            # Retrieve CA certificate chain from the remote site.
            with socket.create_connection((self.ip_or_hostname, self.port)) as sock:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                with context.wrap_socket(sock, server_hostname=self.ip_or_hostname) as ssl_sock:
                    pem_chain = ssl_sock.getpeercertchain()
                    ca_cert = None
                    for der_cert in pem_chain:
                        pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)
                        temp_cert = x509.load_pem_x509_certificate(pem_cert.encode(), default_backend())
                        if temp_cert.subject == self.cert.issuer:
                            ca_cert = temp_cert
                            break
                    if ca_cert is None:
                        raise ValueError("Issuer certificate not found in the remote site's certificate chain")
        return ca_cert





# Example usage:
tester = CertificateTester("www.example.com", 443)
tester.test_distinguished_names_and_constraints()
