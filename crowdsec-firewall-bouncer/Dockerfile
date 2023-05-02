ARG BUILD_FROM
FROM $BUILD_FROM

ARG BUILD_ARCH
ARG BIN_VERSION=v0.0.26

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y -q --install-recommends --no-install-suggests tzdata procps netbase iproute2 ipset curl iptables && \
    mkdir -p /var/run/crowdsec/ && \
    rm -rf /var/lib/apt/lists/*

ADD https://github.com/crowdsecurity/cs-firewall-bouncer/releases/download/$BIN_VERSION/crowdsec-firewall-bouncer-linux-$BUILD_ARCH.tgz /crowdsec-firewall-bouncer.tgz
RUN tar xzvf /crowdsec-firewall-bouncer.tgz && rm /crowdsec-firewall-bouncer.tgz && mv /crowdsec-firewall-bouncer-$BIN_VERSION/crowdsec-firewall-bouncer /crowdsec-firewall-bouncer

# Copy root filesystem
COPY rootfs /
