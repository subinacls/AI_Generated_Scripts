import sys
from multiprocessing import Process
from paratrooper.webserver import webserverkicker
from paratrooper.sniffer import sniffer
from paratrooper.server import tserver
from paratrooper.cleanup import cleanup

if __name__ == "__main__":
    try:
        # Start the web server as a separate process
        wsk = Process(target=webserverkicker)
        wsk.daemon = True
        wsk.start()

        # Start the sniffer module
        sniffer()

        # Start the Paratrooper TCP server
        tserver()

    except KeyboardInterrupt:
        # Perform cleanup on exit
        cleanup()
        sys.exit(0)
