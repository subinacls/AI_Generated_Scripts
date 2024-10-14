'''
import subprocess
from logger_manager import LoggerManager

# Initialize logger
logger = LoggerManager()
'''

class IptBuilder:
    """
    Class to manage and build iptables firewall rules.
    """

    def __init__(self):
        logger.log("Initializing IptBuilder...", 'info')

    @staticmethod
    def send_firewall_command(cmd):
        """
        Utility function to send commands to the system and capture output/errors.
        """
        try:
            logger.log(f"Executing iptables command: {cmd}", 'info')
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode('utf-8').strip()
            errors = result.stderr.decode('utf-8').strip()
            if output:
                logger.log(f"Command Output: {output}", 'info')
            if errors:
                logger.log(f"Command Errors: {errors}", 'error')
        except Exception as e:
            logger.log(f"Failed to execute command: {e}", 'error')

    def flush_fw(self):
        """
        Flush all firewall rules to allow the server to control incoming/outgoing traffic.
        """
        try:
            logger.log('Flushing iptables rules...', 'info')
            fw_commands = [
                'iptables -F',
                'iptables -t nat -F',
                'iptables -t nat -X',
                'iptables -X',
                'iptables -t mangle -F',
                'iptables -t mangle -X',
                'iptables -P INPUT ACCEPT',
                'iptables -P FORWARD ACCEPT',
                'iptables -P OUTPUT ACCEPT',
                'ipset flush trusted 2>/dev/null',
                'ipset flush msfshell 2>/dev/null'
            ]
            for cmd in fw_commands:
                self.send_firewall_command(cmd)
            self.ipt_diag()  # Trigger iptables logging if diagnostics are enabled
        except Exception as e:
            logger.log(f"Failed to flush iptables rules: {e}", 'error')

    @staticmethod
    def basic_fw():
        """
        Set up the basic firewall rules required for server functionality.
        """
        try:
            logger.log('Setting up basic iptables rules...', 'info')
            fw_commands = [
                'ipset create rejected hash:net 2>/dev/null',
                'ipset create everyone hash:net 2>/dev/null',
                'ipset create trusted hash:net 2>/dev/null',
                'ipset create msfshell hash:net 2>/dev/null',
                'iptables -F',
                'iptables -t nat -F',
                'iptables -t nat -X',
                'iptables -X',
                'iptables -t mangle -F',
                'iptables -t mangle -X',
                'iptables -P INPUT ACCEPT',
                'iptables -P FORWARD ACCEPT',
                'iptables -P OUTPUT ACCEPT',
                'iptables -N INLOG',
                'iptables -I INLOG -m limit --limit 2/min -j LOG --log-prefix "IPTables INLOG Drop - " --log-level 7',
                'iptables -A INLOG -j DROP',
                'iptables -N OUTLOG',
                'iptables -I OUTLOG -m limit --limit 2/min -j LOG --log-prefix "IPTables OUTLOG Drop - " --log-level 7',
                'iptables -A OUTLOG -j DROP'
            ]
            for cmd in fw_commands:
                IptBuilder.send_firewall_command(cmd)
        except Exception as e:
            logger.log(f"Failed to set basic iptables rules: {e}", 'error')

    @staticmethod
    def syn_scan_rules_fw():
        """
        Set up rules to detect and block SYN scanning attempts.
        """
        try:
            logger.log('Setting up SYN scan prevention rules...', 'info')
            fw = (
                'iptables -I INPUT -i eth0 -m set --match-set everyone src -p tcp '
                '-m multiport --dports 1:65535 -m state --state NEW -m recent --set; '
                'iptables -I INPUT -i eth0 -m set --match-set everyone src -p tcp '
                '-m multiport --dports 1:65535 -m state --state NEW -m recent --update '
                '--seconds 1 --hitcount 5 -j DROP'
            )
            IptBuilder.send_firewall_command(fw)
        except Exception as e:
            logger.log(f"Failed to set SYN scan prevention rules: {e}", 'error')

    @staticmethod
    def synflood_fw():
        """
        Set up rules to detect and block SYN flooding attempts.
        """
        try:
            logger.log('Setting up SYN flood prevention rules...', 'info')
            fw = 'iptables -A INPUT -p tcp ! --syn -m state --state NEW -j DROP'
            IptBuilder.send_firewall_command(fw)
        except Exception as e:
            logger.log(f"Failed to set SYN flood prevention rules: {e}", 'error')

    @staticmethod
    def fragcheck_fw():
        """
        Set up rules to detect and block fragmented packets.
        """
        try:
            logger.log('Setting up fragmented packet check rules...', 'info')
            fw = 'iptables -A INPUT -f -j DROP'
            IptBuilder.send_firewall_command(fw)
        except Exception as e:
            logger.log(f"Failed to set fragmented packet check rules: {e}", 'error')

    @staticmethod
    def xmasdrop_fw():
        """
        Set up rules to detect and block malformed XMAS packets.
        """
        try:
            logger.log('Setting up XMAS packet drop rules...', 'info')
            fw = 'iptables -A INPUT -p tcp --tcp-flags ALL ALL -j DROP'
            IptBuilder.send_firewall_command(fw)
        except Exception as e:
            logger.log(f"Failed to set XMAS packet drop rules: {e}", 'error')

    @staticmethod
    def nulldrop_fw():
        """
        Set up rules to detect and block NULL packets.
        """
        try:
            logger.log('Setting up NULL packet drop rules...', 'info')
            fw = 'iptables -A INPUT -p tcp --tcp-flags ALL NONE -j DROP'
            IptBuilder.send_firewall_command(fw)
        except Exception as e:
            logger.log(f"Failed to set NULL packet drop rules: {e}", 'error')

    @staticmethod
    def ipt_diag():
        """
        Set up diagnostic iptables logging rules for tracking dropped packets.
        """
        try:
            logger.log('Setting up diagnostic iptables logging...', 'info')
            IptBuilder.inputlog_fw()
            IptBuilder.outlog_fw()
        except Exception as e:
            logger.log(f"Failed to set diagnostic iptables rules: {e}", 'error')

    @staticmethod
    def inputlog_fw():
        """
        Set up INPUT log rules for diagnostics.
        """
        fw = (
            'iptables -N INLOG; '
            'iptables -I INLOG -m limit --limit 2/min -j LOG --log-prefix "IPTables INLOG Drop - " --log-level 7; '
            'iptables -A INLOG -j DROP'
        )
        IptBuilder.send_firewall_command(fw)

    @staticmethod
    def outlog_fw():
        """
        Set up OUTPUT log rules for diagnostics.
        """
        fw = (
            'iptables -N OUTLOG; '
            'iptables -I OUTLOG -m limit --limit 2/min -j LOG --log-prefix "IPTables OUTLOG Drop - " --log-level 7; '
            'iptables -A OUTLOG -j DROP'
        )
        IptBuilder.send_firewall_command(fw)
