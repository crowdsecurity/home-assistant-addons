# Home Assistant cs-firewall-bouncer Add-on

[CrowdSec](https://github.com/crowdsecurity/cs-firewall-bouncer) - CrowdSec bouncer written in golang for firewalls.

## Installation

Follow these steps to get the add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Supervisor** -> **Add-on Store**.
2. Click on the icon at the top right then **Respositories** and add `https://github.com/crowdsecurity/home-assistant-addons`
3. Find the "CrowdSec Firewall Bouncer" add-on in CrowdSec add-ons repository and click it.
4. Click on the "INSTALL" button.

## How to use

!! This addon requires minimum Home Assistant OS version >= 8.0.

As a classic [cs-firewall-bouncer](https://github.com/crowdsecurity/cs-firewall-bouncer), we need to generate a bouncer API key from CrowdSec, get the CrowdSec addon hostname and fill the addon configuration to communicate with CrowdSec.

To generate an bouncer API key, we need to access to the [CrowdSec Terminal](https://github.com/crowdsecurity/home-assistant-addons/blob/main/crowdsec/DOCS.md#crowdsec-terminal). Then type the command:

```bash
root@424ccef4-crowdsec:~# cscli bouncers add cs-firewall-bouncer
INFO[17-05-2022 03:23:36 PM] push and pull to Central API disabled
Api key for 'cs-firewall-bouncer':

   a44bdb2ea50224f763015d04d2cd2e4b

Please keep this key since you will not be able to retrieve it!
```

The API Key and API URL need to be shared from the CrowdSec add-on to the Bouncer add-on. These details can be added through the Home Assistant UI `Settings > Add-Ons > CrowdSec Firewall Bouncer > Configuration`, or by editing `/config/.storage/crowdsec/config/local_api_configuration.yaml` directly.

The API URL should be input as: `http://<crowdsec-terminal-hostname>:8080/`

## Add-on Configuration

For the terminal output provided above, `local_api_configuration.yaml` should appear as:

```yaml
api_url: "http://424ccef4-crowdsec:8080/"
api_key: "a44bdb2ea50224f763015d04d2cd2e4b"
update_frequency: "10s"
log_level: info
tls_enabled: false
tls_ca_cert: ""
tls_client_cert: ""
tls_client_key: ""
tls_skip_verify: false
```

### Option: `api_url` (required)

Set local API url.

### Option: `api_key` (required)

Set local API key.

### Option: `update_frequency` (optional)

Controls how often the bouncer is going to query the local API.

### Option: `nftables_hooks` (optional)

Controls the nftables hooks to use to configure multiple chains.
Can be:

* `prerouting`
* `input` (default)
* `forward`
* `output`
* `postrouting`
* `ingress`

### Option: `log_level` (optional)

Controls logging level.

### Option: `tls_enabled` (optional)

Enable TLS client authentication for connecting to a remote LAPI. When enabled, certificate files must be placed in Home Assistant's `/ssl/` directory.

### Option: `tls_ca_cert` (optional)

Filename of the CA certificate in `/ssl/` directory. Used to verify the remote LAPI server certificate.

### Option: `tls_client_cert` (optional)

Filename of the client certificate in `/ssl/` directory. Used for mTLS authentication with the remote LAPI.

### Option: `tls_client_key` (optional)

Filename of the client private key in `/ssl/` directory. Must match the client certificate.

### Option: `tls_skip_verify` (optional)

Skip TLS certificate verification. **Warning: This is insecure and should only be used for testing.**

## TLS Authentication

To connect to a remote LAPI using TLS/mTLS authentication instead of API key authentication:

### 1. Place certificates in Home Assistant's SSL directory

Copy your certificates to `/ssl/` (accessible via Home Assistant's file editor or SSH):
- `ca.crt` - CA certificate that signed the LAPI server certificate
- `bouncer.crt` - Client certificate for this bouncer
- `bouncer.key` - Client private key

### 2. Configure the add-on

```yaml
api_url: "https://your-lapi-server:8080/"
api_key: ""
tls_enabled: true
tls_ca_cert: "ca.crt"
tls_client_cert: "bouncer.crt"
tls_client_key: "bouncer.key"
```

When using TLS authentication with mTLS (client certificates), `api_key` can be left empty.

### 3. Generate certificates (if needed)

On your CrowdSec LAPI server, you can generate certificates using your preferred CA. See the [CrowdSec TLS documentation](https://doc.crowdsec.net/docs/local_api/tls_auth) for details on configuring TLS authentication.

## Support

Got questions?

You have several options to get them answered:

- The [Crowdsec Discord Chat Server][discord].
- The Home Assistant [Community Forum][forum].

In case you've found a bug, please [open an issue on our GitHub][issue].

[discord]: https://discord.gg/wGN7ShmEE8
[forum]: https://discourse.crowdsec.net/
[issue]: https://github.com/crowdsecurity/home-assistant-addons/issues
