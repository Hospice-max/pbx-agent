# Configuration

The production configuration is `/etc/pbx-agent/pbx-agent.conf`.

The example configuration is `config/pbx-agent.conf.example`.

## AMI

`host` and `port` identify the AMI listener. `username` and `secret` are the dedicated monitoring credentials.

For a local agent, prefer `127.0.0.1` and a local AMI account. Do not expose AMI to the public Internet.

## HTTP

The default listener is `127.0.0.1:8099`. This is intentional: remote access should normally be provided through a reverse proxy, VPN or controlled firewall rule.
