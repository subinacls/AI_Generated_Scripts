import threading
from paratrooper.pipes import fifohandler
from paratrooper.datarouter import DataRouter
from paratrooper.clientdb import DBHandler
from paratrooper.badguydb import BadDBHandler
from SocketServer import StreamRequestHandler, ThreadingMixIn, TCPServer as SocketServer

class ThreadedTCPRequestHandler(StreamRequestHandler):
    def handle(self):
        # Handle incoming TCP requests from clients
        print(f"Handling request from {self.client_address}")
        data = self.rfile.read()
        if data:
            print(f"Received data: {data}")
            dataset = self.client_address[0], data
            DataRouter().offload(dataset)
        else:
            print(f"No data received from {self.client_address}")
            BadDBHandler().import_datalog((self.client_address[0], ''))
            DBHandler().import_everyone_client(self.client_address[0])
        self.wfile.write(b"Response sent")

class ThreadedTCPServer(ThreadingMixIn, SocketServer):
    pass

def tserver():
    try:
        serverport = 8080
        print(f"Starting TCP server on port {serverport}")
        socketserver = ThreadedTCPServer(('', serverport), ThreadedTCPRequestHandler)
        socketserver_thread = threading.Thread(target=socketserver.serve_forever)
        socketserver_thread.setDaemon(True)
        socketserver_thread.start()

        # Start named pipe thread
        fifo_thread = threading.Thread(target=fifohandler)
        fifo_thread.setDaemon(True)
        fifo_thread.start()
        fifo_thread.join()

    except Exception as e:
        print(f"TCP server failed
