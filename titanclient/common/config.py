from types import SimpleNamespace
from os.path import expanduser, isfile

import toml

defaults = {
    "loglevel": "INFO",
    "logdir": "/tmp/titanclient",
    "cachedir": "~/.cache/titanclient",
    "path": "~/.config/titanclient/config.toml"}

settings = SimpleNamespace(**defaults)
hostlist = []

def load_config(path):

    global settings
    global hostlist

    if not isfile(path):
        return settings

    with open(path, "r") as f:
        data = toml.loads(f.read())
        hostlist = data.get("host", [])
        settings.__dict__.update(data["settings"])
        settings.cachedir = expanduser(settings.cachedir)

load_config(expanduser(settings.path))
