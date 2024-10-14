'''
import socket
import threading
import logging
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler

# Initialize logging
logging.basicConfig(
    filename='/path/to/logfile.log',  # Update path as needed
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TCPServer')
'''


class MyTCPServer:
    """
    This class handles the configuration and initialization of the TCP server.
    """

    def __init__(self, server_port):
        self.server_port = server_port
        self.thread_list = []

    def start_server(self):
        """
        Starts the TCP server.
        """
        logger.info("Starting the TCP server on port %s", self.server_port)

        try:
            # Allow socket reuse
            TCPServer.allow_reuse_address = True

            # Initialize the server
            server = ThreadedTCPServer(('', int(self.server_port)), ThreadedTCPRequestHandler)
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.setDaemon(True)  # Set as daemon so it doesn't block the program from exiting

            # Start the server thread
            self.thread_list.append(server_thread)
            server_thread.start()
            logger.info("TCP server started on port %s", self.server_port)

            # Start named pipe handler in another thread (assuming you have fifohandler defined elsewhere)
            fifo_thread = threading.Thread(target=fifohandler)
            fifo_thread.setDaemon(True)
            self.thread_list.append(fifo_thread)
            fifo_thread.start()
            logger.info("Named pipe handler started.")

        except Exception as e:
            logger.error("Failed to start TCP server: %s", e)

    def stop_server(self):
        """
        Stops the TCP server and terminates all associated threads.
        """
        logger.info("Stopping the TCP server...")
        try:
            for thread in self.thread_list:
                if thread.is_alive():
                    thread.join(timeout=1)
            logger.info("All server threads have been stopped.")
        except Exception as e:
            logger.error("Error stopping server threads: %s", e)
