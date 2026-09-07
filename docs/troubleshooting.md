# Troubleshooting

## Service does not start

```bash
systemctl status pbx-agent --no-pager
journalctl -u pbx-agent -n 200 --no-pager
```

Check Python:

```bash
python3 --version
```

Check the configuration:

```bash
python3 - <<'PY'
from agent.config import load_config
print(load_config('/etc/pbx-agent/pbx-agent.conf'))
PY
```

## AMI is disconnected

Check Asterisk:

```bash
systemctl status asterisk
ss -lntp | grep 5038
```

Confirm that the AMI account exists and that its ACL permits the agent host.

## Dashboard unavailable

```bash
ss -lntp | grep 8099
curl http://127.0.0.1:8099/api/health
```

If the service listens only on `127.0.0.1`, remote clients cannot connect directly by design.
