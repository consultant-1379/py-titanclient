import os
import json
import time
import threading

from abc import ABC, abstractmethod
from types import SimpleNamespace
from datetime import datetime

from ..host.files.config import Config
from ..host.files.gpl import GPLData
from ..host.files.statuscode import StatusCodeData
from ..host.files.latency import LatencyData

from ..stats.collections import Values, Stats
from ..common.logger import logger
from ..common.util import list_files
from ..common.config import settings


def load_from_directory(args):
    results = SimpleNamespace(config=[], gpl=[], latency=[], status_codes=[])
    for name in os.listdir(args.directory):
        p = os.path.join(args.directory, name)
        files = list_files(p, ".*evs\\.ec\\.csv$")
        results.config.append(ConfigStatistics(Config(p, name=name), args.config or Values.list(Stats.CONFIG)))
        results.gpl.append(GPLStatistics(GPLData(os.path.join(p, "stat"), name=name), args.gpl or Values.list(Stats.GPL)))
        results.latency.append(LatencyStatistics(LatencyData(p, name=name), args.latency or Values.list("REQUEST")))
        results.status_codes.append(StatusCodeStatistics(StatusCodeData(files[0], name=name)))

    return results

class Statistics:

    def __init__(
            self,
            *logs,
            aggregate=False,
            poller=None,
            progress=None,
            timestamp=None):

        self.logs = logs
        self.stats = SimpleNamespace()
        self.timestamp = timestamp

        self._aggregate = aggregate
        self._poller = poller
        self._progress = progress

        self._types = [s for s in Stats() if s != Stats.TRAFFIC]

    def __repr__(self):
        return f"<Statistics ({len(self.logs)})>"

    def __iter__(self):
        try:
            for stat in self._types:
                if not hasattr(self.stats, stat):
                    continue

                for s in getattr(self.stats, stat):
                    yield s
        finally:
            pass

    def all(self, config=[], gpl=[], latency=[], status_codes=False, interval={}):

        if config:
            self.config(config)
        if gpl:
            self.gpl(gpl)
        if latency:
            self.latency(latency)
        if status_codes:
            self.status_codes()
        if interval:
            self.interval(**interval)

        return self

    def config(self, stats=[]):
        return self._get_data(Stats.CONFIG, self.logs, stats)

    def gpl(self, stats=[]):
        return self._get_data(Stats.GPL, self.logs, stats)

    def latency(self, stats=[]):

        return self._get_data(Stats.LATENCY, self.logs, stats)

    def status_codes(self, stats=[]):
        return self._get_data(Stats.STATUSCODES, self.logs, stats)

    def interval(self, stats, start=None, end=None):
        return self._get_data("interval", self.logs, stats)

    def timeline(self, stats, start=None, end=None):
        return self._get_data("timeline", self.logs, stats)

    def _get_data(self, stats_type, logs, stats):

        threads = []
        results = []
        poller_set = False

        for log in logs:

            def fetch_thread(
                    results,
                    ns,
                    poller,
                    progress,
                    log,
                    timestamp):

                if not hasattr(ns, stats_type):
                    setattr(ns, stats_type, set())

                stat_attr = getattr(ns, stats_type)

                # handle repeated calls
                for stat in stat_attr:
                    if log.name == stat.name:
                        continue

                # this is the expensive part
                obj = getattr(log, stats_type)(poller=poller)

                if stats_type == Stats.CONFIG:
                    s = ConfigStatistics(obj, stats, log=log)

                if stats_type == Stats.GPL:
                    s = GPLStatistics(obj, stats, log=log)

                if stats_type == Stats.LATENCY:
                    s = LatencyStatistics(obj, stats, log=log)

                if stats_type == Stats.STATUSCODES:
                    s = StatusCodeStatistics(obj, log=log)

                stat_attr.add(s)
                results.append(s)

            t = threading.Thread(
                target=fetch_thread,
                args=(results,
                      self.stats,
                      self._poller if not poller_set else None,
                      self._progress,
                      log,
                      self.timestamp))

            poller_set = True

            t.start()
            threads.append(t)

        joined = [t.join() for t in threads]

        return results


class MumbleStatistics(ABC):

    def __init__(self, obj, stats=None, log=None, stat_type="unknown"):
        self.type = stat_type
        self.log = log or None

        self.name = obj.name if hasattr(obj, "name") else "N/A"
        self.obj = obj
        self._data = {}
        self._stats = sorted(stats) if stats else []

        if self.obj:
            self._load()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

    def __iter__(self):
        return self.rows()

    def json(self):
        return json.dumps(self._data)

    def scenarios(self):
        return sorted(self._data.keys())

    def stats(self):
        try:
            for stat in self._stats:
                yield stat
        finally:
            pass

    def summary(self):
        return None

    @abstractmethod
    def rows(self):
        pass

    @abstractmethod
    def _load(self):
        pass


class GPLStatistics(MumbleStatistics):

    def __init__(self, obj, stats, log=None, timestamp=None):
        if isinstance(obj, set):
            self._gpls = obj
        else:
            self._gpls = {obj} if obj else set()
        self.timestamp = timestamp

        super().__init__(obj, stats, log=log, stat_type="gpl")

        atstr = self.timestamp and f" at {datetime.fromtimestamp(self.timestamp)}" or ""
        self.name = f"{self.name}{atstr}"

        self._groups = self._make_groups(stats)
        self.summary = False

    def __add__(self, peer):
        stats = set(self.stats()).union(peer.stats())
        gpl = GPLStatistics(self._gpls | peer._gpls, stats, timestamp=self.timestamp)
        gpl.summary = True
        gpl.name = f"Summary({len(gpl._gpls)})"
        return gpl

    def __radd__(self, peer):
        return self if peer == 0 else self.__add__(peer)

    def _load(self):
        for gpl_data in self._gpls:
            for s in sorted(gpl_data.get_traffic_cases()):
                if not self._data.get(s):
                    self._data[s] = {}
                for name in self._stats:
                    if not self._data[s].get(name):
                        self._data[s][name] = []

                    value = getattr(gpl_data, name)(s, timestamp=self.timestamp)
                    if value is not None:
                        self._data[s][name].append(value)

    def stats(self):
        for g in self.groups():
            for m in self.members(g):
                yield m if g == "-" else f"{g}_{m}"

    def _idmap(self, stats):
        return { v["name"]: v["id"] for v in stats}

    def groups(self):
        sortmap = self._idmap(Values.GROUPS)
        key = lambda v: sortmap.get(v)
        groups = self._groups.keys()
        return sorted(groups, key=key)

    def members(self, group):
        sortmap = self._idmap(Values.GPL)
        key = lambda m: sortmap.get(f"{group}_{m}")
        members = self._groups.get(group)
        return sorted(members, key=key)

    def rows(self):
        for scen in self.scenarios():
            cols = [self._sum(n, self._value(n, scen)) for n in self.stats()]
            yield [scen] + cols

    def overall(self):
        overall = {}
        for stat in self.stats():
            overall[stat] = self._value_overall(stat)
        return overall

    def _sum(self, name, values):
        if "_gos" in name and values:
            return sum(values) / len(values)
        else:
            return sum(values) if values else None

    def _value(self, name, scen):
        return self._data.get(scen, {}).get(name, [])

    def _value_overall(self, name):

        if "_gos" in name:
            return self._gos_overall(name)

        values = []
        for s in self.scenarios():
            values += self._value(name, s)

        return sum(values) if values else None

    def _gos_overall(self, name):

        prefix = name.rsplit('_gos')[0]
        exclude_retry = "excluding_retry" in name

        failed_vals = []
        success_vals = []
        retry_vals = []

        for s in self.scenarios():
            failed_vals += self._value(f"{prefix}_failed", s)
            success_vals += self._value(f"{prefix}_success", s)

            if not exclude_retry:
                retry_vals += self._value(f"{prefix}_retry", s)

        success_total = sum(success_vals)
        failed_total = sum(failed_vals)
        retry_total = sum(retry_vals) if retry_vals else 0

        if not success_total and not failed_total:
            return None

        return success_total / (failed_total + success_total + retry_total) * 100

    @staticmethod
    def _make_groups(stats):
        groups = {}
        for v in stats:
            try:
                prefix, suffix = map(str.strip, v.split("_", 1))
            except:
                prefix, suffix = v, None
            group = groups.setdefault("-" if not suffix else prefix, [])
            group.append(suffix or prefix)
        return groups


class ConfigStatistics(MumbleStatistics):

    def __init__(self, obj, stats, log=None):
        super().__init__(obj, stats, log=log, stat_type="config")
        self._configs = {obj} if obj else set()
        self.summary = False

    def __add__(self, peer):

        stats = set(list(self._stats) + list(peer._stats))
        scens = set(list(self.scenarios()) + list(peer.scenarios()))

        config = ConfigStatistics(None, stats)
        config._configs = self._configs | peer._configs
        config.summary = True
        config.name = f"Summary({len(config._configs)})"

        data = {}
        for scen in sorted(scens):
            data[scen] = {}
            for stat in sorted(stats):
                val1 = self._data.get(scen, {}).get(stat)
                val2 = peer._data.get(scen, {}).get(stat)
                if val1 is None or val2 is None:
                    _sum = val1 or val2 or None
                elif stat in ["cps", "rps", "rrps"]:
                    _sum = (val1 or 0) + (val2 or 0)
                elif val1 == val2 or val2 in val1:
                    _sum = val1
                else:
                    _sum = ",".join([val1, val2])
                data[scen][stat] = _sum
        config._data = data

        return config

    def __radd__(self, peer):
        return self if peer == 0 else self.__add__(peer)

    def _load(self):
        for scen in self.obj.get_traffic_cases():
            self._data[scen.name] = {s:getattr(scen, s)() for s in self._stats}

    def rows(self):
        try:
            for scen, data in self._data.items():
                yield [scen] + [data.get(s) for s in self._stats]
        finally:
            pass


class LatencyStatistics(MumbleStatistics):

    def __init__(self, obj, stats, log=None):
        super().__init__(obj, stats, log=log, stat_type="latency")
        self.keys = ["amount", "latency", "min", "max", "95%", "90%"]
        self._latencies = {obj} if obj else set()
        self.summary = False

    def __add__(self, peer):
        stats = set(list(self._stats) + list(peer._stats))
        scens = set(list(self.scenarios()) + list(peer.scenarios()))
        reqs = set(self.requests() + peer.requests())

        latency = LatencyStatistics(None, list(stats))
        latency._latencies = self._latencies | peer._latencies
        latency.summary = True
        latency.name = f"Summary({len(latency._latencies)})"

        data = {}
        for scen in scens:
            data[scen] = {}
            for req in reqs:
                data[scen][req] = {}
                these = self.values(scen, req)
                those = peer.values(scen, req)
                for k in self.keys:
                    val1 = these.get(k) if these else None
                    val2 = those.get(k) if those else None

                    if val1 is None or val2 is None:
                        _sum = val1 or val2 or None
                    elif k == "amount":
                        _sum = (val1 or 0) + (val2 or 0)
                    elif k == "min":
                        mins = list(filter(lambda v: v is not None, [val1, val2]))
                        _sum = min(mins) if mins else None
                    elif k == "max":
                        maxs = list(filter(lambda v: v is not None, [val1, val2]))
                        _sum = max(maxs) if maxs else None
                    elif k in ["latency", "95%", "90%"]:
                        _sum = ((val1 or 0) + (val2 or 0)) / 2

                    if _sum is not None:
                        data[scen][req][k] = _sum

                if not data[scen][req]:
                    data[scen][req] = None
        latency._data = data

        return latency

    def __radd__(self, peer):
        return self if peer == 0 else self.__add__(peer)

    def _load(self):
        for scen in self.obj.get_traffic_cases():
            self._data[scen] = self.obj.query(scen, self._stats)

    def rows(self):
        try:
            for scen, data in self._data.items():
                yield [scen] + [data.get(s) for s in self._stats]
        finally:
            pass

    def requests(self):
        return self._stats

    def values(self, scenario, request):
        return self._data.get(scenario, {}).get(request)


class StatusCodeStatistics(MumbleStatistics):

    def __init__(self, obj, log=None):
        super().__init__(obj, log=log, stat_type="status_codes")
        self.__scs = {obj} if obj else set()
        self.summary = False

    def __add__(self, peer):
        sc = StatusCodeStatistics(None)
        sc.__scs = self.__scs | peer.__scs
        sc.summary = True
        sc.name = f"Summary({len(sc.__scs)})"

        reqs = set()
        for s in sc.__scs:
            reqs = reqs.union(set(s.get_requests()))

        scens = set(list(self.scenarios()) + list(peer.scenarios()))

        data = {}
        for scen in sorted(scens):
            data[scen] = {}
            for r in reqs:
                data[scen][r] = {}
                corrs = set()
                for s in sc.__scs:
                    corrs = corrs.union(s.get_correlations(r))
                for c in corrs:
                    val1 = self.amount(scen, r, c)
                    val2 = peer.amount(scen, r, c)
                    if val1 is None or val2 is None:
                        _sum = val1 or val2 or None
                    else:
                        _sum = val1 + val2

                    data[scen][r][c] = _sum

        sc._data = data

        return sc

    def __radd__(self, peer):
        return self if peer == 0 else self.__add__(peer)

    def _load(self):
        for scen in self.obj.get_traffic_cases():
            self._data[scen] = {}
            for r in self.obj.get_requests():
                self._data[scen][r] = {}
                for c in self.obj.get_correlations(r):
                    self._data[scen][r][c] = self.obj.get_amount(scen, r, c)

    def rows(self):
        try:
            for scen in sorted(self.scenarios()):
                row = [scen]
                for r in self.requests():
                    for c in self.correlations(r):
                        row = row + [self.amount(scen, r, c)]
                yield row
        finally:
            pass

    def requests(self):
        result = set()
        for scen, reqs in self._data.items():
            for req in reqs.keys():
                result.add(req)
        return sorted(list(result))

    def correlations(self, request):
        result = set()
        for scen, reqs in self._data.items():
            corrs = reqs.get(request)
            if corrs:
                for c in corrs:
                    result.add(c)
        return sorted(list(result))

    def amount(self, scenario, request, correlation):
        return self._data.get(scenario, {}).get(request, {}).get(correlation)

    def overall(self):
        result = {}
        for r in sorted(self.requests()):
            result[r] = {}
            for c in sorted(self.correlations(r)):
                values = [self.amount(s, r, c) for s in sorted(self.scenarios())]
                result[r][c] = sum(filter(bool, values))
        return result
