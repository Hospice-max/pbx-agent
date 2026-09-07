#!/bin/bash
set -euo pipefail

PREFIX=/opt/pbx-agent
ETC=/etc/pbx-agent
STATE=/var/lib/pbx-agent
SERVICE=/etc/systemd/system/pbx-agent.service
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [ "${EUID}" -ne 0 ]; then
  echo "Please run as root."
  exit 1
fi

command -v python3 >/dev/null || { echo "python3 is required."; exit 1; }

mkdir -p "$PREFIX" "$ETC" "$STATE"
cp -a "$ROOT_DIR/agent" "$PREFIX/"
cp -a "$ROOT_DIR/web" "$PREFIX/"
cp "$ROOT_DIR/systemd/pbx-agent.service" "$SERVICE"

if [ ! -f "$ETC/pbx-agent.conf" ]; then
  read -r -p "AMI host [127.0.0.1]: " AMI_HOST
  read -r -p "AMI port [5038]: " AMI_PORT
  read -r -p "AMI username: " AMI_USER
  read -r -s -p "AMI secret: " AMI_SECRET
  echo
  AMI_HOST=${AMI_HOST:-127.0.0.1}
  AMI_PORT=${AMI_PORT:-5038}
  AMI_USER=${AMI_USER:-pbx_agent}
  cat > "$ETC/pbx-agent.conf" <<CFG
[asterisk]
host = ${AMI_HOST}
port = ${AMI_PORT}
username = ${AMI_USER}
secret = ${AMI_SECRET}
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
CFG
  chmod 600 "$ETC/pbx-agent.conf"
else
  echo "Keeping existing $ETC/pbx-agent.conf"
fi

python3 -m compileall -q "$PREFIX/agent"
systemctl daemon-reload
systemctl enable pbx-agent.service
systemctl restart pbx-agent.service

echo
echo "PBX Agent installed."
echo "Status: systemctl status pbx-agent"
echo "Logs:   journalctl -u pbx-agent -f"
echo "URL:    http://127.0.0.1:8099/"
