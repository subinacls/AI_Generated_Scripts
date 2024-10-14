import __builtin__ as bi

### SET VARS ####
'''
Sets some basic static values assigned to the server globally
Sets server port Paratrooper listens on:
    serverport = 6543
Sets diagnostics output of various modules within the application if true
    diag = True
Available for the entire application when global is used

Diagnostics needs to be initialized outside of any try/except
'''
try:
    bi.enableserver = True  ## Ensure the server is enabled at start
    bi.enablesniffer = True  ## Default value set for the sniffing capabilities
    bi.threadlist = list()  ## Makes default thread list
    bi.serverport = 6543  ## Set the serverport var to reflect the bi.serverport contents
    serverport = bi.serverport  ## Set the servers port where the server is listening
    bi.initday = str(datetime.datetime.now()).split()[0]  ## Set the initial date
    initday = bi.initday  ## Set the initday var to reflect the bi.initday contents
    bi.revports = list()  ## Sets useful list to identify any listening MSF handler ports
    bi.shelled = list()  ## Sets useful list to identify any established connections to MSF handler
    bi.ipsetmsflist = list()  ## Sets a list of current ip addresses within the msfshell group of ipset
    bi.DET = 0
    if bi.diag:
        print 'VAR diag: %s' % diag
        print 'VAR serverport: %s' % serverport
        print 'VAR initday: %s' % initday
        print 'VAR bi.revports: %s' % bi.revports
        print 'VAR bi.shelled: %s' % bi.shelled
        print 'VAR bi.ipsetmsflist: %s' % bi.ipsetmsflist
except Exception as setvarsfailed:
    if bi.diag:
        print 'Setting variables failed: %s' % setvarsfailed
    sys.exit(0)
