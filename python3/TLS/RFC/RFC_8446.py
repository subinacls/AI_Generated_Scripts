"""
This class uses the ssl module in Python to establish a TLS connection
  with a remote server at the specified hostname and port. 

The script sets the Application-Layer Protocol Negotiation (ALPN) protocols to ['h2', 'http/1.1'], 
  which means that the client prefers HTTP/2 but also supports HTTP/1.1.

After the TLS handshake is complete,
  the selected_alpn_protocol() method is called on the SSL socket
    this determine which protocol was selected by the server. 

If the selected protocol is h2, 
  then the remote server supports RFC 8446 (TLS 1.3). 
Otherwise, 
  it does not.
"""
import socket
import ssl

class RFC8446Tester:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def test(self):
        context = ssl.create_default_context()
        context.set_alpn_protocols(['h2', 'http/1.1'])

        with socket.create_connection((self.hostname, self.port)) as sock:
            with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                pem_Cert = ssl.DER_cert_to_PEM_cert(ssock.getpeercert(True))
                negotiated_protocol = ssock.selected_alpn_protocol()
                if negotiated_protocol == "h2":
                    print(f"[PASS] - {self.hostname}:{self.port} supports RFC 8446.")
                    print(f"{pem_Cert}")
                else:
                    print(f"[FAIL] - {self.hostname}:{self.port} does not support RFC 8446.")

# Example usage
# tester = RFC8446Tester('example.com', 443)
# tester.test()
