import argparse
import logging
import threading

from .ami import AMIClient
from .config import load_config
from .http_api import serve
from .state import StateStore


DEFAULT_CONFIG = "/etc/pbx-agent/pbx-agent.conf"
WEB_ROOT = "/opt/pbx-agent/web"


def main():
    parser = argparse.ArgumentParser(description="Open-source Asterisk PBX monitoring agent")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--web-root", default=WEB_ROOT)
    args = parser.parse_args()

    settings = load_config(args.config)
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    store = StateStore(settings.state_file)
    store.persist()

    ami = AMIClient(settings, store)
    ami_thread = threading.Thread(target=ami.run_forever, name="ami", daemon=True)
    ami_thread.start()

    serve(settings, store, args.web_root)


if __name__ == "__main__":
    main()
