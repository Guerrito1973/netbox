from netbox.api.serializers import NetBoxModelSerializer

from netbox_netscan.models import DiscoveredHost, ScanRun


class ScanRunSerializer(NetBoxModelSerializer):
    class Meta:
        model = ScanRun
        fields = (
            "id", "url", "display", "target", "status", "started_at", "finished_at",
            "hosts_found", "risky_hosts", "command_summary", "error", "created", "last_updated",
        )
        brief_fields = ("id", "url", "display", "target", "status")


class DiscoveredHostSerializer(NetBoxModelSerializer):
    class Meta:
        model = DiscoveredHost
        fields = (
            "id", "url", "display", "ip_address_text", "mac_address", "hostname", "vendor",
            "device_type", "os_guess", "services", "first_seen", "last_seen", "status",
            "risk_score", "risk_reasons", "recommendations", "device", "netbox_ip", "last_scan",
            "created", "last_updated",
        )
        brief_fields = ("id", "url", "display", "ip_address_text", "risk_score", "last_seen")

