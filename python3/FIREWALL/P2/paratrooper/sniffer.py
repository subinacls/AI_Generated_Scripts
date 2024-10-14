from scapy.all import sniff

def packet_handler(packet):
    """
    Process captured packet.
    """
    print(f"Packet captured: {packet.summary()}")

def sniffer():
    """
    This function starts the sniffer to capture packets.
    """
    print("Sniffer started. Listening for packets...")
    sniff(prn=packet_handler, filter="ip", store=0)
