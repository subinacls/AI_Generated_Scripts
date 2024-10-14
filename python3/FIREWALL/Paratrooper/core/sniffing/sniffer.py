'''
import subprocess
import sys
from logger_manager import LoggerManager

# Ensure compatibility between Python 2 and 3
if sys.version_info[0] < 3:
    import __builtin__ as bi  # Python 2
else:
    import builtins as bi     # Python 3

# Initialize logger
logger = LoggerManager()
'''

def sniffer():
    """
    Launches the sniffer in a new tmux window within the 'paratrooper' session.
    The sniffer.py script is executed in the new tmux window.
    """
    try:
        logger.log('Launching sniffer in new tmux window within paratrooper session...', 'info')

        # Create the 'paratrooper' session if it does not exist, then create a new window for the sniffer
        cmd = 'tmux new-session -d -s paratrooper || tmux new-window -t paratrooper -n sniffer "python sniffer.py"'
        subprocess.Popen(cmd, shell=True)
        
        logger.log('Sniffer launched in tmux window in paratrooper session.', 'info')
    
    except Exception as failedtolaunchsniffer:
        logger.log(f"Failed to launch sniffer: {failedtolaunchsniffer}", 'error')
