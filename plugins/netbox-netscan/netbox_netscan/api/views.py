from netbox.api.viewsets import NetBoxModelViewSet

from netbox_netscan.models import DiscoveredHost, ScanRun

from .serializers import DiscoveredHostSerializer, ScanRunSerializer


class ReadOnlyNetBoxModelViewSet(NetBoxModelViewSet):
    http_method_names = ("get", "head", "options")


class DiscoveredHostViewSet(ReadOnlyNetBoxModelViewSet):
    queryset = DiscoveredHost.objects.select_related("device", "netbox_ip", "last_scan")
    serializer_class = DiscoveredHostSerializer


class ScanRunViewSet(ReadOnlyNetBoxModelViewSet):
    queryset = ScanRun.objects.all()
    serializer_class = ScanRunSerializer

