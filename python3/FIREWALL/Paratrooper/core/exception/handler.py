'''

Requires the use of the following code:

import sys

# Ensure compatibility between Python 2 and 3 for builtins
if sys.version_info[0] < 3:
    import __builtin__ as bi  # Python 2
else:
    import builtins as bi     # Python 3

This ensures that the handling of bi is used across versions of python
'''
def excepthandler():
    sysverinfo = sys.version_info  # Get system version information
    sysapiver = sys.api_version  # Get API versions of the python interpreter and C
    sysver = sys.version  # Get the installed python version information
    sysplatform = sys.platform  # Get the platform information about the underlying OS
    syspath = sys.path  # Get the search PATH environment variable for python
    sysencoding = sys.getfilesystemencoding()  # Gets encoding used by the underlying OS
    sysexec = sys.executable  # Get the system's path for the Python interpreter
    sysexcinfo = sys.exc_info()  # Gets the execution information in a TUPLE
    if getattr(bi, 'diag', False):  # Check if diagnostics is enabled
        print("SYSTEM INFORMATION AFTER EXCEPTION IS ENCOUNTERED")
        print("System version information: {}".format(sysver))
        print("Python interpreter version information: {}".format(sysverinfo))
        print("Python C interpreter version: {}".format(sysapiver))
        print("Underlying OS identifier: {}".format(sysplatform))
        print("Python search PATH: {}".format(syspath))
        print("Current system encoding type: {}".format(sysencoding))
        print("Python interpreter location: {}".format(sysexec))
        print("Python Execution Exception Tuple: {}".format(sysexcinfo))

'''# Example usage in a try-except block
try:
    # Some code that may raise an exception
    1 / 0  # Example of raising an exception (divide by zero)
except:
    excepthandler()  # Call the exception handler
'''
