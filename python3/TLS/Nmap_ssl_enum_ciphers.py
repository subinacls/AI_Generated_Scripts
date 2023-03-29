import nmap
import json

class TLSScanner:
    def __init__(self, target, port, file_name):
        self.target = target
        self.port = port
        self.file_name = file_name
        self.nm = nmap.PortScanner()
        self.results = {}


    def scan(self):
        print(f"scanning {self.target}")
        self.nm.scan(self.target, arguments=f'-p {self.port} -sCV --script=/usr/share/nmap/scripts/ssl-enum-ciphers.nse')
        print(self.nm)
        hosts = self.nm.all_hosts()
        print(hosts)
        for host in self.nm.all_hosts():
            host_results = []
            print(f"{self.nm[host]['tcp'][443]['script']['ssl-enum-ciphers']}")
            """
            script_output = self.nm[host]['tcp'][self.port]['script']
            # ['ssl-enum-ciphers']
            print(f"script output: {script_output}")
            host_results.append({
                'port': self.port,
                'name': script_output['name'],
                'product': script_output['product'],
                'version': script_output['version'],
                'ciphers': script_output['ciphers'],
               'protocols': script_output['protocols']
            })
            print(f"{host_results}")
            self.results[host] = host_results
            self.save_results()
            """
    def save_results(self):
        with open(self.file_name, 'w') as f:
           json.dump(self.results, f, indent=4)


scanner = TLSScanner('www.google.com', '443', 'python3_nmap_tls_scan_results.json')
scanner.scan()
