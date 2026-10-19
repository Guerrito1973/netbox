import ipaddress
import subprocess

from .parser import parse_nmap_xml


class ScanError(RuntimeError):
    pass


class NmapScanner:
    def __init__(self, *, executable="nmap", timing="T3", host_timeout="90s", allow_public=False, minimum_prefix_length=24):
        self.executable = executable
        self.timing = timing
        self.host_timeout = host_timeout
        self.allow_public = allow_public
        self.minimum_prefix_length = int(minimum_prefix_length)

    def validate_target(self, target):
        network = ipaddress.ip_network(target, strict=True)
        if network.prefixlen < self.minimum_prefix_length:
            raise ScanError(f"Target {network} is too large; minimum prefix length is /{self.minimum_prefix_length}.")
        if not self.allow_public and not network.is_private:
            raise ScanError(f"Target {network} is not private and public scanning is disabled.")
        return str(network)

    def _run(self, args, timeout):
        command = [self.executable, *args, "-oX", "-"]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        except FileNotFoundError as exc:
            raise ScanError(f"nmap executable not found: {self.executable}") from exc
        except subprocess.TimeoutExpired as exc:
            raise ScanError("nmap exceeded the configured safety timeout") from exc
        if completed.returncode:
            raise ScanError(completed.stderr.strip() or f"nmap returned {completed.returncode}")
        return parse_nmap_xml(completed.stdout), command

    def scan(self, target, ports):
        target = self.validate_target(target)
        discovered, discovery_command = self._run(["-sn", "-n", target], timeout=600)
        addresses = [host["ip"] for host in discovered]
        if not addresses:
            return [], {"discovery": discovery_command, "services": None}
        service_args = [
            "-sV", "--version-light", f"-{self.timing}", "--max-retries", "2",
            "--host-timeout", self.host_timeout, "-n", "-p", ",".join(str(port) for port in ports), *addresses,
        ]
        detailed, service_command = self._run(service_args, timeout=max(600, len(addresses) * 100))
        details_by_ip = {host["ip"]: host for host in detailed}
        merged = []
        for host in discovered:
            detail = details_by_ip.get(host["ip"], {})
            merged.append({**host, **{key: value for key, value in detail.items() if value not in ("", [], None)}})
        return merged, {"discovery": discovery_command, "services": service_command}
