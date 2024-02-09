from scapy.all import sniff, ICMP

def process_packet(packet):
    if ICMP in packet:
        if packet[ICMP].type == 8:
            payload = packet[ICMP].payload
            if payload:
                padded_data = bytes(payload)
                try:
                    decoded_data = padded_data.decode('utf-8')
                    printable_data = ''.join([c if c.isprintable() else f'\\x{ord(c):02x}' for c in decoded_data])
                    print(f"ICMP Echo Request with padded data: {printable_data}")
                except UnicodeDecodeError:
                    hex_data = padded_data.hex()
                    print(f"ICMP Echo Request with non-text padded data (hex): {hex_data}")
            else:
                print("ICMP Echo Request without padded data")

# Start sniffing for ICMP packets
sniff(filter="icmp", prn=process_packet, store=False)


"""
example on server side returned data from padded ICMP


ICMP Echo Request with padded data: mko8UMkmzx2CjbzKEh03t7CGewYNFZp6
ICMP Echo Request with padded data: NPoU84QkrcLoCL4N1VEdK+fNaTcXF12t
ICMP Echo Request with padded data: lx5rvcZPpqZ7TWGOX5IAL+r/l8hDYzUu
ICMP Echo Request with padded data: vzDDVVWXtP8ehcXHoxAQbiR+b1PJrJ5K
ICMP Echo Request with padded data: slfjEiR0qIz28uMTL0NT8C+OsPSbWTPL
ICMP Echo Request with padded data: DD1L4ZFH2hw6U9BUm0Vt5fkKe5oLsYBk
ICMP Echo Request with padded data: yIHb4M+ujVc18WRS6YXCWQxBTlxlU/ja
ICMP Echo Request with padded data: O+XABfjPFFQ2ybv+8u6ViboONAIcKjDl
ICMP Echo Request with padded data: RnOelPx+t8OYkNBLomBIchxD4jAh0qGq
ICMP Echo Request with padded data: sKqNj71OyBNRitS5SkpB45JHVWMKstoa
ICMP Echo Request with padded data: UTu4hyLx0UxppdHEBK01wAtja9bRCSzi
"""
