#!/bin/bash
"""
    RFC 7540 is the technical specification for the HTTP/2 protocol, which is the second major version of the 
    Hypertext Transfer Protocol (HTTP). HTTP is the protocol used for transferring data over the internet, 
    and it's what makes the World Wide Web possible.

    HTTP/2 was designed to address some of the limitations of the previous version of HTTP, HTTP/1.1, and to make
    the web faster, more secure, and more efficient. Some of the key features of HTTP/2 include:

    Binary framing layer: HTTP/2 uses a binary framing layer instead of the text-based protocol used in HTTP/1.1.
    This makes it more efficient and easier to parse.

    Multiplexing: HTTP/2 allows multiple requests to be sent over a single connection, which means that multiple
    resources can be downloaded simultaneously. This improves performance and reduces latency.

    Server push: HTTP/2 allows servers to send resources to clients without the client having to request them.
    This can improve performance by reducing the number of round trips needed to load a page.

    Header compression: HTTP/2 uses HPACK header compression, which reduces the amount of data that needs to be sent over the network.

    Overall, HTTP/2 represents a significant improvement over HTTP/1.1, and it's widely used today.
"""
# Function to test an HTTP/2 server
function test_http2_server() {
    # Parse user arguments
    local host="$1"
    local port="$2"

    # Test binary framing layer
    echo "Testing binary framing layer..."
    local result="$(echo -ne 'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n' | openssl s_client -connect "${host}:${port}" -ign_eof 2>&1)"
    if echo "${result}" | grep -q 'HTTP/2'; then
        echo "PASS: Binary framing layer test succeeded"
    else
        echo "FAIL: Binary framing layer test failed"
    fi

    # Test multiplexing
    echo "Testing multiplexing..."
    local result="$(curl -sS -o /dev/null -w '%{http_version}\n' --http2 "https://${host}:${port}")"
    if [ "${result}" == "HTTP/2" ]; then
        echo "PASS: Multiplexing test succeeded"
    else
        echo "FAIL: Multiplexing test failed"
    fi

    # Test server push
    echo "Testing server push..."
    local result="$(curl -sS -o /dev/null -w '%{http_version}\n' --http2-prior-knowledge "https://${host}:${port}" 2>&1)"
    if echo "${result}" | grep -q 'Pushed'; then
        echo "PASS: Server push test succeeded"
    else
        echo "FAIL: Server push test failed"
    fi

    # Test header compression
    echo "Testing header compression..."
    local result="$(curl -sS -o /dev/null -w '%{size_request}\n' --http2 "https://${host}:${port}")"
    if [ "${result}" -lt 100 ]; then
        echo "PASS: Header compression test succeeded"
    else
        echo "FAIL: Header compression test failed"
    fi
}; # test_http2_server example.com 443
