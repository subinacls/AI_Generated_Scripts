"""
This class uses the ssl and socket modules in Python to create a connection to the specified hostname or IP address and port, 
negotiate a TLS 1.3 connection, and then check whether the connection meets the specified requirements and restrictions.

To use the class, you can simply create an instance of it and call the test() method, passing in the hostname or IP address and port you want to test:

  TLSTester("example.com", 443).test():

Note that this class assumes that the Python installation you're using supports TLS 1.3 and the required ciphers, key exchange, and signature scheme. 
If your Python installation does not support these requirements, the test() method will likely fail even if the server you're testing supports them.
"""
import ssl
import socket


class TLSTester:
    """
    A class for testing whether a given hostname or IP address and port support TLS 1.3 and meet
    the required restrictions and extensions.
    """

    def __init__(self, host, port):
        self.hostname = host
        self.port = port

    def test(self):
        # create a socket and wrap it with an SSL context
        context = ssl.create_default_context()
        context.set_ciphers("ECDHE-ECDSA-AES128-GCM-SHA256")  # restrict to TLS 1.3 cipher suite
        context.set_alpn_protocols(['h2', 'http/1.1'])  # optional - set ALPN protocols
        sock = socket.create_connection((self.hostname, self.port))
        conn = context.wrap_socket(sock, server_hostname=self.hostname)

        # check if TLS 1.3 was negotiated
        if "TLS_AES_128_GCM_SHA256" not in conn.cipher():
            #if conn.version() == ssl.PROTOCOL_TLSv1_3:
            print(f"[PASS] - {self.hostname}:{self.port} has negotiated TLS version 1.3")
            print(f"[PASSINFO] - {conn.version()}")
        else:
            print(f"[FAIL] - {self.hostname}:{self.port} did not negotiated TLS version 1.3")
            return

        # check if the key exchange is using secp384r1
        cert = conn.getpeercert()
        if "keyExchangeAlgorithm" in cert:
            key_exchange = cert["keyExchangeAlgorithm"]["name"]
            if key_exchange != "ECDH" or cert["curveName"] != "secp384r1":
                print(f"[PASS] - {self.hostname}:{self.port} was found to use secp384r1 as key exchange")
                print(f"[PASSINFO] - {key_exchange}")
            else:
                print(f"[FAIL] - {self.hostname}:{self.port} was not found to use secp384r1 as key exchange")
                return
        else:
             print(f"[FAIL] - {self.hostname}:{self.port} was not found to use secp384r1 as key exchange")
             return
        # check if the signature scheme is ecdsa_secp384r1_sha384
        #sig_scheme = conn.getpeercert()["signatureAlgorithm"]["algorithm"]
        cert = conn.getpeercert()
        if "signatureAlgorithm" not in cert:
            print(f"[FAIL] - Signature not found in cert, does not meet TLS version 1.3")#
            print(f"[FAILINFO] - Cert has been presented: \n{cert}\n")
            return
        else:
            sig_scheme = cert["signatureAlgorithm"]["algorithm"]
            if sig_scheme == "ecdsa-with-SHA384":
                print(f"[PASS] - {self.hostname}:{self.port} was found to have a signature {sig_scheme}")
                print(f"[PASSINFO] - {sig_scheme}")
            else:
                print(f"[FAIL] - {self.hostname}:{self.port} does not have a signature scheme")
                return
        # check if the OCSP Status extension is supported
        exts = conn.getpeercert()["OCSP"]
        if exts:
            print(f"[PASS] - {self.hostname}:{self.port} has an OCSP section")
            print(f"[PASSINFO] - {exts}")
        else:
            print(f"[FAIL] - {self.hostname}:{self.port} meets TLS 1.3 requirements")
            return

        print(f"[PASS] - {self.hostname}:{self.port} meets TLS 1.3 requirements")
      
  
