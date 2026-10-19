from netbox.plugins import PluginConfig


class NetBoxNetScanConfig(PluginConfig):
    name = "netbox_netscan"
    verbose_name = "Network Scanner"
    description = "Network discovery, risk recommendations, and topology mapping"
    version = "0.1.0"
    author = "Armando Guerra"
    base_url = "netscan"
    min_version = "4.7.0"
    max_version = "4.7.99"
    default_settings = {
        "targets": ["192.168.100.0/24"],
        "scheduled_scans": False,
        "allow_public_networks": False,
        "minimum_prefix_length": 24,
        "scan_ports": [21, 22, 23, 53, 80, 139, 443, 445, 554, 631, 1883, 3389, 5900, 8080, 8443, 9100],
        "nmap_path": "nmap",
        "nmap_timing": "T3",
        "host_timeout": "90s",
    }

    def ready(self):
        super().ready()
        from . import jobs  # noqa: F401


config = NetBoxNetScanConfig

