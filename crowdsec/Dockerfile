ARG GOVERSION=1.17
ARG BUILD_FROM

FROM golang:${GOVERSION}-bullseye AS build

WORKDIR /go/src/crowdsec

# wizard.sh requires GNU coreutils
RUN apt-get update && apt-get install -y git jq gcc libc-dev make bash gettext binutils-gold coreutils tzdata python3 python3-pip
RUN git clone https://github.com/crowdsecurity/crowdsec.git --branch $(curl -s https://api.github.com/repos/crowdsecurity/crowdsec/releases/latest | jq -r '.tag_name') --single-branch /tmp/crowdsec
WORKDIR /tmp/crowdsec
RUN SYSTEM="docker" make release
RUN cd crowdsec-v* && ./wizard.sh --docker-mode && cd -
RUN cscli hub update && cscli collections install crowdsecurity/linux && cscli parsers install crowdsecurity/whitelists
RUN GO111MODULE=on go get github.com/mikefarah/yq/v4

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
    && mkdir -p /etc/crowdsec \
    && mkdir -p /var/lib/crowdsec
COPY --from=build /go/bin/yq /usr/bin/yq
COPY --from=build /etc/crowdsec /etc/crowdsec
COPY --from=build /var/lib/crowdsec /var/lib/crowdsec
COPY --from=build /usr/local/bin/crowdsec /usr/local/bin/crowdsec
COPY --from=build /usr/local/bin/cscli /usr/local/bin/cscli
COPY --from=build /tmp/crowdsec/docker/docker_start.sh /docker_start.sh
COPY --from=build /etc/crowdsec/config.yaml /etc/crowdsec/config.yaml
#Due to the wizard using cp -n, we have to copy the config files directly from the source as -n does not exist in busybox cp
#The files are here for reference, as users will need to mount a new version to be actually able to use notifications
#docker sucks
RUN true 
COPY --from=build /tmp/crowdsec/plugins/notifications/email/email.yaml /etc/crowdsec/notifications/email.yaml
COPY --from=build /tmp/crowdsec/plugins/notifications/http/http.yaml /etc/crowdsec/notifications/http.yaml
COPY --from=build /tmp/crowdsec/plugins/notifications/slack/slack.yaml /etc/crowdsec/notifications/slack.yaml
COPY --from=build /tmp/crowdsec/plugins/notifications/splunk/splunk.yaml /etc/crowdsec/notifications/splunk.yaml
# workaround to avoid having build issue ("failed to create image: failed to get layer")
RUN true
COPY --from=build /usr/local/lib/crowdsec/plugins /usr/local/lib/crowdsec/plugins

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD ["./run.sh"]
