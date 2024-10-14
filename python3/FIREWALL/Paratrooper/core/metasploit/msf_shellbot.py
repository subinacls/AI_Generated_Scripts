'''
import sys
from scapy.all import IP, TCP  # Ensure Scapy is installed and available
from logger_manager import LoggerManager
from msf_handler import sendcommands, shahash

# Ensure compatibility between Python 2 and 3 for builtins
if sys.version_info[0] < 3:
    import __builtin__ as bi  # Python 2
else:
    import builtins as bi     # Python 3

# Initialize logger
logger = LoggerManager()
'''
def shell_bot(pkt):
    """
    Function to listen for new Metasploit service ports and manipulate the system accordingly.

    :param pkt: Packet captured by a sniffer (Scapy).
    """
    while bi.enablesniffer:
        logger.log("Entering: shell_bot()", 'info')
        try:
            # Check if the packet has an IP layer
            if IP in pkt:
                ip_src = pkt[IP].src  # Source IP address
                ip_dst = pkt[IP].dst  # Destination IP address
                logger.log(f'shell_bot() - IP src: {ip_src}, IP dst: {ip_dst}', 'debug')

                # Check if the packet has a TCP layer
                if TCP in pkt:
                    tcp_sport = pkt[TCP].sport  # Source port
                    tcp_dport = pkt[TCP].dport  # Destination port
                    tcp_pay = pkt[TCP].payload  # TCP payload
                    logger.log(f'shell_bot() - TCP src port: {tcp_sport}, TCP dst port: {tcp_dport}', 'debug')

                    # Check if the source IP is already in the shelled list
                    if ip_src in bi.shelled:
                        logger.log(f"shell_bot() - IP {ip_src} is already in bi.shelled list.", 'info')
                        pass
                    else:
                        # Iterate over known Metasploit reverse ports
                        for xport in bi.revports:
                            logger.log(f'shell_bot() - Checking port {xport} against TCP dst port {tcp_dport}', 'debug')

                            # If the destination port matches a known MSF port
                            if int(xport) == tcp_dport:
                                logger.log(f'Match found for MSF listener port {xport}', 'info')

                                # Log TCP payload details
                                logger.log(f'Payload length: {len(tcp_pay)}', 'debug')

                                # If the payload length is 0 (indicative of shell request)
                                if len(tcp_pay) == 0:
                                    payload_hash = shahash(tcp_pay)
                                    logger.log(f"Payload hash: {payload_hash}", 'debug')

                                    # Check if the payload matches the known blank hash value
                                    if payload_hash == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855':
                                        logger.log("Matched hash for incoming shell", 'info')

                                        # Add the requesting source IP to the msfshell group
                                        cmd = f'ipset add msfshell {ip_src} 2>/dev/null'
                                        logger.log(f"Sending command: {cmd}", 'info')
                                        sendcommands(cmd)

                                    return  # Exit after handling the shell
                                else:
                                    logger.log(f'Non-empty payload, skipping. Payload: {tcp_pay}', 'debug')
                                    return
                            else:
                                logger.log(f"No match for port {tcp_dport}. Exiting shell_bot.", 'info')
                                return
                else:
                    logger.log("No TCP layer found in packet. Exiting shell_bot.", 'info')
                    return
            else:
                logger.log("No IP layer found in packet. Exiting shell_bot.", 'info')
                return
        except Exception as shell_botfailed:
            # Log any exceptions that occur during packet processing
            logger.log(f"shell_bot() - General failure: {shell_botfailed}", 'error')
            return
