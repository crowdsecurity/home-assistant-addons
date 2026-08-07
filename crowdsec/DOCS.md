# Home Assistant Crowdsec Add-on

[CrowdSec](https://github.com/crowdsecurity/crowdsec) - the open-source and participative IPS able to analyze visitor behavior & provide an adapted response to all kinds of attacks. It also leverages the crowd power to generate a global CTI database to protect the user network.

## Installation

Follow these steps to get the add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Settings** ->  **Add-ons** -> **ADD-ON STORE**.
2. Click on the icon at the top right then **respositories** and add `https://github.com/crowdsecurity/home-assistant-addons`
3. Find the "Crowdsec" add-on in Crowdsec add-ons repository and click it.
4. Click on the "INSTALL" button.

## How to use

The add-on is configured by default to parse and detect bruteforce on home-assistant login interface.

### Crowdsec Terminal

Crowdsec addon expose a web terminal to access the container where Crowdsec is running.
So you can interact with Crowdsec ([bouncers management](https://docs.crowdsec.net/docs/next/user_guides/bouncers_configuration) for example).

You can add the Crowdsec terminal in sidebar :

1. Go to : http://homeassistant.local:8123/hassio/dashboard and click on Crowdsec addon.
2. Enable "Show in sidebar" option.

Or you can open the crowdsec terminal (on the addon info page), by clicking on "OPEN WEB UI" button.


## Add-on Configuration

The Crowdsec add-on has `journald` [option](https://developers.home-assistant.io/docs/add-ons/configuration#optional-configuration-options) activated to map host system journal to process all the logs (even others add-ons logs).
With that, you can even parse and detect behaviors on Nginx Proxy Manager or Nginx addons for example.

This add-on has also persistent config and data files that are store at `/config/.storage/crowdsec/`.

> **Editing multi-line options (`acquisition`, `whitelists`):** use the add-on's **Configuration**
> tab with the pencil/code icon toggled to **Edit in YAML**, not the auto-generated form. Pasting
> multi-line YAML into the plain text-input widget of the visual form silently strips every
> newline (browsers do this on paste into single-line `<input>` fields), collapsing your whole
> value onto one line and producing a `crowdsec init: while loading acquisition config: ...
> invalid header option` fatal error on start. The raw YAML editor preserves newlines correctly.
> After saving, you can double check by opening the CrowdSec terminal and running
> `cat /config/.storage/crowdsec/config/acquis.yaml` — it should come back multi-line.

```yaml
acquisition: |
  ---
  source: journalctl
  journalctl_filter: 
    - "--directory=/var/log/journal/"
  labels:
    type: syslog
disable_lapi: false
remote_lapi_url: ""
agent_username: ""
agent_password: ""
collections:
  - crowdsecurity/home-assistant
  - crowdsecurity/nginx-proxy-manager
  - crowdsecurity/nginx
  - crowdsecurity/sshd
parsers: []
scenarios: []
postoverflows: []
parsers_to_disable: []
scenarios_to_disable: []
disable_online_api: false
whitelists: ""
```

### Option: `acquisition` (required)

Acquisition config file for crowdsec ([see documentation](https://docs.crowdsec.net/docs/next/concepts/#acquisition)).
The default acquisition allow Crowdsec add-on to process all logs from the host system journal.

#### Detecting attacks against other add-ons (Nginx Proxy Manager, Nginx, SSH, ...)

Home Assistant OS tags every supervised add-on's journald log lines with an identifier like
`app_<install-hash>_<addon-name>` (store add-ons) or `app_core_<addon-name>` (system add-ons) —
for example `app_a0d7b954_nginxproxymanager` or `app_core_ssh`. Upstream CrowdSec Hub parsers
normally expect the plain program name instead (e.g. `nginx-proxy-manager`, `sshd`), so without
any extra help they silently never match these HAOS-wrapped identifiers, even once the right
collection is installed.

To fix this, the add-on ships a small local parser
(`crowdsec-addons/haos-program-normalize`, regenerated on every start) that rewrites the
identifier for a few well-known add-ons before the real Hub parsers see it:

| HAOS add-on identifier suffix | Rewritten to | Detected by (installed by default) |
| --- | --- | --- |
| `..._nginxproxymanager` | `nginx-proxy-manager` | `crowdsecurity/nginx-proxy-manager` |
| `..._nginx` | `nginx` | `crowdsecurity/nginx` |
| `..._ssh` | `sshd` | `crowdsecurity/sshd` |

Home Assistant Core itself doesn't need this — its journald identifier is already the plain
`homeassistant`, which `crowdsecurity/home-assistant` (also installed by default) matches directly.

If you run an add-on that isn't in the table above and want CrowdSec to detect attacks against
it, you generally need two things: (1) install the matching collection from the
[CrowdSec Hub](https://app.crowdsec.net/hub) via the `collections` option below, and (2) if that
collection's parser filters on `evt.Parsed.program` (most do — check the parser's `filter:` on
the Hub), extend the bundled normalizer, since the add-on doesn't currently expose this as its
own option. The file the add-on generates lives at
`/config/.storage/crowdsec/config/parsers/s01-parse/crowdsec-addons/haos-program-normalize.yaml`
if you want to inspect it — note that, like `acquis.yaml`, it's rebuilt from scratch on every
addon start, so it's not a place to make persistent manual edits.

Mosquitto/MQTT (`core_mosquitto`), MariaDB, Let's Encrypt, NetBird, Uptime Kuma, ESPHome, NUT,
Z-Wave JS UI, TasmoAdmin, and InfluxDB currently have no CrowdSec Hub parser at all, so there's
nothing to wire up for them today regardless of identifier normalization.

#### Reducing noise / confining acquisition (optional)

By default the add-on reads the *entire* host journal — including plenty of add-ons CrowdSec has
no parser for (Mosquitto, MariaDB, NetBird, Uptime Kuma, ESPHome, InfluxDB, ...) and Home
Assistant's own automation-trace logging. That's safe, but it does mean CrowdSec spends effort
scanning lines it can never do anything with. If you'd rather it only look at programs it can
actually detect attacks for, paste an allowlist `filter:` into this option, e.g.:

```yaml
acquisition: |
  ---
  source: journalctl
  journalctl_filter:
    - "--directory=/var/log/journal/"
  labels:
    type: syslog
  # Allowlist: only feed lines from programs we have a CrowdSec parser for
  # into the pipeline. Extend this list whenever you install a new collection
  # whose add-on isn't covered yet, e.g. add `evt.Parsed.program endsWith '_apache2'`
  # after installing crowdsecurity/apache2 for an Apache add-on.
  filter: >-
    evt.Parsed.program endsWith 'nginxproxymanager' or
    evt.Parsed.program endsWith '_nginx' or
    evt.Parsed.program endsWith '_ssh' or
    evt.Parsed.program in ['homeassistant', 'hass']
```

This is an **allowlist**: anything that doesn't match one of these clauses (Mosquitto, MariaDB,
NetBird, Uptime Kuma, ESPHome, NUT, Z-Wave JS UI, TasmoAdmin, Puppet, InfluxDB, Let's Encrypt,
CrowdSec's own logs, ...) is dropped before it ever enters the parsing pipeline. That means
**you must extend this filter yourself** whenever you install a `collections` entry for a new
add-on — otherwise that add-on's logs will be silently dropped at acquisition time instead of
reaching the new collection's parser. Edit it via the add-on's **Configuration** tab, not by
hand-editing files inside the container: only the `acquisition` *option* is persisted by
Supervisor across restarts, while the generated `acquis.yaml` file is always rebuilt from it on
every start.

If you only care about a couple of specific add-ons and want the most efficient setup, an
alternative is one `journalctl` source per add-on using journald's own filtering instead of a
post-read expression:

```yaml
acquisition: |
  ---
  source: journalctl
  journalctl_filter:
    - "--directory=/var/log/journal/"
    - "--identifier=app_a0d7b954_nginxproxymanager"
  labels:
    type: syslog
  ---
  source: journalctl
  journalctl_filter:
    - "--directory=/var/log/journal/"
    - "--identifier=app_core_ssh"
  labels:
    type: syslog
```

`--directory=/var/log/journal/` **must** stay in every source's `journalctl_filter` list alongside
`--identifier=...` — it's what points `journalctl` at the bind-mounted host journal (from this
add-on's `journald: true` option) in the first place. Drop it and `journalctl` silently reads the
container's own near-empty local journal instead, giving zero lines with no error (you'll see an
empty `cscli metrics show acquisition` table, no row at all, rather than a row with a nonzero
"Lines read").

This lets journald itself do the filtering (no re-scanning the whole journal per source), at the
cost of needing to know each add-on's exact `SYSLOG_IDENTIFIER`, which includes an
installation-specific hash for store add-ons and isn't wildcard-matchable. Find yours from the
CrowdSec terminal with:

```shell
journalctl -o json | jq -r '.SYSLOG_IDENTIFIER' | sort -u
```

### Option: `disable_lapi` (optional)

Disable local API (if you want only the agent).

### Option: `remote_lapi_url` (optional)

When `disable_lapi` is set to `true`, you need to specify the remote local API URL.

### Option: `agent_username` (optional)

When `disable_lapi` is set to `true`, you need to specify the agent username to connect to the remote local API.

### Option: `agent_password` (optional)

When `disable_lapi` is set to `true`, you need to specify the agent password to connect to the remote local API.

### Option: `collections` (optional)

All the [collections](https://docs.crowdsec.net/docs/next/user_guides/hub_mgmt/#collections) you want to install before running crowdsec.

### Option: `parsers` (optional)

All the [parsers](https://docs.crowdsec.net/docs/next/user_guides/hub_mgmt/#parsers) you want to install before running crowdsec.

### Option: `scenarios` (optional)

All the [scenarios](https://docs.crowdsec.net/docs/next/user_guides/hub_mgmt/#scenarios) you want to install before running crowdsec.

### Option: `postoverflows` (optional)

All the [postoverflows](https://docs.crowdsec.net/docs/next/parsers/intro/#postoverflows) you want to install before running crowdsec.

### Option: `parsers_to_disable` (optional)

All the parsers you want to remove before running crowdsec.

### Option: `scenarios_to_disable` (optional)

All the scenarios you want to remove before running crowdsec.

### Option: `disable_online_api` (optional)

Disable Online API registration for signal sharing.

### Option: `whitelists` (optional)

CrowdSec already whitelists RFC1918 private ranges and loopback (`127.0.0.0/8`, `::1`,
`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) out of the box via the `crowdsecurity/whitelists`
parser bundled in the base CrowdSec image — you don't need to do anything for your own LAN
traffic to be excluded from bans.

This option lets you layer your *own* extra trusted sources on top of that baseline — for
example a known-static remote admin IP, a VPN/NetBird peer range that falls outside RFC1918, or
an internal health-check endpoint you don't want triggering scenarios. It's a raw CrowdSec
[whitelist parser](https://docs.crowdsec.net/docs/next/log_processor/whitelist/intro/) definition,
written verbatim to a local parser file and regenerated on every add-on start (same mechanism as
`acquisition`) — leave it empty (the default) for no change in behavior. Example:

```yaml
whitelists: |
  ---
  name: crowdsec-addons/user-whitelists
  description: "Extra trusted sources on top of CrowdSec's built-in RFC1918/loopback whitelist"
  whitelist:
    reason: "trusted sources"
    ip:
      - "203.0.113.42"        # e.g. a known-static remote admin IP
    cidr:
      - "100.64.0.0/10"       # e.g. a VPN/NetBird peer range
    expression:
      - "evt.Meta.http_path == '/health'"   # e.g. an internal health-check endpoint
```

As with `acquisition`, edit this via the add-on's **Configuration** tab rather than hand-editing
files inside the container — the generated file at
`/config/.storage/crowdsec/config/parsers/s02-enrich/crowdsec-addons/user-whitelists.yaml` is
rebuilt (or removed, if you clear the option) from this option on every start.

## Support

Got questions?

You have several options to get them answered:

- The [Crowdsec Discord Chat Server][discord].
- The Home Assistant [Community Forum][forum].

In case you've found a bug, please [open an issue on our GitHub][issue].

[discord]: https://discord.gg/wGN7ShmEE8
[forum]: https://discourse.crowdsec.net/
[issue]: https://github.com/crowdsecurity/home-assistant-addons/issues