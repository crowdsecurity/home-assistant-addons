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

### Crowdsec Web UI

The add-on ships a web UI (Home Assistant ingress) where you can:

- see an overview of active decisions, recent alerts, top scenarios and countries
- add and remove decisions (ban / captcha an IP or range)
- browse and delete alerts
- install, remove and upgrade hub items (collections, parsers, scenarios, …) and reload CrowdSec
- manage allowlists (IPs and ranges that are never banned, e.g. your own public IPv6 prefix)
- add and delete bouncers (the API key is shown once), and list machines
- view `cscli metrics`
- open a web terminal in the container (the **Terminal** tab) for anything else, using `cscli` ([bouncers management](https://docs.crowdsec.net/docs/next/user_guides/bouncers_configuration) for example)

Hub items listed in the add-on configuration are (re)installed on every start, so add permanent items there.

You can add the Crowdsec UI in sidebar :

1. Go to : http://homeassistant.local:8123/hassio/dashboard and click on Crowdsec addon.
2. Enable "Show in sidebar" option.

Or you can open it (on the addon info page), by clicking on "OPEN WEB UI" button.


## Add-on Configuration

The Crowdsec add-on has `journald` [option](https://developers.home-assistant.io/docs/add-ons/configuration#optional-configuration-options) activated to map host system journal to process all the logs (even others add-ons logs).
With that, you can even parse and detect behaviors on Nginx Proxy Manager or Nginx addons for example.

This add-on has also persistent config and data files that are store at `/config/.storage/crowdsec/`.

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
parsers: []
scenarios: []
postoverflows: []
parsers_to_disable:
  - crowdsecurity/whitelists
scenarios_to_disable: []
disable_online_api: false
```

### Option: `acquisition` (required)

Acquisition config file for crowdsec ([see documentation](https://docs.crowdsec.net/docs/next/concepts/#acquisition)).
The default acquisition allow Crowdsec add-on to process all logs from the host system journal.

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

## Support

Got questions?

You have several options to get them answered:

- The [Crowdsec Discord Chat Server][discord].
- The Home Assistant [Community Forum][forum].

In case you've found a bug, please [open an issue on our GitHub][issue].

[discord]: https://discord.gg/wGN7ShmEE8
[forum]: https://discourse.crowdsec.net/
[issue]: https://github.com/crowdsecurity/home-assistant-addons/issues