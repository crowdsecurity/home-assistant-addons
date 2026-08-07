# Changelog

## 1.7.8-1

- Fix detection for add-ons behind Home Assistant OS's `app_<hash>_<name>`/`app_core_<name>` journald identifier wrapping (Nginx Proxy Manager, Nginx, SSH), which previously caused their logs to silently never match upstream CrowdSec Hub parsers even with the right collection installed. Adds a bundled local normalizer parser and installs `crowdsecurity/nginx-proxy-manager`, `crowdsecurity/nginx` and `crowdsecurity/sshd` by default alongside the existing `crowdsecurity/home-assistant`.
- Document an optional acquisition allowlist `filter:` recipe and per-add-on `journalctl_filter` alternative to reduce log volume/noise for add-ons CrowdSec has no parser for (Mosquitto/MQTT, MariaDB, NetBird, Uptime Kuma, ESPHome, NUT, Z-Wave JS UI, TasmoAdmin, Puppet, InfluxDB).
- Add optional `whitelists` option to layer custom trusted IPs/CIDRs/expressions on top of CrowdSec's built-in RFC1918/loopback whitelist.

## 1.7.8

- Bump crowdsec version to 1.7.8

## 1.7.7

- Bump crowdsec version to 1.7.7

## 1.7.6

- Bump crowdsec version to 1.7.6

## 1.7.4

- Bump crowdsec version to 1.7.4

## 1.7.2

- Bump crowdsec version to 1.7.2

## 1.7.0

- Bump crowdsec version to 1.7.0

## 1.6.11

- Bump crowdsec version to 1.6.11

## 1.6.10

- Bump crowdsec version to 1.6.10

## 1.6.9

- Bump crowdsec version to 1.6.9

## 1.6.8

- Bump crowdsec version to 1.6.8

## 1.6.6

- Bump crowdsec version to 1.6.6

## 1.6.5-1

- Workaround a potential start failure when running with LAPI

## 1.6.5

- Bump crowdsec version to 1.6.5

## 1.6.4

- Bump crowdsec version to 1.6.4

## 1.6.3

- Bump crowdsec version to 1.6.3

## 1.6.2

- Bump crowdsec version to 1.6.2

## 1.6.1-2

- Bump crowdsec version to 1.6.1-2

## 1.6.0-1

- Bump crowdsec version to 1.6.0-1
