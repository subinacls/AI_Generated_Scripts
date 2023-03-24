import concurrent.futures
import socket
import json
import logging
import ipaddress


class PortScanner:
    def __init__(self, ports=None):
        self.ports = ports or [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8081, 8443]

    def scan(self, cidr_ranges, output_file):
        try:
            logging.basicConfig(level=logging.DEBUG)
            #logging.basicConfig(level=None)
            logger = logging.getLogger(__name__)
            logger.debug(f"Scanning CIDR ranges: {cidr_ranges}")
            results = {}
            with concurrent.futures.ProcessPoolExecutor() as process_pool:
                for ip, open_ports in zip(self._get_ips(cidr_ranges), process_pool.map(self._scan_ports, self._get_ips(cidr_ranges))):
                    if open_ports:
                        results[str(ip)] = open_ports
            with open(output_file, 'w') as f:
                json.dump(results, f)
        except:
            pass

    def _scan_ports(self, ip):
        try:
            open_ports = []
            for port in self.ports:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.1)
                        try:
                            if s.connect_ex((str(ip), port)) == 0:
                                open_ports.append(port)
                        except Exception as e:
                            continue
                except Exception as e:
                    continue
            if open_ports:
                print("{}: {}".format(ip,open_ports))
                return str(ip), open_ports
        except:
            return str("null"), []

    def _get_ips(self, cidr_ranges):
        try:
            ips = []
            for cidr_range in cidr_ranges:
                ips += list(ipaddress.IPv4Network(cidr_range))
            return ips
        except Exception as e:
            pass

if __name__ == '__main__':
    scanner = PortScanner()
    #scanner = PortScanner([443,8443,10443])
    results = scanner.scan(['1.2.3.0/8'],'results.json')
    #results = scanner.scan(['1.2.3.0/8','12.3.0/16'], 'results.json')
    print(json.dumps(results))
