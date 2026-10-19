import unittest

from module_loader import parser

parse_nmap_xml = parser.parse_nmap_xml


SAMPLE = """<?xml version="1.0"?>
<nmaprun><host><status state="up"/><address addr="192.168.100.10" addrtype="ipv4"/>
<address addr="AA:BB:CC:DD:EE:FF" addrtype="mac" vendor="Example Inc"/>
<hostnames><hostname name="printer.local"/></hostnames><ports>
<port protocol="tcp" portid="9100"><state state="open"/><service name="jetdirect" product="Printer"/></port>
<port protocol="tcp" portid="22"><state state="closed"/></port>
</ports></host></nmaprun>"""


class ParserTests(unittest.TestCase):
    def test_parses_live_host_and_open_service(self):
        hosts = parse_nmap_xml(SAMPLE)
        self.assertEqual(len(hosts), 1)
        self.assertEqual(hosts[0]["ip"], "192.168.100.10")
        self.assertEqual(hosts[0]["vendor"], "Example Inc")
        self.assertEqual(hosts[0]["services"][0]["port"], 9100)

    def test_ignores_down_hosts(self):
        self.assertEqual(parse_nmap_xml('<nmaprun><host><status state="down"/></host></nmaprun>'), [])


if __name__ == "__main__":
    unittest.main()
