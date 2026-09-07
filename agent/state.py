import json
import os
import threading
from datetime import datetime, timezone


STATUS_MAP = {
    "0": ("available", "Libre", "status-yellow", 2),
    "1": ("in_use", "En ligne / en appel", "status-green", 1),
    "2": ("busy", "Occupé", "status-green", 1),
    "4": ("unavailable", "Inaccessible", "status-red", 4),
    "8": ("ringing", "Sonnerie", "status-orange", 3),
    "9": ("ringing", "En ligne et sonnerie", "status-orange", 3),
    "16": ("on_hold", "En attente", "status-orange", 3),
    "17": ("on_hold", "En ligne et en attente", "status-orange", 3),
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


class StateStore:
    def __init__(self, path):
        self.path = path
        self.lock = threading.RLock()
        self.extensions = {}
        self.endpoints = {}
        self.channels = {}
        self.meta = {
            "started_at": now_iso(),
            "last_event_at": None,
            "ami_connected": False,
            "ami_error": None,
        }

    def set_ami(self, connected, error=None):
        with self.lock:
            self.meta["ami_connected"] = connected
            self.meta["ami_error"] = error
            if connected:
                self.meta["last_event_at"] = now_iso()

    def touch_event(self):
        with self.lock:
            self.meta["last_event_at"] = now_iso()

    def update_extension(self, ext, context, status):
        state, text, css, priority = STATUS_MAP.get(
            str(status), ("unknown", "Statut %s" % status, "status-red", 5)
        )
        with self.lock:
            self.extensions[str(ext)] = {
                "extension": str(ext),
                "context": context or "ext-local",
                "state": state,
                "status_code": str(status),
                "text": text,
                "class": css,
                "priority": priority,
                "updated_at": now_iso(),
            }
            self.meta["last_event_at"] = now_iso()

    def update_endpoint(self, name, device_state=None, contact_status=None):
        with self.lock:
            item = self.endpoints.setdefault(str(name), {
                "endpoint": str(name),
                "technology": "PJSIP",
            })
            if device_state is not None:
                item["device_state"] = device_state
            if contact_status is not None:
                item["contact_status"] = contact_status
                item["registered"] = contact_status == "Reachable"
            item["updated_at"] = now_iso()
            self.meta["last_event_at"] = now_iso()

    def add_channel(self, channel, uniqueid, state, caller=None, connected=None):
        if not channel:
            return
        with self.lock:
            self.channels[uniqueid or channel] = {
                "channel": channel,
                "uniqueid": uniqueid or channel,
                "state": state,
                "caller": caller or "",
                "connected": connected or "",
                "updated_at": now_iso(),
            }
            self.meta["last_event_at"] = now_iso()

    def remove_channel(self, uniqueid):
        if not uniqueid:
            return
        with self.lock:
            self.channels.pop(uniqueid, None)
            self.meta["last_event_at"] = now_iso()

    def snapshot(self):
        with self.lock:
            channels = list(self.channels.values())
            return {
                "version": 1,
                "generated_at": now_iso(),
                "health": dict(self.meta),
                "summary": {
                    "extensions": len(self.extensions),
                    "endpoints": len(self.endpoints),
                    "active_channels": len(channels),
                },
                "extensions": dict(self.extensions),
                "endpoints": dict(self.endpoints),
                "channels": channels,
            }

    def persist(self):
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump(self.snapshot(), handle, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)
