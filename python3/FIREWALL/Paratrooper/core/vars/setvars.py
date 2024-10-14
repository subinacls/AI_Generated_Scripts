'''
import sys
import datetime

# Ensure compatibility between Python 2 and 3 for builtins
if sys.version_info[0] < 3:
    import __builtin__ as bi  # Python 2
else:
    import builtins as bi     # Python 3

### SET VARS ###
Sets some basic static values assigned to the server globally.
'''

try:
    # Initialize global variables
    bi.enableserver = True  # Ensure the server is enabled at start
    bi.enablesniffer = True  # Default value set for the sniffing capabilities
    bi.threadlist = list()  # Create default thread list
    bi.serverport = 6543  # Set the server port to 6543
    serverport = bi.serverport  # Local variable reflecting the global serverport
    bi.initday = str(datetime.datetime.now()).split()[0]  # Get and set the initial date
    initday = bi.initday  # Local variable reflecting the global initday
    bi.revports = list()  # List of listening MSF handler ports
    bi.shelled = list()  # List of established connections to MSF handler
    bi.ipsetmsflist = list()  # List of current IP addresses within the MSF shell group
    bi.DET = 0  # A global diagnostic variable

    # Output diagnostics if enabled
    if getattr(bi, 'diag', False):  # Check if diagnostics are enabled
        print("VAR diag: {}".format(bi.diag))
        print("VAR serverport: {}".format(serverport))
        print("VAR initday: {}".format(initday))
        print("VAR bi.revports: {}".format(bi.revports))
        print("VAR bi.shelled: {}".format(bi.shelled))
        print("VAR bi.ipsetmsflist: {}".format(bi.ipsetmsflist))

except Exception as setvarsfailed:
    if getattr(bi, 'diag', False):  # Check if diagnostics are enabled
        print("Setting variables failed: {}".format(setvarsfailed))
    sys.exit(1)  # Use exit(1) to indicate an error occurred
