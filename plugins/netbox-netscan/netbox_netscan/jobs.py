from django.db import transaction
from django.utils import timezone

from core.choices import JobIntervalChoices
from ipam.models import IPAddress
from netbox.jobs import JobRunner, system_job
from netbox.plugins.utils import get_plugin_config

from .choices import HostStatusChoices, ScanStatusChoices
from .models import DiscoveredHost, ScanRun
from .scanning import NmapScanner
from .scanning.risk import assess_risk, classify_device


def plugin_setting(name, default=None):
    return get_plugin_config("netbox_netscan", name, default)


class ScanNetworkJob(JobRunner):
    class Meta:
        name = "Network discovery scan"

    def run(self, target=None, *args, **kwargs):
        targets = [target] if target else plugin_setting("targets", [])
        scanner = NmapScanner(
            executable=plugin_setting("nmap_path", "nmap"),
            timing=plugin_setting("nmap_timing", "T3"),
            host_timeout=plugin_setting("host_timeout", "90s"),
            allow_public=plugin_setting("allow_public_networks", False),
            minimum_prefix_length=plugin_setting("minimum_prefix_length", 24),
        )
        for scan_target in targets:
            self._scan_target(scanner, scan_target)

    def _scan_target(self, scanner, target):
        run = ScanRun.objects.create(
            target=target,
            status=ScanStatusChoices.STATUS_RUNNING,
            started_at=timezone.now(),
        )
        self.logger.info("Starting safe network scan for %s", target)
        try:
            hosts, commands = scanner.scan(target, plugin_setting("scan_ports", []))
            risky_hosts = self._persist_hosts(hosts, run)
            run.status = ScanStatusChoices.STATUS_COMPLETED
            run.hosts_found = len(hosts)
            run.risky_hosts = risky_hosts
            run.command_summary = commands
            self.logger.info("Scan of %s found %d active hosts (%d risky)", target, len(hosts), risky_hosts)
        except Exception as exc:
            run.status = ScanStatusChoices.STATUS_FAILED
            run.error = str(exc)
            self.logger.error("Scan of %s failed: %s", target, exc)
            raise
        finally:
            run.finished_at = timezone.now()
            run.save()

    @transaction.atomic
    def _persist_hosts(self, hosts, run):
        observed_at = timezone.now()
        risky_hosts = 0
        for data in hosts:
            existing = DiscoveredHost.objects.filter(ip_address_text=data["ip"]).first()
            netbox_ip = IPAddress.objects.filter(address__net_host=data["ip"]).first()
            previous_mac = existing.mac_address if existing else ""
            score, reasons, recommendations = assess_risk(
                data, known_in_netbox=netbox_ip is not None, previous_mac=previous_mac
            )
            device = None
            if netbox_ip and netbox_ip.assigned_object:
                device = getattr(netbox_ip.assigned_object, "device", None)
            defaults = {
                "mac_address": data.get("mac", ""),
                "hostname": data.get("hostname", ""),
                "vendor": data.get("vendor", ""),
                "device_type": classify_device(data),
                "os_guess": data.get("os", ""),
                "services": data.get("services", []),
                "last_seen": observed_at,
                "risk_score": score,
                "risk_reasons": reasons,
                "recommendations": recommendations,
                "netbox_ip": netbox_ip,
                "device": device,
                "last_scan": run,
            }
            if not existing:
                defaults["first_seen"] = observed_at
                defaults["status"] = HostStatusChoices.STATUS_KNOWN if netbox_ip else HostStatusChoices.STATUS_NEW
            elif existing.status != HostStatusChoices.STATUS_IGNORED:
                defaults["status"] = HostStatusChoices.STATUS_KNOWN if netbox_ip else HostStatusChoices.STATUS_NEW
            DiscoveredHost.objects.update_or_create(ip_address_text=data["ip"], defaults=defaults)
            if score >= 40:
                risky_hosts += 1
        return risky_hosts


@system_job(interval=JobIntervalChoices.INTERVAL_HOURLY)
class ScheduledNetworkScanJob(ScanNetworkJob):
    class Meta:
        name = "Scheduled network discovery scan"

    def run(self, *args, **kwargs):
        if not plugin_setting("scheduled_scans", False):
            self.logger.info("Scheduled scans are disabled in PLUGINS_CONFIG")
            return
        super().run(*args, **kwargs)

