'''
import os
import signal
import psutil  # For managing processes more safely
'''

def detcord():
    # Get the current file name and process ID
    current_file = os.path.basename(__file__)
    current_pid = os.getpid()
    
    # Iterate through all processes and kill the ones matching this file
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            # Skip the current process itself and match processes related to the current script
            if proc.info['pid'] != current_pid and current_file in ' '.join(proc.info['cmdline']):
                os.kill(proc.info['pid'], signal.SIGKILL)
                print(f"Killed process with PID: {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return "All matching processes killed."
