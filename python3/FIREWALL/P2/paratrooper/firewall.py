import subprocess
import logging

# Setup logger
logger = logging.getLogger(__name__)

def sendcommands(command):
    """
    Executes a shell command on the system.
    """
    try:
        logger.debug(f"Executing command: {command}")
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        raise e

class IptBuilder:
    """
    Manages iptables firewall rules.
    """

    def flush_fw(self):
        """
        Flush all firewall rules.
        """
        logger.info("Flushing firewall rules")
        sendcommands("iptables -F")

    def basic_fw(self):
        """
        Sets basic firewall rules to prevent unauthorized traffic.
        """
        logger.info("Setting up basic firewall rules")
        sendcommands("iptables -P INPUT DROP")
        sendcommands("iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT")
