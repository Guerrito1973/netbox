# NetBox Network Scanner

Plugin for NetBox 4.7 that discovers hosts with `nmap`, records when they were
last seen, correlates them with NetBox IPAM/DCIM, explains security risk, and
draws a lightweight network map.

## What is included

- Two-stage scans: host discovery (`-sn`) followed by limited service detection.
- Strict guardrails: private targets only, `/24` maximum by default, no shell
  invocation, `T3`, bounded retries and per-host timeout.
- `first_seen`, `last_seen`, MAC/vendor, hostname, OS guess, selected services,
  estimated device type, and optional links to `ipam.IPAddress` and `dcim.Device`.
- Explainable risk score and concrete recommendations for unknown assets, MAC
  changes, randomized MACs, Telnet, FTP, SMB, RDP, VNC, MQTT, and raw printing.
- Manual background scans, optional hourly scans, REST read API, scan history,
  and a dependency-free SVG map.

This is discovery and prioritization, not a vulnerability scanner. A service
banner is not proof that a vulnerability exists.

## Docker installation

The supplied image extends `netboxcommunity/netbox:v4.7.3`, installs `nmap`,
and installs this plugin:

```bash
docker build -f deployment/Dockerfile -t local/netbox-netscan:4.7.3 .
```

Merge `deployment/configuration.py.example` into the NetBox configuration,
use the custom image for both `netbox` and `netbox-worker`, and then run:

```bash
docker compose run --rm netbox ./manage.py migrate
docker compose up -d
```

The worker performs the scans. Grant `NET_RAW` and `NET_ADMIN` to that service.
Docker bridge networking can discover reachable IPs and ports, but normally
cannot see Ethernet MAC addresses on the physical LAN. For MAC/OUI discovery,
run a dedicated worker with host networking on Linux. When doing so, PostgreSQL
and Redis must also be reachable from the host-networked worker (container DNS
names such as `postgres` will not resolve there).

Do not run the whole web application privileged. Do not expose the NetBox web
port merely to make scanning work.

## Deployment from GitHub

The repository includes `.github/workflows/netbox-netscan.yml`. On each push to
`main` that changes this plugin it runs the unit tests, builds the wheel, builds
the custom NetBox image, and publishes it as:

```text
ghcr.io/guerrito1973/netbox-netscan:main
```

A Git tag such as `v0.1.0` also publishes immutable `0.1.0` and `0.1` image
tags. Production should use a version tag instead of `main` so that rollback is
just a deployment of the previous version.

On a new Ubuntu host, install Docker Engine plus the Compose plugin, clone this
fork, and run:

```bash
sudo mkdir -p /opt/netbox-source
sudo chown "$USER:$USER" /opt/netbox-source
git clone https://github.com/Guerrito1973/netbox.git /opt/netbox-source

bash /opt/netbox-source/plugins/netbox-netscan/deployment/bootstrap-ubuntu.sh
```

Review `/opt/netbox-docker/configuration/netscan.py`,
`/opt/netbox-docker/netscan.env`, and the standard NetBox Docker environment
files. Then deploy:

```bash
bash /opt/netbox-source/plugins/netbox-netscan/deployment/deploy.sh
```

To deploy a published release or roll back to it:

```bash
bash /opt/netbox-source/plugins/netbox-netscan/deployment/update.sh 0.1.0
```

The scripts validate Compose, pull the requested image, start its dependencies,
apply migrations, and only then recreate the services. If the GHCR package is
private, authenticate the Ubuntu host first with a GitHub token holding only
`read:packages`:

```bash
docker login ghcr.io --username Guerrito1973
```

Do not store the token in Git, Compose YAML, or the plugin configuration.

## First rollout

1. Configure only `192.168.100.0/24` and leave `scheduled_scans` false.
2. Start the default RQ worker and grant the user `view_discoveredhost`,
   `view_scanrun`, and `add_scanrun` permissions.
3. Open **Plugins → Network Scanner**, queue a scan, and review its Job log.
4. Confirm expected hosts and tune `scan_ports` before enabling schedules.
5. Add `192.168.1.0/24` and `192.168.5.0/24` one at a time.

Only scan networks for which you have explicit authorization. Avoid service
detection on fragile printers, medical devices, PLCs, or other operational
technology until the owner approves a maintenance window.

## API

- `/api/plugins/netscan/hosts/`
- `/api/plugins/netscan/runs/`

Both endpoints are read-only and use NetBox object permissions.

## Suggested next improvements

1. Create a separate sensor/worker in each routed site and report observations
   centrally; this improves reachability and preserves local MAC visibility.
2. Add LLDP/SNMP polling with read-only credentials stored outside the database
   to learn switch ports and real L2 links. The current map is inventory-based.
3. Track observations in a time-series table so appearance/disappearance and
   DHCP churn can be analyzed without overwriting the latest state.
4. Add allowlists per VLAN and maintenance windows to reduce false positives.
5. Add notifications through NetBox event rules only after risk thresholds have
   been tuned; otherwise alert fatigue arrives quickly.
6. Add authenticated CVE enrichment from a maintained feed. Do not infer CVEs
   from banner text alone.

## Development checks

Inside a NetBox 4.7 development environment:

```bash
pip install -e plugins/netbox-netscan
python netbox/manage.py makemigrations --check netbox_netscan
python netbox/manage.py check
python -m unittest discover plugins/netbox-netscan/tests
```
