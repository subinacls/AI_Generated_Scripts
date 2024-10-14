'''
import socketserver
import threading
from logger_manager import LoggerManager

# Initialize logger
logger = LoggerManager()
'''
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for handling each TCP client connection.
    """
    def handle(self):
        """
        This method handles incoming client connections.
        """
        try:
            logger.log(f"Connection from {self.client_address}", 'info')

            # Receive and handle data (up to 1024 bytes at a time)
            data = self.request.recv(1024).strip()
            logger.log(f"Received data: {data}", 'debug')

            # Echo the data back to the client
            self.request.sendall(data)

        except Exception as e:
            logger.log(f"Error in handling client request: {e}", 'error')

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    This class sets up the TCP server to handle requests in separate threads.
    """
    allow_reuse_address = True  # Allow address reuse for fast server restarts

    def __init__(self, server_address, handler_class):
        super().__init__(server_address, handler_class)
        logger.log(f"Server initialized on {server_address}", 'info')

    def mytcpserver(self):
        """
        Starts the server and handles incoming client connections.
        """
        try:
            with self:
                logger.log('Server started and waiting for connections...', 'info')
                self.serve_forever()  # Start the server loop

        except Exception as e:
            logger.log(f"Server error: {e}", 'error')


# Example of using thread locks to ensure thread-safe operations
lock = threading.Lock()
