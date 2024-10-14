'''
import subprocess
from logger_manager import LoggerManager

# Initialize logger
logger = LoggerManager()
'''
class IPsetBuilder:
    """
    Class to handle ipset commands for managing IP groups on the system.
    Used to manage and categorize IPs into different access groups such as rejected, trusted, and everyone.
    """

    def __init__(self):
        logger.log("Initializing IPsetBuilder...", 'info')

    @staticmethod
    def send_ipset_command(command):
        """
        Utility function to send ipset commands to the system and handle output/errors.
        """
        try:
            logger.log(f"Executing ipset command: {command}", 'info')
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode('utf-8').strip()
            errors = result.stderr.decode('utf-8').strip()
            if output:
                logger.log(f"Command Output: {output}", 'info')
            if errors:
                logger.log(f"Command Errors: {errors}", 'error')
        except Exception as e:
            logger.log(f"Failed to execute ipset command: {e}", 'error')

    @staticmethod
    def del_rejected_ips():
        """
        Deletes the rejected ipset group.
        """
        logger.log('Deleting rejected IP group...', 'info')
        IPsetBuilder.send_ipset_command('ipset destroy rejected 2>/dev/null')

    @staticmethod
    def flush_rejected_ips():
        """
        Flushes the rejected ipset group.
        """
        logger.log('Flushing rejected IP group...', 'info')
        IPsetBuilder.send_ipset_command('ipset flush rejected 2>/dev/null')

    @staticmethod
    def create_rejected_ips():
        """
        Creates the rejected ipset group.
        """
        logger.log('Creating rejected IP group...', 'info')
        IPsetBuilder.send_ipset_command('ipset create rejected hash:net 2>/dev/null')

    @staticmethod
    def flush_trusted_ips():
        """
        Flushes the trusted ipset group.
        """
        logger.log('Flushing trusted IP group...', 'info')
        IPsetBuilder.send_ipset_command('ipset flush trusted 2>/dev/null')

    @staticmethod
    def create_trusted_ips():
        """
        Creates the trusted ipset group.
        """
        logger.log('Creating trusted IP group...', 'info')
        IPsetBuilder.send_ipset_command('ipset create trusted hash:net 2>/dev/null')

    @staticmethod
    def flush_everyone_ips():
        """
        Flushes the everyone ipset group and adds default CIDR.
        """
        logger.log('Flushing everyone IP group...', 'info')
        IPsetBuilder.send_ipset_command('ipset flush everyone 2>/dev/null; ipset add everyone 0.0.0.0/1 2>/dev/null')

    @staticmethod
    def create_everyone_ips():
        """
        Creates the everyone ipset group and adds default CIDR.
        """
        logger.log('Creating everyone IP group...', 'info')
        IPsetBuilder.send_ipset_command('ipset create everyone hash:net 2>/dev/null; ipset add everyone 0.0.0.0/1 2>/dev/null')

    @staticmethod
    def add_trusted_ips(aticlientip):
        """
        Adds a client IP to the trusted IP group.
        Handles both single IP and CIDR entries.
        """
        logger.log(f'Adding IP {aticlientip} to trusted IP group...', 'info')
        try:
            ipiscidr = str(aticlientip).split('/')[1]  # Split and get CIDR if available
            ipset_command = f'ipset add trusted {aticlientip} 2>/dev/null'
        except IndexError:
            ipset_command = f'ipset add trusted {aticlientip}/32 2>/dev/null'  # Default to /32 for single IPs
        IPsetBuilder.send_ipset_command(ipset_command)

    @staticmethod
    def add_rejected_ips(ariclientip):
        """
        Adds a client IP to the rejected IP group.
        Handles both single IP and CIDR entries.
        """
        logger.log(f'Adding IP {ariclientip} to rejected IP group...', 'info')
        try:
            ipiscidr = str(ariclientip).split('/')[1]  # Split and get CIDR if available
            ipset_command = f'ipset add rejected {ariclientip} 2>/dev/null'
        except IndexError:
            ipset_command = f'ipset add rejected {ariclientip}/32 2>/dev/null'  # Default to /32 for single IPs
        IPsetBuilder.send_ipset_command(ipset_command)

    @staticmethod
    def save_ips():
        """
        Saves the current ipset configuration to disk.
        """
        logger.log('Saving IPset configuration...', 'info')
        IPsetBuilder.send_ipset_command('ipset save > /root/ipset_saved')

    @staticmethod
    def load_ips():
        """
        Loads the ipset configuration from disk.
        """
        logger.log('Loading IPset configuration...', 'info')
        IPsetBuilder.send_ipset_command('ipset restore < /root/ipset_saved')


# Example usage to flush groups
IPsetBuilder().flush_everyone_ips()
IPsetBuilder().flush_trusted_ips()
