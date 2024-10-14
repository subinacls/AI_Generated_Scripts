'''
import schedule
import time
import sys
from logger_manager import LoggerManager
from msf_handler import MSFhandler

# Python 2/3 compatibility for the `print()` function and exception handling
try:
    input = raw_input  # Python 2 compatibility
except NameError:
    pass  # Python 3 compatibility

# Initialize the logger
logger = LoggerManager()
'''
# Define the scheduled jobs with logging
def schedule_msf_tasks():
    logger.log('Scheduling MSF handler tasks...', 'info')

    # Schedule the job to scan for listener ports every 2 minutes
    schedule.every(2).minutes.do(scan_msf_ports)
    logger.log('Scheduled: MSF port scanning every 2 minutes.', 'info')

    # Schedule the job to identify ESTABLISHED shells every 1 minute
    schedule.every(1).minutes.do(scan_shelled_hosts)
    logger.log('Scheduled: Shelled host scanning every 1 minute.', 'info')

    # Schedule the job to drop shelled hosts every 30 seconds
    schedule.every(30).seconds.do(drop_shelled_hosts)
    logger.log('Scheduled: Drop shelled hosts every 30 seconds.', 'info')
