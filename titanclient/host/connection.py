import os
import re
import sys
import time
import shutil
import pickle
import logging
import tarfile
import datetime
import threading
import subprocess

from functools import wraps
from tempfile import NamedTemporaryFile

import paramiko
from scp import SCPClient

from ..common.util import LenientNamespace
from ..common.logger import logger


def connect(
        hostname,
        username,
        password,
        port=22,
        ssh_config_file="~/.ssh/config"):

    try:
        ssh_config = paramiko.SSHConfig()
        ssh_config.parse(open(os.path.expanduser(ssh_config_file)))
        host_config = ssh_config.lookup(hostname)
        proxy = host_config.get("proxycommand")
        if proxy and port != 22:
            proxy = re.sub(":22", ":" + str(port), proxy)
    except IOError:
        proxy = None

    logger.debug(f"establish connection to {hostname}")

    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname,
              username=username,
              password=password,
              sock=paramiko.ProxyCommand(proxy) if proxy else None,
              port=port)

    return c


def autoconnect(m):
    @wraps(m)
    def arg_wrapper(self, *args, **kwargs):
        if not self.client:
            self.connect()
        return m(self, *args, **kwargs)

    return arg_wrapper


class SSHClient:

    def __init__(self, host):
        self.config = host.config
        self.client = None

    def connect(self):
        self.client = self.fresh()

    def disconnect(self):

        if not self.client:
            return

        self.client.close()
        self.client = None

    def reconnect(self):
        self.disconnect()
        self.connect()

    def fresh(self):
        return connect(
            self.config.hostname,
            self.config.username,
            self.config.password)

    @autoconnect
    def sftp(self):
        return self.client.open_sftp()

    @autoconnect
    def run(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        status = stdout.channel.recv_exit_status()
        output = stdout.read().decode("UTF-8")
        error = stderr.read().decode("UTF-8")
        return output, error, status

    @autoconnect
    def fetch(self, attrs, remote_dir, target_dir, poller=None):

        archive = NamedTemporaryFile(dir="/tmp", suffix=".tar.gz").name
        manifest = archive.replace(".tar.gz", ".manifest")

        remotes = []
        for a in attrs:
            remote_full = os.path.join(remote_dir, a.filename)
            remotes.append(remote_full)

        with open(manifest, "w") as local:
            local.write("\n".join(remotes))

        # tarball remote files and transfer them
        tar_czf = f"tar czf {archive} --files-from {manifest}"
        sftp = self.sftp()
        sftp.put(manifest, os.path.join("/tmp", manifest))

        self.run(tar_czf)
        local_tar = os.path.join(target_dir, os.path.basename(archive))

        transfer = FileTransfer(self, archive, target_dir)
        transfer.start(poller=poller)

        self.run(f"rm {archive} {manifest}")

        fetched = []

        # strip the remote directory path from files
        tar = tarfile.open(local_tar)
        for member in tar.getmembers():
            if member.isreg():
                member.name = os.path.basename(member.name)
                tar.extract(member, path=target_dir)
                fetched.append(os.path.join(target_dir, member.name))

        subprocess.check_output(["rm", local_tar, manifest])

        return fetched



class FileTransfer:

    def __init__(
            self,
            client,
            filename,
            target_dir):

        self.client = client
        self.filename = filename
        self.target_dir = target_dir

        self.files = {}

        self.start_date = None
        self.end_date = None

        self.poller = None
        self.period = 0.1
        self.last = time.time()

    def __repr__(self):
        return f"<FileTransfer {self.filename}>"

    def start(self, poller=None):
        logger.debug(f"fresh SSH session to transfer {self.filename}")

        if poller:
            logger.debug(f"set poller: {poller.__name__}")
            self.poller = poller

        ssh = self.client.fresh()
        c = SCPClient(ssh.get_transport(), progress=self.poll)

        c.get(self.filename, self.target_dir)
        self.end_date = datetime.datetime.now()
        ssh.close()

    def status(self):
        size = sum([d.get("size") for d in self.files.values()])
        copied = sum([d.get("copied") for d in self.files.values()])
        return {"size": size,
                "copied": copied,
                "files": len(self.files.keys())}

    def poll(self, name, size, copied):

        if self.end_date:
            logger.debug(f"fetch complete: {self.filename}")
            return

        if not self.files:
            self.start_date = datetime.datetime.now()

        self.files.setdefault(name, {})
        self.files[name] = {
            "size": size,
            "copied": copied,
            "finished": size == copied}

        all_finished = [d.get("finished") for d in self.files.values()]
        if all(all_finished):
            self.end_date = datetime.datetime.now()

        tick = time.time()
        if tick - self.last > self.period:
            self.last = tick
            if self.poller:
                self.poller(self)



def progress_bar(t):
    status = t.status()
    multiple_files = status.get("files", 0) > 1
    timestamp = (t.start_date or datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    prefix = f"[{timestamp}] "
    prefix += f"fetch {status.get('files')} files:" if multiple_files else f"fetch {t.filename}:"

    if t.start_date and t.end_date:
        elapsed = t.end_date - t.start_date
    elif t.start_date:
        elapsed = datetime.datetime.now() - t.start_date
    else:
        elapsed = "??:??:??.?"

    main, decimal = str(elapsed).split(".")

    print_progress(
        status.get("copied"),
        status.get("size"),
        prefix=prefix,
        elapsed=f"{main}.{decimal[0:1]}")

    if t.end_date:
        print("\n")


# https://stackoverflow.com/a/34325723
def print_progress(
        iteration,
        total,
        prefix='',
        decimals=1,
        length=None,
        elapsed=None,
        fill='█',
        printEnd="\r"):

    ratio = f"{iteration}/{total}"

    if not length:
        columns = shutil.get_terminal_size((80, 20)).columns
        length = columns - (len(prefix) + len(ratio) + len(str(elapsed)) + 12)
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)

    print(f"\r{prefix} |{bar}| {ratio} {percent}% {elapsed}", end=printEnd)
