import ipaddress

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import View

from netbox.plugins.utils import get_plugin_config

from .jobs import ScanNetworkJob
from .models import DiscoveredHost, ScanRun


class NetScanPermissionMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True


class DashboardView(NetScanPermissionMixin, View):
    permission_required = "netbox_netscan.view_discoveredhost"

    def get(self, request):
        hosts = DiscoveredHost.objects.select_related("device", "netbox_ip")
        return render(request, "netbox_netscan/dashboard.html", {
            "hosts": hosts[:250],
            "runs": ScanRun.objects.all()[:10],
            "targets": get_plugin_config("netbox_netscan", "targets", []),
            "risk_count": hosts.filter(risk_score__gte=40).count(),
            "title": "Network discovery",
        })


class HostView(NetScanPermissionMixin, View):
    permission_required = "netbox_netscan.view_discoveredhost"

    def get(self, request, pk):
        try:
            host = DiscoveredHost.objects.select_related("device", "netbox_ip", "last_scan").get(pk=pk)
        except DiscoveredHost.DoesNotExist as exc:
            raise Http404 from exc
        return render(request, "netbox_netscan/host.html", {"object": host, "title": str(host)})


class ScanRunView(NetScanPermissionMixin, View):
    permission_required = "netbox_netscan.view_scanrun"

    def get(self, request, pk):
        try:
            run = ScanRun.objects.get(pk=pk)
        except ScanRun.DoesNotExist as exc:
            raise Http404 from exc
        return render(request, "netbox_netscan/scanrun.html", {"object": run, "title": str(run)})


class TriggerScanView(NetScanPermissionMixin, View):
    permission_required = "netbox_netscan.add_scanrun"

    def post(self, request):
        configured = get_plugin_config("netbox_netscan", "targets", [])
        target = request.POST.get("target", "")
        if target not in configured:
            messages.error(request, "The selected target is not configured for scanning.")
            return redirect("plugins:netbox_netscan:dashboard")
        ScanNetworkJob.enqueue(target=target, user=request.user)
        messages.success(request, f"Scan of {target} was queued.")
        return redirect("plugins:netbox_netscan:dashboard")


class NetworkMapView(NetScanPermissionMixin, View):
    permission_required = "netbox_netscan.view_discoveredhost"

    def get(self, request):
        targets = get_plugin_config("netbox_netscan", "targets", [])
        networks = [ipaddress.ip_network(value) for value in targets]
        graph = {"nodes": [], "links": []}
        for network in networks:
            graph["nodes"].append({"id": str(network), "label": str(network), "kind": "network", "risk": 0})
        for host in DiscoveredHost.objects.all():
            parent = next((str(network) for network in networks if ipaddress.ip_address(host.ip_address_text) in network), "Unassigned")
            if parent == "Unassigned" and not any(node["id"] == parent for node in graph["nodes"]):
                graph["nodes"].append({"id": parent, "label": parent, "kind": "network", "risk": 0})
            graph["nodes"].append({
                "id": f"host-{host.pk}", "label": host.hostname or host.ip_address_text,
                "ip": host.ip_address_text, "kind": host.device_type or "unknown", "risk": host.risk_score,
                "last_seen": host.last_seen.isoformat(), "url": host.get_absolute_url(),
            })
            graph["links"].append({"source": parent, "target": f"host-{host.pk}"})
        return render(request, "netbox_netscan/map.html", {"graph": graph, "title": "Network map"})

