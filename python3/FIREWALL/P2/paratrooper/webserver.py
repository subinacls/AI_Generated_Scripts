import http.server
import socketserver
import logging

# Setup logger
logger = logging.getLogger(__name__)

PORT = 8000

def webserverkicker():
    """
    Web server to monitor the application.
    """
    handler = http.server.SimpleHTTPRequestHandler
    try:
        httpd = socketserver.TCPServer(("", PORT), handler)
        logger.info(f"Webserver started at http://localhost:{PORT}")
        httpd.serve_forever()
    except Exception as e:
        logger.error(f"Webserver encountered an error: {e}")
        raise e
