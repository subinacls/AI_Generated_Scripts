import sys
import logging
from multiprocessing import Process
from paratrooper.webserver import webserverkicker
from paratrooper.sniffer import sniffer
from paratrooper.server import tserver
from paratrooper.cleanup import cleanup

# Setup logging configuration
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        logger.info("Starting the Paratrooper application...")

        # Start the web server as a separate process
        wsk = Process(target=webserverkicker)
        wsk.daemon = True
        wsk.start()

        # Start the sniffer module
        sniffer()

        # Start the Paratrooper TCP server
        tserver()

    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt detected, performing cleanup.")
        cleanup()
        sys.exit(0)

    except Exception as e:
        logger.error(f"Unhandled exception occurred: {e}")
        cleanup()
        sys.exit(1)
