
'''
import sys
import signal
from logger_manager import LoggerManager

# Ensure compatibility between Python 2 and 3 for builtins
if sys.version_info[0] < 3:
    import __builtin__ as bi  # Python 2
else:
    import builtins as bi     # Python 3

# Initialize logger
logger = LoggerManager()
'''

def signal_handler(signal_received, frame):
    """
    Handles signals like SIGINT (Ctrl+C) and performs necessary cleanup before exiting.
    :param signal_received: Signal that was caught.
    :param frame: Current stack frame.
    """
    try:
        logger.log('Entering: signal_handler()', 'info')
        logger.log('User Interrupt Captured (Signal: {}) - Exiting Paratrooper Server'.format(signal_received), 'warning')
        
        # Run cleanup routine before exiting
        cleanup()
        
        logger.log('Exiting: signal_handler()', 'info')
        logger.log('Exiting Paratrooper Server', 'info')
        sys.exit(0)

    except Exception as e:
        logger.log('Error in signal_handler: {}'.format(e), 'error')
        sys.exit(1)  # Exit with error code if there’s an issue

# Setup signal handling for user interrupts (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
