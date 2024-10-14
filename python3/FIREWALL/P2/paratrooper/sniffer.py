from scapy.all import sniff
import logging

# Setup logger
logger = logging.getLogger(__name__)

def packet_handler(packet):
    """
    Process captured packet.
    """
    logger.debug(f"Packet captured: {packet.summary()}")

def sniffer():
    """
    This function starts the sniffer to capture packets.
    """
    logger.info("Sniffer started. Listening for packets...")
    try:
        sniff(prn=packet_handler, filter="ip", store=0)
    except Exception as e:
        logger.error(f"Sniffer encountered an error: {e}")
        raise e
