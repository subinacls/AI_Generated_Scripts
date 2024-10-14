import threading
import logging
from paratrooper.pipes import fifohandler
from paratrooper.datarouter import DataRouter
from paratrooper.clientdb import DBHandler
from paratrooper.badguydb import BadDBHandler
from socketserver import StreamRequestHandler, ThreadingMixIn, TCPServer as SocketServer
import schedule

# Setup logger
logger = logging.getLogger(__name__)

class ThreadedTCPRequestHandler(StreamRequestHandler):
    def handle(self):
        logger.debug(f"Handling request from {self.client_address}")
        try:
            data = self.rfile.read()
            if data:
                logger.debug(f"Received data: {data}")
                dataset = self.client_address[0], data
                DataRouter().offload(dataset)
            else:
                logger.warning(f"No data received from {self.client_address}")
                BadDBHandler().import_datalog((self.client_address[0], ''))
                DBHandler().import_everyone_client(self.client_address[0])
            self.wfile.write(b"Response sent")
        except Exception as e:
            logger.error(f"Error handling request from {self.client_address}: {e}")
            raise e

class ThreadedTCPServer(ThreadingMixIn, SocketServer):
    pass

def tserver():
    try:
        serverport = 8080
        logger.info(f"Starting TCP server on port {serverport}")
        socketserver = ThreadedTCPServer(('', serverport), ThreadedTCPRequestHandler)
        socketserver_thread = threading.Thread(target=socketserver.serve_forever)
        socketserver_thread.setDaemon(True)
        socketserver_thread.start()

        # Start named pipe thread
        fifo_thread = threading.Thread(target=fifohandler)
        fifo_thread.setDaemon(True)
        fifo_thread.start()

        while True:
            schedule.run_pending()

    except Exception as e:
        logger.error(f"TCP server encountered an error: {e}")
        raise e
