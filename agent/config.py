from configparser import ConfigParser
from dataclasses import dataclass


@dataclass
class Settings:
    ami_host: str
    ami_port: int
    ami_username: str
    ami_secret: str
    connect_timeout: float
    reconnect_initial: float
    reconnect_max: float
    state_file: str
    log_level: str
    http_host: str
    http_port: int
    allow_origins: str


def load_config(path: str) -> Settings:
    parser = ConfigParser()
    if not parser.read(path):
        raise FileNotFoundError("Configuration file not found: %s" % path)

    a = parser["asterisk"]
    agent = parser["agent"]
    http = parser["http"]
    security = parser["security"] if parser.has_section("security") else {}

    return Settings(
        ami_host=a.get("host", "127.0.0.1"),
        ami_port=a.getint("port", 5038),
        ami_username=a.get("username", ""),
        ami_secret=a.get("secret", ""),
        connect_timeout=a.getfloat("connect_timeout", 10),
        reconnect_initial=a.getfloat("reconnect_initial", 2),
        reconnect_max=a.getfloat("reconnect_max", 30),
        state_file=agent.get("state_file", "/var/lib/pbx-agent/state.json"),
        log_level=agent.get("log_level", "INFO"),
        http_host=http.get("host", "127.0.0.1"),
        http_port=http.getint("port", 8099),
        allow_origins=security.get("allow_origins", ""),
    )
