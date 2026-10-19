import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("dcim", "0251_fix_ltree_cascade_triggers"),
        ("ipam", "0097_merge_ipaddress_host_index_and_multi_protocol_services"),
        ("extras", "0144_customfield_status"),
    ]
    operations = [
        migrations.CreateModel(
            name="ScanRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("target", models.CharField(max_length=255)),
                ("status", models.CharField(default="pending", max_length=20)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("hosts_found", models.PositiveIntegerField(default=0)),
                ("risky_hosts", models.PositiveIntegerField(default=0)),
                ("command_summary", models.JSONField(blank=True, default=dict)),
                ("error", models.TextField(blank=True)),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={"ordering": ("-started_at", "-created")},
        ),
        migrations.CreateModel(
            name="DiscoveredHost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("ip_address_text", models.GenericIPAddressField(protocol="both", unique=True, unpack_ipv4=True)),
                ("mac_address", models.CharField(blank=True, db_index=True, max_length=17)),
                ("hostname", models.CharField(blank=True, max_length=255)),
                ("vendor", models.CharField(blank=True, max_length=255)),
                ("device_type", models.CharField(blank=True, max_length=80)),
                ("os_guess", models.CharField(blank=True, max_length=255)),
                ("services", models.JSONField(blank=True, default=list)),
                ("first_seen", models.DateTimeField()),
                ("last_seen", models.DateTimeField(db_index=True)),
                ("status", models.CharField(default="new", max_length=20)),
                ("risk_score", models.PositiveSmallIntegerField(db_index=True, default=0)),
                ("risk_reasons", models.JSONField(blank=True, default=list)),
                ("recommendations", models.JSONField(blank=True, default=list)),
                ("device", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="discovered_hosts", to="dcim.device")),
                ("last_scan", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="hosts", to="netbox_netscan.scanrun")),
                ("netbox_ip", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="discovery_records", to="ipam.ipaddress")),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={"ordering": ("-risk_score", "ip_address_text")},
        ),
    ]
