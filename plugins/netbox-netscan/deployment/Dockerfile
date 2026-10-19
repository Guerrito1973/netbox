ARG NETBOX_IMAGE=netboxcommunity/netbox:v4.7.3
FROM ${NETBOX_IMAGE}

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends nmap \
    && rm -rf /var/lib/apt/lists/*

COPY . /tmp/netbox-netscan
RUN /usr/local/bin/uv pip install /tmp/netbox-netscan \
    && rm -rf /tmp/netbox-netscan

USER netbox
