# Home Assistant cs-firewall-bouncer Add-on

[CrowdSec](https://github.com/crowdsecurity/cs-firewall-bouncer) - Crowdsec bouncer written in golang for firewalls.

## Installation

Follow these steps to get the add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Supervisor** -> **Add-on Store**.
2. Click on the icon at the top right then **respositories** and add `https://github.com/crowdsecurity/home-assistant-addons`
3. Find the "Crowdsec Firewall Bouncer" add-on in Crowdsec add-ons repository and click it.
4. Click on the "INSTALL" button.

## How to use

:warning: This addon requires minimum Home assistant OS version >= 8.0.

As a classic [cs-firewall-bouncer](https://github.com/crowdsecurity/cs-firewall-bouncer), we need to generate a bouncer API key from crowdsec and fill the addon configuration to communicate with crowdsec.

## Add-on Configuration

```yaml
api_url: ""
api_key: ""
update_frequency: "10s"
log_level: info
```

### Option: `api_url` (required)

Set local API url.

### Option: `api_key` (optional)

Set local API key.

### Option: `update_frequency` (optional)

Controls how often the bouncer is going to query the local API.

### Option: `log_level` (optional)

Controls logging level.

## Support

Got questions?

You have several options to get them answered:

- The [Crowdsec Discord Chat Server][discord].
- The Home Assistant [Community Forum][forum].

In case you've found a bug, please [open an issue on our GitHub][issue].

[discord]: https://discord.gg/wGN7ShmEE8
[forum]: https://discourse.crowdsec.net/
[issue]: https://github.com/crowdsecurity/home-assistant-addons/issues