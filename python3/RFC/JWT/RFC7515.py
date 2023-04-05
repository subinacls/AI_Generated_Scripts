import json
import os
from datetime import datetime, timedelta
from typing import Union
from hashlib import sha256
from hmac import HMAC
from base64 import urlsafe_b64encode

class RFC7515TestSuite:
    def __init__(self):
        self.results = {
            "signature_verification": False,
            "tampered_signature": False,
            "tampered_payload": False,
            "invalid_algorithm": False,
            "invalid_key": False,
            "multiple_signatures": False,
            "expired_signature": False,
            "nbf_validation": False,
            "header_parameter_validation": False,
            "compact_serialization": False,
        }

    def run_tests(self, payload: Union[str, dict], key: Union[str, bytes], key_is_file: bool):
        # Load the payload
        if isinstance(payload, str):
            payload = json.loads(payload)

        # Load the key
        if key_is_file:
            with open(key, "rb") as f:
                key = f.read()

        # Convert the key to bytes if necessary
        if isinstance(key, str):
            key = key.encode()

        # Get the JWS header
        header = {"alg": "HS256", "typ": "JWT"}

        # Create a JWS with a valid signature
        valid_jws = self._create_jws(payload, header, key)

        # Test signature verification
        self._test_signature_verification(valid_jws, key)

        # Test tampered signature
        self._test_tampered_signature(valid_jws)

        # Test tampered payload
        self._test_tampered_payload(payload, header, key)

        # Test invalid algorithm
        self._test_invalid_algorithm(payload, header, key)

        # Test invalid key
        self._test_invalid_key(payload, header, key)

        # Test multiple signatures
        self._test_multiple_signatures(payload, header, key)

        # Test expired signature
        self._test_expired_signature(payload, header, key)

        # Test NBF validation
        self._test_nbf_validation(payload, header, key)

        # Test header parameter validation
        self._test_header_parameter_validation(payload, header, key)

        # Test compact serialization
        self._test_compact_serialization(valid_jws)

        # Save results to file
        self._save_results()

    def _create_jws(self, payload, header, key):
        # Encode the header and payload as JSON
        encoded_header = self._base64url_encode(json.dumps(header).encode())
        encoded_payload = self._base64url_encode(json.dumps(payload).encode())

        # Create the signature
        signing_input = b".".join([encoded_header, encoded_payload])
        signature = self._create_signature(signing_input, key)

        # Encode the signature as base64url
        encoded_signature = self._base64url_encode(signature)

        # Create the JWS
        jws = b".".join([encoded_header, encoded_payload, encoded_signature])
        return jws

    def _create_signature(self, signing_input, key):
        return HMAC(key, signing_input, sha256).digest()

    def _base64url_encode(self, data):
        return urlsafe_b64encode(data).rstrip(b"=").decode()

    def _test_signature_verification(self, jws, key):
        try:
            header, payload, signature = jws.split(b".")
            signing_input = b".".join([header, payload])
            expected_signature = self._create_signature(signing_input, key)
            if signature == self._base64url_encode(expected_signature).encode():
               
            self.results["signature_verification"] = True
    except:
        pass

    def _test_tampered_signature(self, jws):
        try:
            header, payload, signature = jws.split(b".")
            tampered_signature = self._base64url_encode(signature[::-1])
            tampered_jws = b".".join([header, payload, tampered_signature])
            header, payload, signature = tampered_jws.split(b".")
            if not self._verify_jws(header, payload, signature):
                self.results["tampered_signature"] = True
        except:
            pass

    def _test_tampered_payload(self, payload, header, key):
        tampered_payload = payload.copy()
        tampered_payload["foo"] = "bar"
        tampered_jws = self._create_jws(tampered_payload, header, key)
        header, payload, signature = tampered_jws.split(b".")
        if not self._verify_jws(header, payload, signature):
            self.results["tampered_payload"] = True

    def _test_invalid_algorithm(self, payload, header, key):
        invalid_header = header.copy()
        invalid_header["alg"] = "invalid_algorithm"
        invalid_jws = self._create_jws(payload, invalid_header, key)
        header, payload, signature = invalid_jws.split(b".")
        if not self._verify_jws(header, payload, signature):
            self.results["invalid_algorithm"] = True

    def _test_invalid_key(self, payload, header, key):
        invalid_key = b"invalid_key"
        invalid_jws = self._create_jws(payload, header, invalid_key)
        header, payload, signature = invalid_jws.split(b".")
        if not self._verify_jws(header, payload, signature):
            self.results["invalid_key"] = True

    def _test_multiple_signatures(self, payload, header, key):
        header["alg"] = "HS512"
        jws1 = self._create_jws(payload, header, key)
        header["alg"] = "HS384"
        jws2 = self._create_jws(payload, header, key)
        header["alg"] = "HS256"
        jws3 = self._create_jws(payload, header, key)
        jws = b".".join([jws1, jws2, jws3])
        if not self._verify_jws(header, payload, jws.split(b".")[-1]):
            self.results["multiple_signatures"] = True

    def _test_expired_signature(self, payload, header, key):
        now = datetime.utcnow()
        exp = now - timedelta(minutes=1)
        header["alg"] = "HS256"
        header["exp"] = int(exp.timestamp())
        jws = self._create_jws(payload, header, key)
        header, payload, signature = jws.split(b".")
        if not self._verify_jws(header, payload, signature):
            self.results["expired_signature"] = True

    def _test_nbf_validation(self, payload, header, key):
        now = datetime.utcnow()
        nbf = now + timedelta(minutes=1)
        header["alg"] = "HS256"
        header["nbf"] = int(nbf.timestamp())
        jws = self._create_jws(payload, header, key)
        header, payload, signature = jws.split(b".")
        if not self._verify_jws(header, payload, signature):
            self.results["nbf_validation"] = True

    def _test_header_parameter_validation(self, payload, header, key):
        header["invalid_parameter"] = "invalid_value"
        invalid_jws = self._create_jws(payload, header, key)
        header, payload, signature = invalid_jws.split(b".")
        if not self._verify_jws(header, payload, signature):
            self.results["header_parameter_validation"] = True

    def _test_compact_serialization(self, jws):
        try:
            header, payload, signature = jws.split(b".")
            compact_jws = b".".join([header, payload, signature])
            if compact_jws == jws:
                self.results["compact_serialization"] = True
        except:
            pass

    def _verify_jws(self, header, payload, signature):
        try:
            header = json.loads(self._base64url_decode(header))
            alg = header.get("alg")
            key = self._get_key(header)
            signing_input = b".".join([header.encode(), payload.encode()])
            expected_signature = self._create_signature(signing_input, key)
            return signature == self._base64url_encode(expected_signature).encode()
        except:
            return False

    def _get_key(self, header):
        if header["alg"] == "HS256":
            return key
        elif header["alg"] == "HS384":
            return key[:48]
        elif header["alg"] == "HS512":
            return key[:64]
        else:
            raise ValueError("Unsupported algorithm")

    def _base64url_decode(self, data):
        padding = b"=" * (4 - (len(data) % 4))
        return urlsafe_b64decode(data + padding).decode()

    def _save_results(self):
        filename = "rfc7515_test_results.json"
        if os.path.exists(filename):
            with open(filename, "r") as f:
                results = json.load(f)
        else:
            results = {}
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        results[timestamp] = self.results
        with open(filename, "w") as f:
            json.dump(results, f, indent=4)

#
#
# To use this test suite, you can create an instance of `RFC7515TestSuite` and call the `run_tests`
# method with the JSON payload and signing key:
#
# suite = RFC7515TestSuite()
# payload = {"sub": "1234567890", "name": "John Doe", "iat": 1516239022}
# key = b"secret"
# key_is_file = False
# suite.run_tests(payload, key, key_is_file)
