RISKY_PORTS = {
    21: (25, "FTP is exposed and may transmit credentials without encryption.", "Disable FTP or replace it with SFTP."),
    23: (40, "Telnet is exposed and transmits sessions without encryption.", "Disable Telnet and use SSH."),
    139: (15, "Legacy NetBIOS file sharing is exposed.", "Restrict NetBIOS to trusted hosts or disable it."),
    445: (20, "SMB is reachable from the scanned network.", "Restrict SMB with host firewall/VLAN rules and require SMBv3."),
    3389: (20, "Remote Desktop is reachable from the scanned network.", "Put RDP behind VPN/MFA and restrict its source addresses."),
    5900: (25, "VNC is reachable from the scanned network.", "Restrict VNC to a management VLAN or VPN and enforce encryption."),
    1883: (20, "Unencrypted MQTT is exposed.", "Require authenticated MQTT over TLS (port 8883)."),
    9100: (10, "Raw printer service is reachable.", "Restrict port 9100 to print servers and trusted clients."),
}


def classify_device(host):
    names = " ".join([host.get("hostname", ""), host.get("vendor", ""), host.get("os", "")]).lower()
    ports = {service["port"] for service in host.get("services", [])}
    if 9100 in ports or "printer" in names:
        return "printer"
    if 554 in ports or "camera" in names:
        return "camera"
    if 445 in ports and any(token in names for token in ("synology", "qnap", "nas")):
        return "storage"
    if any(token in names for token in ("router", "openwrt", "mikrotik", "ubiquiti")):
        return "network"
    if 80 in ports or 443 in ports or 8080 in ports or 8443 in ports:
        return "server-or-iot"
    return "unknown"


def assess_risk(host, *, known_in_netbox=False, previous_mac=""):
    score, reasons, recommendations = 0, [], []
    if not known_in_netbox:
        score += 25
        reasons.append("The IP address is not registered in NetBox.")
        recommendations.append("Identify the owner and register or quarantine this device.")

    mac = host.get("mac", "").upper()
    if mac and int(mac.split(":")[0], 16) & 2:
        score += 10
        reasons.append("The MAC address is locally administered or randomized.")
        recommendations.append("Confirm whether MAC randomization is expected for this device.")

    if previous_mac and mac and previous_mac.upper() != mac:
        score += 35
        reasons.append(f"The MAC address changed from {previous_mac} to {mac}.")
        recommendations.append("Check DHCP/ARP records and rule out address spoofing or an undocumented replacement.")

    for service in host.get("services", []):
        rule = RISKY_PORTS.get(service.get("port"))
        if rule:
            points, reason, recommendation = rule
            score += points
            reasons.append(reason)
            recommendations.append(recommendation)

    if not host.get("vendor") and mac:
        score += 5
        reasons.append("The MAC vendor could not be identified.")
        recommendations.append("Verify the manufacturer and update the asset inventory.")

    return min(score, 100), list(dict.fromkeys(reasons)), list(dict.fromkeys(recommendations))

