#!/bin/bash
set -euo pipefail

if [ "${EUID}" -ne 0 ]; then
  echo "Please run as root."
  exit 1
fi

systemctl disable --now pbx-agent.service 2>/dev/null || true
rm -f /etc/systemd/system/pbx-agent.service
rm -rf /opt/pbx-agent
rm -rf /var/lib/pbx-agent
systemctl daemon-reload

echo "PBX Agent binaries and state removed."
echo "Configuration was kept at /etc/pbx-agent/pbx-agent.conf."
echo "Remove it manually if you also want to delete the AMI credentials."
