ARG BUILD_FROM
FROM $BUILD_FROM

RUN apt-get update
RUN apt-get install -y -q --install-recommends --no-install-suggests \
    procps \
    systemd \
    ca-certificates \
    bash \
    tzdata && \
  mkdir -p /etc/crowdsec && \
  mkdir -p /var/lib/crowdsec

COPY --from=hessahely/crowdsec:debian /usr/local/bin/yq /usr/local/bin/yq
COPY --from=hessahely/crowdsec:debian /staging/etc/crowdsec /etc/crowdsec
COPY --from=hessahely/crowdsec:debian /staging/var/lib/crowdsec /var/lib/crowdsec
COPY --from=hessahely/crowdsec:debian /usr/local/bin/crowdsec /usr/local/bin/crowdsec
COPY --from=hessahely/crowdsec:debian /usr/local/bin/cscli /usr/local/bin/cscli
COPY --from=hessahely/crowdsec:debian /docker_start.sh /docker_start.sh
COPY --from=hessahely/crowdsec:debian /staging/etc/crowdsec/config.yaml /etc/crowdsec/config.yaml
#Due to the wizard using cp -n, we have to copy the config files directly from the source as -n does not exist in busybox cp
#The files are here for reference, as users will need to mount a new version to be actually able to use notifications
COPY --from=hessahely/crowdsec:debian /staging/etc/crowdsec/notifications/http.yaml /etc/crowdsec/notifications/http.yaml
COPY --from=hessahely/crowdsec:debian /staging/etc/crowdsec/notifications/slack.yaml /etc/crowdsec/notifications/slack.yaml
COPY --from=hessahely/crowdsec:debian /staging/etc/crowdsec/notifications/splunk.yaml /etc/crowdsec/notifications/splunk.yaml
# workaround to avoid having build issue ("failed to create image: failed to get layer")
RUN true
COPY --from=hessahely/crowdsec:debian /usr/local/lib/crowdsec/plugins /usr/local/lib/crowdsec/plugins

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD ["./run.sh"]
#ENTRYPOINT /bin/sh /run.sh