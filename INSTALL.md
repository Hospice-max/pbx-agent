# Installation guide

## 1. Prepare Asterisk AMI

Enable AMI according to your Asterisk deployment and create a dedicated monitoring account.

## 2. Install

```bash
sudo ./scripts/install.sh
```

## 3. Validate

```bash
systemctl status pbx-agent
curl http://127.0.0.1:8099/api/health
```

## 4. Open the dashboard

On the PBX itself:

```text
http://127.0.0.1:8099/
```

For remote access, configure a reverse proxy or controlled network access.
