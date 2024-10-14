import __builtin__ as bi

class AdminCmds:
    def __init__(self):
        pass

    @staticmethod
    def disablediag():
        try:
            bi.diag = ""
            banner()
        except Exception as debugfailseffailed:
            print "Setting diag false failed: %s" % debugfailseffailed

    @staticmethod
    def enablediag():
        try:
            bi.diag = True
            banner()
        except Exception as debugfailseffailed:
            print "Setting diag true failed: %s" % debugfailseffailed
