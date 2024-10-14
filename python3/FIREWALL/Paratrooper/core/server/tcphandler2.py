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


class ThreadedTCPRequestHandler(StreamRequestHandler):
    """
    This is the Threaded TCP Request handler which interrogates the supplied data for conformity
    before offloading the contents. If the contents do not pass the baseline requirements, the
    packets are logged as bad guys and further sorted for offline analysis to produce a threat model.
    """

    def handle(self):
        logger.info("Handling request from client: %s:%s", self.client_address[0], self.client_address[1])

        while bi.enableserver:
            try:
                schedule.run_pending()  # Run any scheduled tasks
            except Exception as e:
                logger.error("Failed to run scheduled jobs: %s", e)

            global clientip, clientport, data, dataset
            self.request.settimeout(10)  # Set the socket timeout value

            try:
                clientip = self.client_address[0]
                clientport = self.client_address[1]
            except Exception as e:
                logger.error("Failed to get client address: %s", e)
                return

            try:
                data = self.rfile.readlines()  # Receive data from the client
                logger.info("Received data from %s:%s", clientip, clientport)
            except Exception as e:
                data = ''
                logger.error("Failed to receive data: %s", e)
                DBHandler().import_everyone_client(clientip)
                BadDBHandler().import_datalog((clientip, ''))
                self.wfile.write(data.encode())
                return

            if len(data) <= 4000:  # Check data length
                logger.warning("Data from %s:%s does not meet minimal length requirements", clientip, clientport)
                BadDBHandler().import_datalog((clientip, data))
                DBHandler().import_everyone_client(clientip)
                self.wfile.write(''.encode())
                return

            try:
                dataset = clientip, data  # Create dataset tuple
            except Exception as e:
                logger.error("Failed to create dataset: %s", e)

            try:
                DataRouter().offload(dataset)  # Offload data for processing
            except Exception as e:
                logger.error("Failed to offload data from %s:%s: %s", clientip, clientport, e)
                BadDBHandler().import_datalog((clientip, data))
                DBHandler().import_everyone_client(clientip)
                self.wfile.write(''.encode())
                return

            self.wfile.write(''.encode())
            return


class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    """
    Threaded TCP server that allows handling requests in separate threads.
    """
    pass


