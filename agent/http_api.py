import json
import logging
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


class Handler(BaseHTTPRequestHandler):
    store = None
    web_root = None
    allow_origins = ""

    def log_message(self, fmt, *args):
        logging.getLogger("pbx-agent.http").info("%s - %s", self.address_string(), fmt % args)

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if self.allow_origins:
            self.send_header("Access-Control-Allow-Origin", self.allow_origins)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            snapshot = self.store.snapshot()
            self.send_json({"ok": snapshot["health"]["ami_connected"], "health": snapshot["health"]})
            return
        if path == "/api/status":
            self.send_json(self.store.snapshot())
            return
        if path == "/api/extensions":
            self.send_json(list(self.store.snapshot()["extensions"].values()))
            return
        if path == "/api/pjsip":
            self.send_json(list(self.store.snapshot()["endpoints"].values()))
            return
        if path == "/api/calls":
            snapshot = self.store.snapshot()
            self.send_json({"summary": snapshot["summary"], "channels": snapshot["channels"]})
            return
        if path in ("/", "/index.html"):
            path = "/index.html"
        self.serve_static(path)

    def serve_static(self, path):
        relative = path.lstrip("/")
        if ".." in relative.split("/"):
            self.send_json({"error": "invalid path"}, 400)
            return
        file_path = os.path.join(self.web_root, relative)
        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, "index.html")
        if not os.path.isfile(file_path):
            self.send_json({"error": "not found"}, 404)
            return
        content_types = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}
        ext = os.path.splitext(file_path)[1]
        with open(file_path, "rb") as handle:
            body = handle.read()
        self.send_response(200)
        self.send_header("Content-Type", content_types.get(ext, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(settings, store, web_root):
    Handler.store = store
    Handler.web_root = web_root
    Handler.allow_origins = settings.allow_origins
    server = ThreadingHTTPServer((settings.http_host, settings.http_port), Handler)
    logging.getLogger("pbx-agent.http").info("HTTP server listening on %s:%s", settings.http_host, settings.http_port)
    server.serve_forever()
