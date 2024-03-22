ARG BUILD_FROM
FROM $BUILD_FROM

ARG BUILD_ARCH

RUN apt-get update
RUN apt-get install -y -q --install-recommends --no-install-suggests \
    procps \
    systemd \
    ca-certificates \
    bash \
    tzdata \
    wget \
    tmux \
    vim \
    nano \
    && if [ "${BUILD_ARCH}" = "armhf" ] || [ "${BUILD_ARCH}" = "armv7" ]; then \
        wget -q -O /usr/bin/yq "https://github.com/mikefarah/yq/releases/download/v4.20.1/yq_linux_arm"; \
    elif [ "${BUILD_ARCH}" = "aarch64" ]; then \
        wget -q -O /usr/bin/yq "https://github.com/mikefarah/yq/releases/download/v4.20.1/yq_linux_arm64"; \
    elif [ "${BUILD_ARCH}" = "i386" ]; then \
        wget -q -O /usr/bin/yq "https://github.com/mikefarah/yq/releases/download/v4.20.1/yq_linux_386"; \
    elif [ "${BUILD_ARCH}" = "amd64" ]; then \
        wget -q -O /usr/bin/yq "https://github.com/mikefarah/yq/releases/download/v4.20.1/yq_linux_amd64"; \
    else \
        exit 1; \
    fi \
    && if [ "${BUILD_ARCH}" = "armhf" ]; then \
        wget -q -O /usr/bin/ttyd "https://github.com/tsl0922/ttyd/releases/download/1.6.3/ttyd.armhf"; \
    elif [ "${BUILD_ARCH}" = "armv7" ]; then \
        wget -q -O /usr/bin/ttyd "https://github.com/tsl0922/ttyd/releases/download/1.6.3/ttyd.arm"; \
    elif [ "${BUILD_ARCH}" = "aarch64" ]; then \
        wget -q -O /usr/bin/ttyd "https://github.com/tsl0922/ttyd/releases/download/1.6.3/ttyd.aarch64"; \
    elif [ "${BUILD_ARCH}" = "i386" ] || [ "${BUILD_ARCH}" = "amd64" ]; then \
        wget -q -O /usr/bin/ttyd "https://github.com/tsl0922/ttyd/releases/download/1.6.3/ttyd.x86_64"; \
    else \
        exit 1; \
    fi \
    && chmod +x /usr/bin/yq \
    && chmod +x /usr/bin/ttyd \
    && mkdir -p /etc/crowdsec \
    && mkdir -p /var/lib/crowdsec
RUN echo "deb http://deb.debian.org/debian bullseye-backports main" >> /etc/apt/sources.list \
    && apt-get update && apt-get install -t bullseye-backports -y libsystemd0
#Add alias until env variables will be supported by crowdsec.
RUN echo 'alias cscli="cscli -c /config/.storage/crowdsec/config/config.yaml"' > /root/.bashrc

COPY --from=crowdsecurity/crowdsec:v1.6.0-1 /staging/etc/crowdsec /etc/crowdsec
COPY --from=crowdsecurity/crowdsec:v1.6.0-1 /staging/var/lib/crowdsec /var/lib/crowdsec
COPY --from=crowdsecurity/crowdsec:v1.6.0-1 /usr/local/bin/crowdsec /usr/local/bin/crowdsec
COPY --from=crowdsecurity/crowdsec:v1.6.0-1 /usr/local/bin/cscli /usr/local/bin/cscli
COPY --from=crowdsecurity/crowdsec:v1.6.0-1 /docker_start.sh /docker_start.sh
COPY --from=crowdsecurity/crowdsec:v1.6.0-1 /staging/etc/crowdsec/config.yaml /etc/crowdsec/config.yaml
#Due to the wizard using cp -n, we have to copy the config files directly from the source as -n does not exist in busybox cp
#The files are here for reference, as users will need to mount a new version to be actually able to use notifications
COPY --from=crowdsecurity/crowdsec:v1.6.0-1 /staging/etc/crowdsec/notifications/email.yaml /etc/crowdsec/notifications/email.yaml
COPY --from=crowdsecurity/crowdsec:v1.6.0-1 /staging/etc/crowdsec/notifications/http.yaml /etc/crowdsec/notifications/http.yaml
COPY --from=crowdsecurity/crowdsec:v1.6.0-1 /staging/etc/crowdsec/notifications/slack.yaml /etc/crowdsec/notifications/slack.yaml
COPY --from=crowdsecurity/crowdsec:v1.6.0-1 /staging/etc/crowdsec/notifications/splunk.yaml /etc/crowdsec/notifications/splunk.yaml
# workaround to avoid having build issue ("failed to create image: failed to get layer")
RUN true
COPY --from=crowdsecurity/crowdsec:v1.6.0-1 /usr/local/lib/crowdsec/plugins /usr/local/lib/crowdsec/plugins

# Copy root filesystem
COPY rootfs /
