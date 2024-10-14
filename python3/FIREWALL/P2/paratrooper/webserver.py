import http.server
import socketserver

PORT = 8000

def webserverkicker():
    """
    Web server to monitor the application.
    """
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    print(f"Webserver started at http://localhost:{PORT}")
    httpd.serve_forever()
