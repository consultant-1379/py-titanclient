import os
import re
import hashlib

from ..common.util import uuid
from ..common.logger import logger
from ..common.config import settings

from ..host.files.config import Config
from ..host.files.gpl import GPLData
from ..host.files.statuscode import StatusCodeData
from ..host.files.latency import LatencyData

from ..host.connection import FileTransfer
from ..host.cache import cache, cache_status, clear_cache


class Log:

    def __init__(self, path, runtime=None, available={}, client=None):

        self.name = os.path.basename(path)
        self.runtime = runtime
        self.path = path
        self.client = client
        self.id = uuid(self.name + self.client.config.hostname)

        self._available = {
            "gpl": available.get("gpl", False),
            "config": available.get("config", False),
            "latency": available.get("latency", False),
            "status_codes": available.get("status_codes", False)}

    def __repr__(self):
        return f"<Log {self.name}>"

    def __iter__(self):
        for a in ["name", "runtime", "path", "id"]:
            yield a, getattr(self, a)
        yield "available", self._available

    def available(self, stat):
        return self._available.get(stat)

    def config(self, poller=None):
        """
        Return Config object associated with log.
        """
        config_rx = re.compile(settings.regex.get("config"))
        return cache(
            Config,
            config_rx,
            self.path,
            self.client,
            self.id,
            self.name,
            poller)

    def gpl(self, poller=None):
        """
        Return GPLData of execution log.

        Note: *.gpl files become available after TitanSim has exited,
        since they are written during shutdown.
        """
        gpl_rx = re.compile(settings.regex.get("gpl"))
        gpl_path = os.path.join(self.path, "stat")
        return cache(
            GPLData,
            gpl_rx,
            gpl_path,
            self.client,
            self.id,
            self.name,
            poller)

    def status_codes(self, poller=None):
        """
        Return StatusCodeData of execution log.
        """
        status_codes_rx = re.compile(settings.regex.get("status_codes"))
        return cache(
            StatusCodeData,
            status_codes_rx,
            self.path,
            self.client,
            self.id,
            self.name,
            poller)

    def latency(self, poller=None):
        """
        Return LatencyData object of execution log.
        """
        latency_rx = re.compile(settings.regex.get("latency"))
        return cache(
            LatencyData,
            latency_rx,
            self.path,
            self.client,
            self.id,
            self.name,
            poller)

    def fetch(self, outdir, poller=None):
        raise NotImplementedError

    def cached(self):
        return cache_status(self)

    def clear_cache(self):
        return clear_cache(self)

    def cache_path(self):
        return os.path.join(
            settings.cachedir,
            str(self.client.id),
            str(self.id))
