'''
import subprocess
import sys
from logger_manager import LoggerManager

# Ensure compatibility between Python 2 and 3 for builtins
if sys.version_info[0] < 3:
    import __builtin__ as bi  # Python 2
else:
    import builtins as bi     # Python 3

# Initialize logger
logger = LoggerManager()
'''

def webserverkicker():
    """
    Launches the Admin Web Panel in a new tmux window within the 'paratrooper' session.
    The AdminWebPanel.py script is executed in the new tmux window.
    """
    try:
        logger.log('Launching Admin Web Panel in new tmux window within paratrooper session...', 'info')

        # Create the 'paratrooper' session if it does not exist, then create a new window for the web server
        cmd = 'tmux new-session -d -s paratrooper || tmux new-window -t paratrooper -n admin_panel "python ./AdminWebPanel.py"'
        subprocess.Popen(cmd, shell=True)
        
        logger.log('Admin Web Panel launched in tmux window in paratrooper session.', 'info')
    
    except Exception as pyfailedtolaunch:
        logger.log(f"Failed to launch the Python web server: {pyfailedtolaunch}", 'error')
