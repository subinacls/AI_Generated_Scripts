import logging

# Setup logger
logger = logging.getLogger(__name__)

class IPsetBuilder:
    """
    Manages IP sets for cataloging trusted and rejected IPs.
    """

    @staticmethod
    def create_rejected_ips():
        """
        Creates the rejected IP set list.
        """
        logger.info("Creating rejected IP set")
        sendcommands('ipset create rejected hash:net')

    @staticmethod
    def add_rejected_ips(ip):
        """
        Adds an IP to the rejected list.
        """
        logger.info(f"Adding {ip} to rejected IP set")
        sendcommands(f'ipset add rejected {ip}')

    @staticmethod
    def create_trusted_ips():
        """
        Creates the trusted IP set list.
        """
        logger.info("Creating trusted IP set")
        sendcommands('ipset create trusted hash:net')

    @staticmethod
    def add_trusted_ips(ip):
        """
        Adds an IP to the trusted list.
        """
        logger.info(f"Adding {ip} to trusted IP set")
        sendcommands(f'ipset add trusted {ip}')
