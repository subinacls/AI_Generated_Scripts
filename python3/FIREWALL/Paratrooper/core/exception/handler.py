import sys
import __builtin__ as bi

def excepthandler():
    sysverinfo = sys.version_info  ## Get system version information
    sysapiver = sys.api_version  ## Get API versions of the python interpreter and C
    sysver = sys.version  ## Get the installed python version information
    sysplatform = sys.platform  ## Get the platform information about the underlying OS
    syspath = sys.path  ## Get the search PATH environment variable for python
    ## Must call the frame related calls from their respective exceptions and set as builtin
    # sysframe    = sys._getframe()  ## Get the current frame on the thread
    sysencoding = sys.getfilesystemencoding()  ## Gets encoding used by the underlying OS
    sysexec = sys.executable  ## Get the systems path for the Python interpreter
    sysexcinfo = sys.exc_info()  ## Gets the execution information in a TUPLE
    ## Must call the frame related calls from their respective exceptions and set as builtin
    # syscurframe = sys_current_frame()  ## Gets the current information about the frame causing the exception
    if bi.diag:
        print "SYSTEM INFORMATION AFTER EXCEPTION IS ENCOUNTERED"
        print "System version information: %s" % sysver
        print "Python interpreter version information: %s" % sysverinfo
        print "Python C interpreter version: %s" % sysapiver
        print "Underlying OS identifier: %s" % sysplatform
        print "Python search PATH: %s" % syspath
        # print "Current Execution Frame: %s" % sysframe
        print "Current system encoding type: %s" % sysencoding
        print "Python interpreter location: %s" % sysexec
        print "Python Execution Exception Tuple: %s" % str(sysexcinfo)
        # print "Current Frame Identifier: %s" % syscurframe
