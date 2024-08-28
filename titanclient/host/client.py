""" .. include:: ../../docs/host/host.md """

import os
import re
import time
from datetime import datetime

from ..common.util import retry, uuid, LenientNamespace
from ..host.log import Log
from ..host.connection import SSHClient
from ..api.client import APIClient


class HostClient:

    def __init__(
            self,
            hostname=None,
            port=8080,
            username=None,
            password=None,
            install_dir=None,
            config_path=None,
            pm_path=None,
            config={},
            client=None):

        self.config = LenientNamespace(
            hostname = config.get("hostname", hostname),
            username = config.get("username", username),
            password = config.get("password", password),
            port = config.get("port", port),
            install_dir = config.get("install_dir", install_dir),
            config_file = config.get("config_file", config_path),
            pm_path = config.get("pm_path", pm_path))

        self.config.shortname = self.make_shortname()
        self.id = uuid(self.config.hostname + self.config.shortname)

        self.api = APIClient(self.config.hostname, self.config.port)
        self.ssh = client or SSHClient(self)


    def __repr__(self):
        return f"<HostClient {self.config.hostname}>"

    def disconnect(self):
        if not self.ssh:
            return

        self.ssh.disconnect()
        self.ssh = None

    def connect(self):
        self.ssh = SSHClient(self)

    def clone(self):
        return HostClient(config=vars(self.config))

    def list_dir(self, path, regex=".*"):
        sftp = self.ssh.sftp()
        files = []
        for attr in sftp.listdir_attr(path):
            if re.match(regex, attr.filename):
                files.append(attr)

        return files

    def make_shortname(self):
        lastoctet = self.config.hostname.split(".")[-1]
        return f"ts{lastoctet}"

    def launch(self, retries=10, modes=[], logid=None, sudo=True):

        @retry(n=retries, callback=lambda v: v is not None)
        def _launch():

            if self.api.ping():
                log = self.current()
                return log, "running"

            logfmt = f"%Y%m%d_%H%M%S_{self.config.shortname}"
            _logid = logid or datetime.strftime(datetime.now(), logfmt)
            logdir = f"{self.config.install_dir}/log/{_logid}"

            switch = "p" if self.config.config_file.endswith("prj") else "c"
            launch = (
                f"{'sudo' if sudo else ''} "
                f"{self.config.install_dir}/run.bash "
                f" -R{switch} {self.config.config_file} "
                f" -m {','.join(modes)} "
                f" -n {_logid} > {logdir}.console.log 2>&1 &")

            stdout, stderr, status = self.ssh.run(launch)

            if status:
                print("launch failed:", stderr, file=sys.stderr)
                return

            time.sleep(10)

            stdout, stderr, status = self.ssh.run("pgrep -l mctr_cli")

            if status == 0:
                resp = None
                for _ in range(0, 20):
                    if self.api.ping():
                        return self.current(), "started"
                    else:
                        time.sleep(10)

        return _launch()
        #self.start_stats(modes, logdir)

    def start_stats(self, modes, logdir):

        config_filename = os.path.basename(self.config.config_file)

        getstat_cmd = (
            f"{self.config.install_dir}/tools/util/getStatOverview.py "
            f"--dir {self.config.install_dir}/build "
            f"--resultFile {logdir}/{config_filename}_{{mode}}.stat "
            f"-c {self.config.config_file} "
            f"--mode {{mode}} --waitForStatFiles --repeat 0 > /tmp/{{mode}}.log 2>&1 &")

        ev_cmd = (
            f"bash -c 'rmdir {logdir}/evsPerVerdictType {logdir}/latencyData; sleep 10;"
            f"nohup netcat -d localhost 8100"
            f" | {self.config.install_dir}/tools/util/EVpreprocessor -R -d {logdir} -f {self.config.config_file}"
            f" | {self.config.install_dir}/tools/util/EventVectorAnalyzer.pl -r {logdir}/{config_filename}.evs.txt -l {logdir}/latencyData > /tmp/ev.tmp 2>&1 & ' ")

        for m in modes:
            self.ssh.run(getstat_cmd.format(mode=m))
            self.ssh.run(ev_cmd)

    def stop_stats(self):
        self.ssh.run("pkill -9 -f getStatOverview")
        self.ssh.run("pkill -9 -f netcat")

    def shutdown(self, poll_period=30, poll_n=10, timeout=900):

        def wait_to_kill_mctr():

            end = time.time() + timeout
            while time.time() < end:
                out, err, status = self.ssh.run("pgrep mctr_cli")

                if status != 0:
                    return

                time.sleep(poll_period)

            self.ssh.run("pkill -f mctr_cli")

        self.api.exit()

        for _ in range(0, poll_n):
            try:
                ready = self.api.ready()
            except Exception:
                ready = False
            if ready:
                client.exit()
                time.sleep(poll_period)
            else:
                self.stop_stats()
                break

        wait_to_kill_mctr()

    def logs(self):
        """
        Return a list of Log objects representing the executions
        found in the install directory on the Host.
        """

        # use single quotes to prevent evaluation of shell code
        log_path = f"{self.config.install_dir}/log/"

        find_log = (
            f"find '{log_path}' -maxdepth 1 -type d -printf \"%p\\n\" | "
            f"xargs stat -c \"%n %Y\"")

        find_cfg = (
            f"find '{log_path}'*/ -name '*.cfg' -type f -printf \"%p\\n\" | "
            f"xargs stat -c \"%n %Y\"")

        find_txt = (
            f"find '{log_path}'*/ -name stat -type d;"
            f"find '{log_path}'*/ -name '*.evs.ec.csv' -type f;"
            f"find '{log_path}'*/ -name '*.evs.txt' -type f;")

        log_out, log_err, log_status = self.ssh.run(find_log)
        cfg_out, cfg_err, cfg_status = self.ssh.run(find_cfg)
        txt_out, txt_err, txt_status = self.ssh.run(find_txt)

        data_available = {}
        path = None

        for line in txt_out.strip("\n").split("\n"):

            if not line.strip():
                continue

            path, txt = line.rsplit("/", 1)
            data_available[path] = data_available.get(path, {})
            data = None

            if txt == "stat":
                data = "gpl"
            if txt.endswith("ec.csv"):
                data = "status_codes"
            if txt.endswith("evs.txt"):
                data = "latency"

            if data:
                data_available[path][data] = True
            else:
                data_available[path][data] = False

            data_available[path]["config"] = True

        logs = []
        logs_list = log_out.strip("\n").split("\n")[1:]

        for log in logs_list:
            log_path, log_age = log.split(" ")
            i = cfg_out.find(log_path)
            j = cfg_out.find(" ", i)
            cfg_age = cfg_out[j:j+11] if i >= 0 and j >= 0 else log_age
            logs.append(
                Log(path=log_path,
                    runtime=int(log_age) - int(cfg_age),
                    available=data_available.get(log_path, {}),
                    client=self))

        return sorted(logs, key=lambda i: i.name)

    def current(self):
        """
        Return a TitanSimLog object associated with the currently running
        execution.
        """
        command = (
            "ps aux                       |"
            "grep run.bash                |"
            "grep -v grep                 |"
            "grep -shoP '(?<=\-n )[^\s]+' |"
            "uniq")

        out, err, status = self.ssh.run(command)
        name = out.strip("\n")
        if status == 0:
            for log in self.logs():
                if name == log.name:
                    return log

    def pm(self):
        raise NotImplementedError()
