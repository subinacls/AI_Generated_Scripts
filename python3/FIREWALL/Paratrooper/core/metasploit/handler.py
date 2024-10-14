import subprocess
import sys
from logger_manager import LoggerManager

# Ensure compatibility between Python 2 and 3 for builtins
if sys.version_info[0] < 3:
    import __builtin__ as bi  # Python 2
else:
    import builtins as bi     # Python 3

# Initialize the logger
logger = LoggerManager()

class MSFhandler:
    def __init__(self):
        logger.log('Entering: MSFhandler()', 'info')

    @staticmethod
    def start_msflisteners(resource_file):
        logger.log('Entering: MSFhandler().start_msflisteners()', 'info')
        
        # Used to launch msf resource file for multihandler and jobs
        cmd = 'msfconsole -r ' + str(resource_file)
        logger.log('VAR cmd: {}'.format(cmd), 'debug')
        
        sendcommands(cmd)
        
        logger.log('Exiting: MSFhandler().start_msflisteners()', 'info')

    @staticmethod
    def getmsfports():
        logger.log('Entering: MSFhandler().getmsfports()', 'info')

        try:
            bi.revports = list()
            logger.log('MSFhandler().getmsfports() - VAR bi.revports: {}'.format(bi.revports), 'debug')

            # Execute commands to get ports
            ns = subprocess.Popen(('netstat', '-antelop'), stdout=subprocess.PIPE)
            glisten = subprocess.Popen(('grep', 'LISTEN'), stdin=ns.stdout, stdout=subprocess.PIPE)
            gruby = subprocess.Popen(('grep', '-i', 'ruby'), stdin=glisten.stdout, stdout=subprocess.PIPE)
            ports = subprocess.Popen(('cut', '-d:', '-f2'), stdin=gruby.stdout, stdout=subprocess.PIPE)
            mports = subprocess.Popen(('cut', '-d ', '-f1'), stdin=ports.stdout, stdout=subprocess.PIPE)
            sortu = subprocess.check_output(('sort', '-u'), stdin=mports.stdout)

            logger.log('MSFhandler().getmsfports() - VAR mports: {}'.format(sortu), 'debug')

            for xport in sortu.split():
                bi.revports.append(xport)
                logger.log('MSFhandler().getmsfports() - xport: {}'.format(xport), 'debug')

            logger.log('MSF Reverse ports list: {}'.format(bi.revports), 'info')

        except Exception as getmsfportsfailed:
            logger.log('MSFhandler().getmsfports() - Failed: {}'.format(getmsfportsfailed), 'error')

    @staticmethod
    def getshelledhost():
        logger.log('Entering: MSFhandler().getshelledhost()', 'info')

        try:
            bi.shelled = []
            logger.log('MSFhandler().getshelledhost() - VAR bi.shelled: {}'.format(bi.shelled), 'debug')

            # Execute commands to get shelled hosts
            ns = subprocess.Popen(('netstat', '-antelop'), stdout=subprocess.PIPE)
            glisten = subprocess.Popen(('grep', 'ESTABLISHED'), stdin=ns.stdout, stdout=subprocess.PIPE)
            gruby = subprocess.Popen(('grep', '-i', 'ruby'), stdin=glisten.stdout, stdout=subprocess.PIPE)
            ports = subprocess.Popen(('cut', '-d:', '-f2'), stdin=gruby.stdout, stdout=subprocess.PIPE)
            shrink = subprocess.Popen(('tr', '-s', ' '), stdin=ports.stdout, stdout=subprocess.PIPE)
            ipaddr = subprocess.Popen(('cut', '-d ', '-f2'), stdin=shrink.stdout, stdout=subprocess.PIPE)
            sortu = subprocess.check_output(('sort', '-u'), stdin=ipaddr.stdout)

            logger.log('MSFhandler().getshelledhost() - VAR sortu: {}'.format(sortu), 'debug')

            for xms in sortu.split():
                bi.shelled.append(xms)
                logger.log('MSFhandler().getshelledhost() - Suspected shelled IP: {}'.format(xms), 'debug')

            logger.log('MSFhandler().getshelledhost() - Shelled host list: {}'.format(bi.shelled), 'info')

        except Exception as getshelledhostfailed:
            logger.log('MSFhandler().getshelledhost() - Failed: {}'.format(getshelledhostfailed), 'error')

    @staticmethod
    def dropshelledhost():
        logger.log('Entering: MSFhandler().dropshelledhost()', 'info')

        try:
            logger.log('MSFhandler().dropshelledhost() - VAR bi.revports: {}'.format(bi.revports), 'debug')

            if len(bi.revports) == 0:
                logger.log('No MSF listening ports found', 'info')
                return

            if len(bi.shelled) != 0:
                logger.log('Found shelled host: {}'.format(bi.shelled), 'info')

                try:
                    # Check users in msfshell group
                    ms = subprocess.Popen(('ipset', 'list', 'msfshell'), stdout=subprocess.PIPE)
                    grepip = subprocess.check_output(('grep', '-E', '([0-9]{1,3}\.){3}([0-9]{1,3})'), stdin=ms.stdout)

                    for xms in grepip.split():
                        bi.ipsetmsflist.append(xms)
                        logger.log('Found in ipsetmsflist: {}'.format(xms), 'debug')

                except Exception as nousersinlist:
                    logger.log('No users identified in the msfshell group', 'warning')

                removed = []
                established = []

                for xipsetip in bi.ipsetmsflist:
                    if xipsetip not in bi.shelled:
                        cmd = 'ipset del msfshell ' + str(xipsetip) + ' 2>/dev/null'
                        sendcommands(cmd)
                        removed.append(xipsetip)
                        logger.log('Removed {} from msfshell group'.format(xipsetip), 'info')
                    else:
                        established.append(xipsetip)
                        logger.log('Connection still established for: {}'.format(xipsetip), 'debug')

                logger.log('Hosts removed: {}'.format(removed), 'info')
                logger.log('Hosts still established: {}'.format(established), 'info')

                bi.ipsetmsflist = []

        except Exception as dropshelledhostfailed:
            logger.log('MSFhandler().dropshelledhost() - Failed: {}'.format(dropshelledhostfailed), 'error')
