from ..common.util import tmap
from ..common.config import hostlist
from ..host.client import HostClient


def hosts(regex=None, host_ids=[]):
    rx = re.compile(regex) if regex else None
    results = []
    for h in hostlist:
        hc = HostClient(config=h)
        if host_ids:
            if str(hc.id) in host_ids:
                results.append(hc)
        else:
            results.append(hc)

    return results


def logs(log_ids=()):

    results = []
    for hc, logs in tmap(lambda hc: (hc, hc.logs()), hosts()):
        for l in logs:
            if not log_ids or str(l.id) in log_ids:
                results.append(l)

    return results


def do(f, host_ids):
    tmap(f, hosts(host_ids=host_ids))
