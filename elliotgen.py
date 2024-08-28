import os
import sys
import json
from subprocess import run
from urllib.request import urlopen

name = "openapi.json"

os.chdir("titanclient/elliot")

url = sys.argv[1]
with urlopen(url) as r:
    data = json.loads(r.read())
    data["info"].update({"version": "1.0.0"})
    with open(name, "w") as f:
        f.write(json.dumps(data, indent=2))

os.makedirs("openapi", exist_ok=True)
cmd = f"openapi-python-client update --meta none --path {name} --config ../../openapi_config.yaml"
run(cmd, shell=True)
os.remove(name)

from titanclient.elliot.client import ElliotClient
c = ElliotClient("http://localhost:5000")
c.login(username="admin", password="admin") 