import ssl
import socket
import subprocess

class TLSTester:
    def __init__(self, host, port, protocol='TCP'):
        self.host = host
        self.port = port
        self.protocol = protocol.upper()
        self.ssl_version = ssl.PROTOCOL_TLSv1_2 # default to TLSv1.2
        self.ciphers = []
        self.dhe_groups = []
        self.hash_algorithms = []
        self.signature_algorithms = []
        self.psk_ciphers = []

    def _test_dtls(self):
        dtls = subprocess.run(['openssl', 's_client', '-dtls1', '-connect', f'{self.host}:{self.port}'], input=b'Q', capture_output=True)
        if dtls.returncode == 0:
            print('DTLS test passed')
            return True
        else:
            print('DTLS test failed')
            return False

    def _test_ciphers(self):
        supported_ciphers = subprocess.run(['openssl', 'ciphers', '-V', 'ALL', '-connect', f'{self.host}:{self.port}'], capture_output=True, text=True).stdout
        for line in supported_ciphers.splitlines():
            cipher = line.split()[1]
            if 'TLS_' in cipher and 'EXP' not in cipher:
                self.ciphers.append(cipher)
                if 'FAIL' in line:
                    print(f'Unsupported cipher: {cipher}')
                    return False
        print(f'Supported ciphers: {", ".join(self.ciphers)}')
        return True

    def _test_mandatory_ciphers(self):
        mandatory_ciphers = [
            'TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256',
            'TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384'
        ]
        for cipher in mandatory_ciphers:
            if cipher not in self.ciphers:
                print(f'Missing mandatory cipher: {cipher}')
                return False
        print('Mandatory ciphers test passed')
        return True

    def _test_recommended_ciphers(self):
        recommended_ciphers = [
            'TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384',
            'TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384'
        ]
        for cipher in recommended_ciphers:
            if cipher not in self.ciphers:
                print(f'Missing recommended cipher: {cipher}')
                return False
        print('Recommended ciphers test passed')
        return True

    def _test_aead_pfs_ciphers(self):
        unsupported_ciphers = []
        for cipher in self.ciphers:
            if 'AEAD' not in cipher:
                continue
            if 'DHE' not in cipher and 'ECDHE' not in cipher:
                unsupported_ciphers.append(cipher)
        if unsupported_ciphers:
            print(f'Unsupported AEAD and PFS ciphers: {", ".join(unsupported_ciphers)}')
            return False
        else:
            print('AEAD and PFS ciphers test passed')
            return True

    def _test_dhe_groups(self):
        unsupported_groups = []
        for group in self.dhe_groups:
            if group not in ['secp256r1', 'secp384r1']:
                unsupported_groups.append(group)
        if unsupported_groups:
            print(f'Unsupported DHE groups: {", ".join(unsupported_groups)}')
            return False
        else:
            print('DHE groups test passed')
            return True

    def _test_hash_algorithms(self):
        unsupported_algorithms = []
        for algorithm in self.hash_algorithms:
            if algorithm not in ['sha256', 'sha384']:
                unsupported_algorithms.append(algorithm)
        if unsupported_algorithms:
            print(f'Unsupported hash algorithms: {", ".join(unsupported_algorithms)}')
            return False
        else:
            print('Hash algorithms test passed')
            return True

    def _test_signature_algorithms(self):
        unsupported_algorithms = []
        for algorithm in self.signature_algorithms:
            if algorithm not in ['ecdsa', 'ecdsa-with-SHA384', 'rsa_pss_rsae_sha256', 'rsa_pkcs1_sha256']:
                unsupported_algorithms.append(algorithm)
        if unsupported_algorithms:
            print(f'Unsupported signature algorithms: {", ".join(unsupported_algorithms)}')
            return False
        else:
            print('Signature algorithms test passed')
            return True

    def _test_tls_compression(self):
        supported_extensions = subprocess.run(['openssl', 's_client', '-prexit', '-connect', f'{self.host}:{self.port}'], input=b'Q', capture_output=True, text=True).stdout
        if 'Truncated HMAC' in supported_extensions:
            print('Truncated HMAC extension test failed')
            return False
        if 'server name' not in supported_extensions:
            print('SNI extension test failed')
            return False
        if 'Session resumption' not in supported_extensions:
            print('Session resumption extension test failed')
            return False
        if 'Extended master secret' not in supported_extensions:
            print('Extended master secret extension test failed')
            return False
        if 'Supported Groups' not in supported_extensions:
            print('Supported Groups extension test failed')
            return False
        if 'OCSP status' not in supported_extensions:
            print('OCSP status extension test failed')
            return False
        print('TLS compression test passed')
        return True

    def _test_tls_extensions(self):
        extensions = subprocess.run(['openssl', 's_client', '-prexit', '-connect', f'{self.host}:{self.port}'], input=b'Q', capture_output=True, text=True).stdout
        for line in extensions.splitlines():
            if 'Extension' in line:
                extension = line.split(':')[1].strip()
                if extension not in ['status_request', 'supported_groups', 'extended_master_secret']:
                    print(f'Unsupported extension: {extension}')
                    return False
        print('TLS extensions test passed')
        return True

    def _test_psk_ciphers(self):
        psk_ciphers = [
            'TLS_DHE_PSK_WITH_AES_128_GCM_SHA256',
            'TLS_ECDHE_PSK_WITH_AES_128_GCM_SHA256',
            'TLS_ECDHE_PSK_WITH_AES_256_GCM_SHA384'
        ]
        for cipher in psk_ciphers:
            if cipher in self.ciphers:
                self.psk_ciphers.append(cipher)
        if 'TLS_DHE_PSK_WITH_AES_128_GCM_SHA256' not in self.psk_ciphers:
            print('PSK cipher test failed: missing TLS_DHE_PSK_WITH_AES_128_GCM_SHA256')
            return False
        if 'TLS_ECDHE_PSK_WITH_AES_128_GCM_SHA256' not in self.psk_ciphers:
            print('PSK cipher test failed: missing TLS_ECDHE_PSK_WITH_AES_128_GCM_SHA256')
            return False
        if 'TLS_ECDHE_PSK_WITH_AES_256_GCM_SHA384' not in self.psk_ciphers:
            print('PSK cipher test failed: missing TLS_ECDHE_PSK_WITH_AES_256_GCM_SHA384')
            return False
        print('PSK cipher test passed')
        return True

    def test_tls(self):
        # Test DTLS
        if self.protocol == 'UDP':
            if not self._test_dtls():
                return False

        # Test TCP
        if self.protocol != 'TCP':
            print('Only TCP protocol is supported')
            return False

        # Test supported ciphers
        if not self._test_ciphers():
            return False

        # Test mandatory ciphers
        if not self._test_mandatory_ciphers():
            return False

        # Test recommended ciphers
        if not self._test_recommended_ciphers():
            return False

        # Test AEAD and PFS ciphers
        if not self._test_aead_pfs_ciphers():
            return False

        # Test DHE groups
        if not self._test_dhe_groups():
            return False

        # Test hash algorithms
        if not self._test_hash_algorithms():
            return False

        # Test signature algorithms
        if not self._test_signature_algorithms():
            return False

        # Test TLS compression
        if not self._test_tls_compression():
            return False

        # Test TLS extensions
        if not self._test_tls_extensions():
            return False

        # Test PSK ciphers
        if not self._test_psk_ciphers():
            return False

        print('All tests passed')
        return True
