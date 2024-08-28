import os
import shutil
import pickle

from ..common.util import uuid
from ..common.logger import logger
from ..common.config import settings


def cache(
        cls,
        regex,
        remote_path,
        client=None,
        logid=None,
        name=None,
        poller=None):

    """
    Fetch files matched by `regex` in `path` and pass them as argument
    to `cls`.

    On subsequent calls, return the cached/pickled class instance from
    local cache storage until the cache is deleted.
    """

    # set up local paths
    host_uuid = str(client.id)

    host_cache_path = os.path.join(os.path.expanduser(settings.cachedir), host_uuid)
    log_cache_path = os.path.join(host_cache_path, str(logid))
    path_cache_path = os.path.join(log_cache_path, cls.__name__)

    # list remote files
    remote = client.list_dir(remote_path, regex)

    # check for changes since last pickle
    modified = []
    for attr in remote:
        local_path = os.path.join(path_cache_path, attr.filename)
        if os.path.exists(local_path):
            local_mtime = os.path.getmtime(local_path)
            if local_mtime < attr.st_mtime:
                modified.append(attr)

    # return current pickled data in case no updates were found
    pickle_path = os.path.join(path_cache_path, cls.__name__ + ".bin")

    if modified and os.path.exists(pickle_path):
        logger.debug(f"delete cache {name} (updates found)")
        os.remove(pickle_path)

    if os.path.exists(pickle_path):
        with open(pickle_path, "br") as f:
            logger.debug(f"load cache {pickle_path}")
            return pickle.load(f)

    # ensure directories
    for p in [host_cache_path, path_cache_path]:
        if not os.path.exists(p):
            logger.debug(f"make directory: {p}")
            os.makedirs(p, exist_ok=True)

    logger.debug(f"fetch {cls.__name__} of {name} on {client.config.hostname}")

    # fetch remote files
    client.ssh.fetch(
        modified or remote,
        remote_path,
        path_cache_path,
        poller=poller)

    # instantiate data class and pickle it for later
    data = cls(path_cache_path, name=name)

    with open(pickle_path, "bw") as f:
        logger.debug(f"dump cache {pickle_path}")
        pickle.dump(data, f)

    return data


def clear_cache(log):
    p = log.cache_path()
    if os.path.exists(p):
        shutil.rmtree(p)


cache_dirs = {
    "gpl": "GPLData/GPLData.bin",
    "latency": "LatencyData/LatencyData.bin",
    "status_codes": "StatusCodeData/StatusCodeData.bin",
    "config": "Config/Config.bin"}


def cache_status(log):

    def exists(path):
        return os.path.exists(os.path.join(log.cache_path(), path))

    return {n: exists(f) for n, f in cache_dirs.items()}


def cache_load(host_uuid, log_uuid, data_type):
    log_path = os.path.join(settings.cachedir, host_uuid, str(log_uuid))
    data_path = os.path.join(log_path, cache_dirs.get(data_type))

    if os.path.exists(data_path):
        with open(data_path, "br") as f:
            return pickle.load(f)
