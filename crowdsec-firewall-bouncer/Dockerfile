ARG BUILD_FROM
FROM $BUILD_FROM

ARG BUILD_ARCH
ARG BIN_VERSION=v0.0.31

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y -q --install-recommends --no-install-suggests tzdata procps netbase iproute2 ipset curl iptables wget && \
    mkdir -p /var/run/crowdsec/ && \
    rm -rf /var/lib/apt/lists/*

RUN if [ "${BUILD_ARCH}" = "armhf" ]; then \
        wget -q -O /crowdsec-firewall-bouncer.tgz "https://github.com/crowdsecurity/cs-firewall-bouncer/releases/download/${BIN_VERSION}/crowdsec-firewall-bouncer-linux-armv7.tgz"; \
    elif [ "${BUILD_ARCH}" = "aarch64" ]; then \
        wget -q -O /crowdsec-firewall-bouncer.tgz "https://github.com/crowdsecurity/cs-firewall-bouncer/releases/download/${BIN_VERSION}/crowdsec-firewall-bouncer-linux-arm64.tgz"; \
    elif [ "${BUILD_ARCH}" = "i386" ]; then \
        wget -q -O /crowdsec-firewall-bouncer.tgz "https://github.com/crowdsecurity/cs-firewall-bouncer/releases/download/${BIN_VERSION}/crowdsec-firewall-bouncer-linux-386.tgz"; \
    else \
        wget -q -O /crowdsec-firewall-bouncer.tgz "https://github.com/crowdsecurity/cs-firewall-bouncer/releases/download/${BIN_VERSION}/crowdsec-firewall-bouncer-linux-${BUILD_ARCH}.tgz"; \
    fi

RUN tar xzvf /crowdsec-firewall-bouncer.tgz && rm /crowdsec-firewall-bouncer.tgz && mv /crowdsec-firewall-bouncer-$BIN_VERSION/crowdsec-firewall-bouncer /crowdsec-firewall-bouncer

# Copy root filesystem
COPY rootfs /
