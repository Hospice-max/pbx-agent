import logging
import socket
import time


class AMIError(Exception):
    pass


def parse_message(raw):
    result = {}
    for line in raw.split("\r\n"):
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    return result


class AMIClient:
    def __init__(self, settings, store):
        self.settings = settings
        self.store = store
        self.log = logging.getLogger("pbx-agent.ami")
        self.sock = None
        self.buffer = ""

    def send_action(self, action, **fields):
        lines = ["Action: %s" % action]
        for key, value in fields.items():
            if value is not None:
                lines.append("%s: %s" % (key, value))
        payload = "\r\n".join(lines) + "\r\n\r\n"
        self.sock.sendall(payload.encode("utf-8"))

    def connect(self):
        self.sock = socket.create_connection(
            (self.settings.ami_host, self.settings.ami_port),
            timeout=self.settings.connect_timeout,
        )
        self.sock.settimeout(30)
        self._read_banner()
        self.send_action(
            "Login",
            Username=self.settings.ami_username,
            Secret=self.settings.ami_secret,
            Events="on",
        )
        self.send_action("PJSIPShowEndpoints")
        self.send_action("ExtensionStateList")
        self.send_action("CoreShowChannels")
        self.store.set_ami(True)
        self.log.info("Connected to Asterisk AMI %s:%s", self.settings.ami_host, self.settings.ami_port)

    def _read_banner(self):
        try:
            self.sock.recv(4096)
        except socket.timeout:
            pass

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass
        self.sock = None
        self.store.set_ami(False)

    def run_forever(self):
        delay = self.settings.reconnect_initial
        while True:
            try:
                self.connect()
                delay = self.settings.reconnect_initial
                self.read_events()
            except Exception as exc:
                self.log.error("AMI connection error: %s", exc)
                self.store.set_ami(False, str(exc))
            finally:
                self.close()
            time.sleep(delay)
            delay = min(delay * 2, self.settings.reconnect_max)

    def read_events(self):
        while self.sock:
            data = self.sock.recv(8192)
            if not data:
                raise AMIError("AMI connection closed")
            self.buffer += data.decode("utf-8", errors="replace")
            while "\r\n\r\n" in self.buffer:
                raw, self.buffer = self.buffer.split("\r\n\r\n", 1)
                if raw.strip():
                    self.handle(parse_message(raw))

    def handle(self, msg):
        event = msg.get("Event")
        if not event:
            return
        self.store.touch_event()

        if event == "EndpointList":
            self.store.update_endpoint(
                msg.get("ObjectName", ""),
                device_state=msg.get("DeviceState"),
            )
        elif event == "ContactStatus":
            self.store.update_endpoint(
                msg.get("EndpointName", ""),
                contact_status=msg.get("ContactStatus"),
            )
        elif event in ("ExtensionStatus", "ExtensionState"):
            ext = msg.get("Exten")
            context = msg.get("Context", "ext-local")
            status = msg.get("Status", "0")
            if ext and (context == "ext-local" or not context):
                self.store.update_extension(ext, context, status)
        elif event == "Newchannel":
            self.store.add_channel(
                msg.get("Channel"), msg.get("Uniqueid"), "new",
                msg.get("CallerIDNum"), msg.get("ConnectedLineNum"),
            )
        elif event == "Newstate":
            self.store.add_channel(
                msg.get("Channel"), msg.get("Uniqueid"), msg.get("ChannelStateDesc", "unknown"),
                msg.get("CallerIDNum"), msg.get("ConnectedLineNum"),
            )
        elif event == "Hangup":
            self.store.remove_channel(msg.get("Uniqueid"))
