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

def sendcommands(cmds):
    """
    Sends commands to the underlying operating system and returns the result.
    SECURITY CONCERN: This function executes system-level commands, so it should be used with caution.
    """
    logger.log('Entering: sendcommands()', 'info')

    try:
        # Log a security warning since executing system commands can be risky
        logger.log('SECURITY WARNING: Executing system-level commands. Ensure this is run with proper permissions.', 'warning')

        # Execute the command using subprocess
        result = subprocess.Popen(cmds, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = result.communicate()  # Capture both stdout and stderr

        # If there's output, log it
        if output:
            output_lines = output.decode('utf-8').splitlines()  # Convert bytes to string
            for line in output_lines:
                if line.strip():  # Ignore blank lines
                    logger.log(f"sendcommands() - Command output: {line.strip()}", 'info')

        # If there are errors, log them
        if errors:
            error_lines = errors.decode('utf-8').splitlines()  # Convert bytes to string
            for err in error_lines:
                if err.strip():  # Ignore blank lines
                    logger.log(f"sendcommands() - Command error: {err.strip()}", 'error')

        logger.log('Exiting: sendcommands()', 'info')

    except Exception as e:
        logger.log(f"sendcommands() - Failed to execute commands: {e}", 'error')
        logger.log('Exiting: sendcommands() due to error', 'info')
        return None
