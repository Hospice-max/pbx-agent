# PBX Agent

Open-source monitoring agent for Asterisk / FreePBX.

PBX Agent connects to Asterisk through the Asterisk Manager Interface (AMI) and exposes a lightweight local HTTP API and web interface for real-time PBX state.

## Features

- Python 3 implementation; no external Python dependency.
- AMI reconnect loop with exponential backoff.
- PJSIP endpoint discovery.
- Extension state monitoring through `ExtensionStateList`, `ExtensionStatus` and `ExtensionState` events.
- Contact reachability monitoring through `ContactStatus`.
- Active channel and call counters.
- Health endpoint.
- JSON API suitable for integrations.
- Static web dashboard.
- systemd service.
- Configuration outside the source tree.
- Safe installation and uninstall scripts.
- MIT licensed.

## Architecture

```text
                         +-----------------------+
                         |       Browser         |
                         |   /pbx-agent/         |
                         +-----------+-----------+
                                     |
                                  HTTP API
                                     |
                         +-----------v-----------+
                         |      PBX Agent        |
                         | Python 3 / stdlib     |
                         +-----------+-----------+
                                     |
                                   AMI
                                     |
                         +-----------v-----------+
                         |       Asterisk        |
                         |   PJSIP / channels    |
                         +-----------------------+
```

AMI is Asterisk's asynchronous management interface. It is used here for state/events rather than replacing the Asterisk dialplan. See the official Asterisk AMI documentation: https://docs.asterisk.org/Configuration/Interfaces/Asterisk-Manager-Interface-AMI/.

## Requirements

- Linux
- Asterisk 16+ recommended
- AMI enabled on Asterisk
- Python 3.8+
- systemd
- A web browser

The agent itself does not require Apache, Nginx, PHP, Node.js or a Python package manager. Its built-in HTTP server serves the dashboard and API.

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_ORG/pbx-agent.git
cd pbx-agent
```

Run the installer as root:

```bash
sudo ./scripts/install.sh
```

The installer asks for the AMI host, port, username and secret. The secret is written to `/etc/pbx-agent/pbx-agent.conf`, not to the Git repository.

After installation:

```bash
systemctl status pbx-agent
journalctl -u pbx-agent -f
```

Open:

```text
http://PBX_IP:8099/
```

## Configuration

Default file:

```text
/etc/pbx-agent/pbx-agent.conf
```

Example:

```ini
[asterisk]
host = 127.0.0.1
port = 5038
username = pbx_agent
secret = CHANGE_ME
connect_timeout = 10
reconnect_initial = 2
reconnect_max = 30

[agent]
state_file = /var/lib/pbx-agent/state.json
log_level = INFO

[http]
host = 127.0.0.1
port = 8099

[security]
allow_origins =
```

To make the dashboard reachable from another machine, change `[http] host` to `0.0.0.0` and protect the port with the server firewall/reverse proxy as appropriate.

## API

`GET /api/health`

Returns agent and AMI health.

`GET /api/status`

Returns the complete current state.

`GET /api/extensions`

Returns extension state records.

`GET /api/calls`

Returns currently tracked channels and call counters.

`GET /api/pjsip`

Returns PJSIP endpoint/contact state collected through AMI events.

## Asterisk AMI permissions

Create a dedicated AMI account instead of reusing an administrator account. The agent is intended to operate as a read-only monitor.

Example concept for `manager.conf`:

```ini
[pbx_agent]
secret = CHANGE_ME
read = system,call,reporting
write = none
permit = 127.0.0.1/255.255.255.255
```

The exact permissions required can vary with the Asterisk version and the events/actions enabled on the PBX. Validate the account against your Asterisk configuration before production use.

## Upgrade

```bash
cd /path/to/pbx-agent
git pull
sudo ./scripts/install.sh
```

The installer preserves `/etc/pbx-agent/pbx-agent.conf` unless you explicitly choose to overwrite it.

## Uninstall

```bash
sudo ./scripts/uninstall.sh
```

The uninstall script removes the service and installed program files. It deliberately does not delete `/etc/pbx-agent/pbx-agent.conf` automatically.

## Logs and troubleshooting

```bash
systemctl status pbx-agent
journalctl -u pbx-agent -n 100 --no-pager
ss -lntp | grep 8099
ss -lntp | grep 5038
```

Test the API locally:

```bash
curl http://127.0.0.1:8099/api/health
curl http://127.0.0.1:8099/api/extensions
```

If AMI is unavailable, the HTTP API remains available and reports the AMI connection as unhealthy.

## Development

Run without installing:

```bash
python3 -m agent.main --config ./config/pbx-agent.conf.example
```

Or:

```bash
PYTHONPATH=. python3 -m agent.main --config ./config/pbx-agent.conf.example
```

Run syntax checks:

```bash
python3 -m compileall agent
```

Run tests:

```bash
python3 -m unittest discover -s tests -v
```

## Security

Read `SECURITY.md` before exposing the HTTP API or AMI outside localhost. Never commit AMI secrets. For security reports, use the process described in `SECURITY.md`.

## License

MIT. See `LICENSE`.
