'''
import sys

# Ensure compatibility between Python 2 and 3 for builtins
if sys.version_info[0] < 3:
    import __builtin__ as bi  # Python 2
else:
    import builtins as bi     # Python 3
'''

class AdminCmds:
    def __init__(self):
        pass

    @staticmethod
    def disablediag():
        try:
            bi.diag = ""  # Disable diagnostics by setting to an empty string
            banner()  # Refresh the banner (ensure the banner function is defined)
        except Exception as debugfails:
            print("Setting diag to false failed: {}".format(debugfails))

    @staticmethod
    def enablediag():
        try:
            bi.diag = True  # Enable diagnostics by setting to True
            banner()  # Refresh the banner (ensure the banner function is defined)
        except Exception as debugfails:
            print("Setting diag to true failed: {}".format(debugfails))
