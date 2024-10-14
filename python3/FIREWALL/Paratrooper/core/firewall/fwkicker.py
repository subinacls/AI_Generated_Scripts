'''
from logger_manager import LoggerManager
from iptbuilder import IptBuilder  # Assuming IptBuilder class is in iptbuilder.py

# Initialize logger
logger = LoggerManager()
'''

def build_firewall():
    """
    Build and execute the iptables firewall rules before the server starts.
    This ensures all incoming traffic is processed according to the firewall rules.
    """
    try:
        logger.log('Starting firewall build process...', 'info')

        # Flush existing iptables firewall rules
        ipt_builder = IptBuilder()
        ipt_builder.flush_fw()  # Flush iptables

        # Build the baseline firewall rules for the server
        ipt_builder.basic_fw()  # Set baseline rules
        
        logger.log('Firewall build process completed successfully.', 'info')

    except Exception as firewall_build_failed:
        logger.log(f"Firewall build process failed: {firewall_build_failed}", 'error')
        return 0

# Run the firewall build before server execution
build_firewall()
