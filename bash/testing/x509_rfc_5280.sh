"""
RFC 5280, titled "Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile," 
is a specification that establishes a standard format and validation process for X.509 certificates and CRLs 
(Certificate Revocation Lists) in the context of the Internet PKI (Public Key Infrastructure).

X.509 certificates are digital documents used to verify the identity of entities, such as individuals, organizations, 
or servers, in various applications, including SSL/TLS for secure web communication. A certificate binds a public key 
to an entity by including information such as the entity's name, the public key, the issuing Certificate Authority (CA), 
and the certificate's validity period.

RFC 5280 describes the structure of X.509 certificates and CRLs and provides guidelines on how to interpret and process them. 
The specification outlines various fields and extensions used in certificates, such as:

    Version: Indicates the certificate version (X.509v3 is the most recent and widely used version).
    Serial Number: A unique identifier assigned by the issuing CA.
    Signature Algorithm: The algorithm used by the CA to sign the certificate.
    Issuer: The name of the CA that issued the certificate.
    Validity: The certificate's validity period, including the start (Not Before) and end (Not After) dates.
    Subject: The name of the entity to which the certificate is issued.
    Subject Public Key Info: The public key and its associated algorithm.

Additionally, RFC 5280 defines the path validation process, which involves checking a certificate chain from the end-entity 
certificate to a trusted root CA, ensuring that the chain is properly formed and that each certificate in the chain complies 
with the constraints and requirements specified in the standard.

In summary, RFC 5280 provides a comprehensive framework for creating, interpreting, and validating X.509 certificates and CRLs 
in the Internet PKI, thus ensuring the interoperability and security of digital certificates in various applications.

To test a certificate against RFC 5280, you can use OpenSSL, a widely-used cryptographic library and toolkit. OpenSSL provides 
tools for handling X.509 certificates and can help ensure that a certificate complies with the constraints and requirements 
specified in RFC 5280.

Here's a step-by-step guide to testing a certificate against RFC 5280 using OpenSSL:

Obtain the certificate to test. You can either get it from a file, or you can download it from a server by connecting to the hostname 
and port number. To download the certificate, use the following command:

    echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | openssl x509 -outform PEM > certificate.pem

Replace example.com with the hostname or IP address and 443 with the port number.

Verify the certificate chain. To do this, you'll need the certificate itself and the intermediate and root CA certificates. You can usually 
download the intermediate and root CA certificates from the CA's website or obtain them from the server. Save these certificates in separate 
files or concatenate them into a single file.Suppose you have the intermediate and root certificates in a file called ca-bundle.pem. 
You can now verify the certificate chain using the following command:

    openssl verify -purpose sslserver -CAfile ca-bundle.pem certificate.pem

Test the certificate against RFC 5280 using the -x509_strict flag:

    openssl verify -x509_strict -purpose sslserver -CAfile ca-bundle.pem certificate.pem

This command checks the certificate against the constraints and requirements specified in RFC 5280.

If the certificate complies with RFC 5280, OpenSSL will output a message like this:

    certificate.pem: OK

If the certificate doesn't comply with RFC 5280, OpenSSL will display an error message indicating the issue.

Keep in mind that the OpenSSL verify command only covers a subset of RFC 5280 requirements, and certain checks might not be implemented. 
However, it is a useful tool to identify common issues and ensure basic compliance with the standard.
"""
test_rfc5280() {
  if [ $# -lt 2 ] || [ $# -gt 3 ]; then
    echo "Usage: test_rfc5280 <ip_or_hostname> <port> [chain_file]"
    return 1
  fi

  local ip_or_hostname="$1"
  local port="$2"
  local cert_file="cert.pem"
  local chain_file_provided=0

  if [ $# -eq 3 ]; then
    chain_file="$3"
    chain_file_provided=1
  else
    chain_file="chain.pem"
  fi

  if [ $chain_file_provided -eq 0 ]; then
    # Get the certificate and the chain
    echo | openssl s_client -connect "${ip_or_hostname}:${port}" -servername "${ip_or_hostname}" -showcerts 2>/dev/null | awk '/BEGIN CERTIFICATE/,/END CERTIFICATE/' > "${chain_file}"
  fi

  # Extract the end-entity certificate
  awk '/BEGIN CERTIFICATE/{flag=1} flag{print > "cert.pem"} /END CERTIFICATE/{flag=0; exit}' "${chain_file}"

  # Check if the certificate exists and is not empty
  if [ ! -s "${cert_file}" ]; then
    echo "Error: Failed to retrieve the certificate."
    rm -f "${cert_file}"
    [ $chain_file_provided -eq 0 ] && rm -f "${chain_file}"
    return 1
  fi

  # Check if the certificate is X.509v3
  local version=$(openssl x509 -in "${cert_file}" -text -noout 2>/dev/null | grep "Version" | awk '{print $2}')
  if [ "${version}" != "3" ]; then
    echo "Error: The certificate is not X.509v3."
    openssl x509 -in "${cert_file}" -text -noout
    rm -f "${cert_file}"
    [ $chain_file_provided -eq 0 ] && rm -f "${chain_file}"
    return 1
  fi

  # Test the certificate against RFC 5280
  local result=$(openssl verify -x509_strict -purpose sslserver -CAfile "${chain_file}" "${cert_file}" 2>&1)

  # Clean up
  rm -f "${cert_file}"
  [ $chain_file_provided -eq 0 ] && rm -f "${chain_file}"

  # Check the result
  if [[ "${result}" =~ ": OK" ]]; then
    echo "Success: ${result} The certificate complies with RFC 5280."
    return 0
  else
    echo "Error: ${result} The certificate does not comply with RFC 5280."
    return 1
  fi
};

# Example usage:
# test_rfc5280 "www.example.com" 443
# or with a provided chain file:
# test_rfc5280 "www.example.com" 443 "provided_chain.pem"
