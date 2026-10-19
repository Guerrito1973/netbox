from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel

from .choices import HostStatusChoices, ScanStatusChoices


class ScanRun(NetBoxModel):
    target = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=ScanStatusChoices, default=ScanStatusChoices.STATUS_PENDING)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    hosts_found = models.PositiveIntegerField(default=0)
    risky_hosts = models.PositiveIntegerField(default=0)
    command_summary = models.JSONField(default=dict, blank=True)
    error = models.TextField(blank=True)

    class Meta:
        ordering = ("-started_at", "-created")

    def __str__(self):
        return f"{self.target} - {self.status}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_netscan:scanrun", args=[self.pk])


class DiscoveredHost(NetBoxModel):
    ip_address_text = models.GenericIPAddressField(protocol="both", unpack_ipv4=True, unique=True)
    mac_address = models.CharField(max_length=17, blank=True, db_index=True)
    hostname = models.CharField(max_length=255, blank=True)
    vendor = models.CharField(max_length=255, blank=True)
    device_type = models.CharField(max_length=80, blank=True)
    os_guess = models.CharField(max_length=255, blank=True)
    services = models.JSONField(default=list, blank=True)
    first_seen = models.DateTimeField()
    last_seen = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=20, choices=HostStatusChoices, default=HostStatusChoices.STATUS_NEW)
    risk_score = models.PositiveSmallIntegerField(default=0, db_index=True)
    risk_reasons = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    device = models.ForeignKey(
        "dcim.Device", on_delete=models.SET_NULL, related_name="discovered_hosts", null=True, blank=True
    )
    netbox_ip = models.ForeignKey(
        "ipam.IPAddress", on_delete=models.SET_NULL, related_name="discovery_records", null=True, blank=True
    )
    last_scan = models.ForeignKey(
        ScanRun, on_delete=models.SET_NULL, related_name="hosts", null=True, blank=True
    )

    class Meta:
        ordering = ("-risk_score", "ip_address_text")

    def __str__(self):
        return self.hostname or self.ip_address_text

    @property
    def risk_level(self):
        if self.risk_score >= 70:
            return "critical"
        if self.risk_score >= 40:
            return "high"
        if self.risk_score >= 20:
            return "medium"
        return "low"

    def get_absolute_url(self):
        return reverse("plugins:netbox_netscan:discoveredhost", args=[self.pk])

