'''
import sys

# Ensuring input() works across both versions
try:
    input = raw_input  # In Python 2, raw_input() is used
except NameError:
    pass  # In Python 3, input() is already correct

# Ensure compatibility between Python 2 and 3 for builtins
if sys.version_info[0] < 3:
    import __builtin__ as bi  # Python 2
else:
    import builtins as bi     # Python 3
'''
##### SET DEBUG #####
bi.diag = True  # If True, diagnostics are enabled

from multiprocessing import Process
import sys
from sniffer_module import sniffer  # import sniffer functionality
from server_module import tserver  # import TCP server functionality
from webserver_module import webserverkicker  # import web server functionality
from cleanup_module import cleanup  # import cleanup functionality

def main():
    try:
        # Start the web server as a background process
        wsk = Process(target=webserverkicker)
        wsk.daemon = True
        wsk.start()
        # Start the sniffer
        sniffer()
        # Start the TCP server
        tserver()
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Exiting and cleaning up.")
        cleanup()  # Ensure cleanup is called before exiting
        sys.exit(0)

if __name__ == "__main__":
    main()
