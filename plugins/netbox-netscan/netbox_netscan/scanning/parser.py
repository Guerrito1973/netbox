import xml.etree.ElementTree as ET


def parse_nmap_xml(xml_text):
    """Turn nmap XML into small, serializable host dictionaries."""
    root = ET.fromstring(xml_text)
    hosts = []
    for node in root.findall("host"):
        state = node.find("status")
        if state is None or state.get("state") != "up":
            continue
        addresses = {item.get("addrtype"): item for item in node.findall("address")}
        ip_node = addresses.get("ipv4")
        if ip_node is None:
            ip_node = addresses.get("ipv6")
        if ip_node is None:
            continue
        mac_node = addresses.get("mac")
        hostname_node = node.find("hostnames/hostname")
        os_node = node.find("os/osmatch")
        services = []
        for port in node.findall("ports/port"):
            port_state = port.find("state")
            if port_state is None or port_state.get("state") != "open":
                continue
            service = port.find("service")
            services.append({
                "port": int(port.get("portid")),
                "protocol": port.get("protocol", "tcp"),
                "name": service.get("name", "unknown") if service is not None else "unknown",
                "product": service.get("product", "") if service is not None else "",
                "version": service.get("version", "") if service is not None else "",
            })
        hosts.append({
            "ip": ip_node.get("addr"),
            "mac": mac_node.get("addr", "").upper() if mac_node is not None else "",
            "vendor": mac_node.get("vendor", "") if mac_node is not None else "",
            "hostname": hostname_node.get("name", "") if hostname_node is not None else "",
            "os": os_node.get("name", "") if os_node is not None else "",
            "services": services,
        })
    return hosts
