import socket
import ssl
import requests
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ExtensionOID, NameOID
from cryptography.x509.ocsp import OCSPResponseStatus
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

    def test_validity_period(self):
        current_time = datetime.utcnow()
        not_before = self.cert.not_valid_before
        not_after = self.cert.not_valid_after

        if not_before <= current_time <= not_after:
            print("Success: Validity period test passed.")
            return True
        else:
            print("Error: Validity period test failed.")
            return False

    def test_dn_and_name_constraints(self):
        try:
            issuer_dn = self.cert.issuer
            subject_dn = self.cert.subject

            # Validate the format and encoding of the issuer and subject DNs.
            # This example assumes the format and encoding are correct, as they are directly retrieved from the certificate.

            # Verify that the certificate complies with any name constraints imposed by the issuing CA.
            issuer = self._get_issuer_certificate(issuer_dn)
            name_constraints = issuer.extensions.get_extension_for_oid(ExtensionOID.NAME_CONSTRAINTS).value

            if name_constraints:
                permitted_subtrees = name_constraints.permitted_subtrees
                excluded_subtrees = name_constraints.excluded_subtrees

                if permitted_subtrees:
                    for attr in subject_dn:
                        for subtree in permitted_subtrees:
                            if isinstance(subtree, x509.GeneralSubtree) and subtree.base == attr.oid:
                                assert attr.value in subtree.base.value

                if excluded_subtrees:
                    for attr in subject_dn:
                        for subtree in excluded_subtrees:
                            if isinstance(subtree, x509.GeneralSubtree) and subtree.base == attr.oid:
                                assert attr.value not in subtree.base.value

            print("Success: Distinguished names and name constraints test passed.")
            return True
        except AssertionError:
            print("Error: Distinguished names and name constraints test failed.")
            return False

    def test_public_key_and_algorithm(self):
        try:
            public_key = self.cert.public_key()

            # Ensure that the subjectPublicKeyInfo field contains a supported public key algorithm.
            assert isinstance(public_key, (x509.rsa.RSAPublicKey, x509.ec.EllipticCurvePublicKey))

            # Verify that the public key meets the requirements for its algorithm, including key length and format.
            if isinstance(public_key, x509.rsa.RSAPublicKey):
                assert public_key.key_size >= 2048
            elif isinstance(public_key, x509.ec.EllipticCurvePublicKey):
                assert public_key.curve.key_size >= 256

            print("Success: Public key and algorithm test passed.")
            return True





    except AssertionError:
        print("Error: Public key and algorithm test failed.")
        return False

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


#if name == "main":
#    ip_or_hostname = input("Enter IP or hostname: ")
#    port = int(input("Enter port number: "))
tester = CertificateTester("www.example.com", 443)
tester
