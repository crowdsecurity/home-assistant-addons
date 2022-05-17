# Home Assistant cs-firewall-bouncer Add-on

[CrowdSec](https://github.com/crowdsecurity/cs-firewall-bouncer) - Crowdsec bouncer written in golang for firewalls.

## Installation

Follow these steps to get the add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Supervisor** -> **Add-on Store**.
2. Click on the icon at the top right then **respositories** and add `https://github.com/crowdsecurity/home-assistant-addons`
3. Find the "Crowdsec Firewall Bouncer" add-on in Crowdsec add-ons repository and click it.
4. Click on the "INSTALL" button.

## How to use

!! This addon requires minimum Home assistant OS version >= 8.0.

As a classic [cs-firewall-bouncer](https://github.com/crowdsecurity/cs-firewall-bouncer), we need to generate a bouncer API key from crowdsec, get the crowdsec addon hostname and fill the addon configuration to communicate with crowdsec.

To generate a bouncer API key, we need to access to the [Crowdsec terminal](https://github.com/crowdsecurity/home-assistant-addons/blob/main/crowdsec/DOCS.md#crowdsec-terminal). Then type the command :

```bash
root@424ccef4-crowdsec:~# cscli bouncers add cs-firewall-bouncer
INFO[17-05-2022 03:23:36 PM] push and pull to Central API disabled        
Api key for 'cs-firewall-bouncer':

   a44bdb2ea50224f763015d04d2cd2e4b

Please keep this key since you will not be able to retrieve it!
```

Here is the bouncer API key you can copy and paste in your addon configuration.
In the same time, you can see in the terminal the crowdsec addon hostname you can retreive to specify the `api_url`.

## Add-on Configuration

```yaml
api_url: "http://424ccef4-crowdsec:8080/"
api_key: "a44bdb2ea50224f763015d04d2cd2e4b"
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