import os
import re
import json
import glob
import shutil
from functools import wraps
from datetime import timedelta
from types import SimpleNamespace

import click
from prettytable import PrettyTable

from ..cli.args import (
    GlobalArgumentCommand as GAC,
    NaturalOrderGroup as NOG)
from ..common.config import settings
from ..common.logger import logger
from ..host import hosts
from ..host.files.config import Config
from ..host.connection import progress_bar
from ..api.client import APIClient
from ..api.playlist import Playlist
from ..stats.collections import Values
from ..stats.statistics import Statistics, load_from_directory
from ..stats.reports import XLS


ctx = {"help_option_names": ["-h", "--help"]}
mainhelp = """
titanclient CLI interface to manage TitanSim APIs and hosts
"""

@click.group(help=mainhelp, context_settings=ctx)
def top():
    pass


@top.group(help="Elliot REST API")
def elliot():
    pass


@top.group(help="TitanSim host operations", cls=NOG)
def host():
    pass


@host.command("list", help="list configured hosts", cls=GAC)
def list_hosts(verbose):
    table = PrettyTable(["id", "shortname", "address"])
    for h in hosts.hosts():
        table.add_row([h.id, h.config.shortname, h.config.hostname])
    print(table)


@host.group(help="process TitanSim logs")
def log():
    pass


@host.command("launch", help="launch one or more TitanSims")
@click.option("-i", "--host_id", help="host ID", multiple=True)
def launch(host_ids):
    hosts.do(lambda h: h.launch(), host_ids)


@host.command("shutdown", help="shutdown one or more TitanSims")
@click.option("-i", "--host_id", help="host ID", multiple=True)
def shutdown(host_ids):
    hosts.do(lambda h: h.shutdown(), host_ids)


@host.command("status", help="show TitanSim host status")
@click.option("-i", "--host_id", "host_ids", help="host ID", multiple=True)
def status(host_ids):

    def status(hc):
        print(hc.id, hc.config.hostname, "ready" if hc.api.ready() else "down")

    hosts.do(status, host_ids)


@log.command("list", help="list logs on configured hosts", cls=GAC)
@click.option("--format", required=False, default="table",
              help="output format")
def list_logs(format, verbose):
    if format not in ["txt", "json", "table"]:
        raise ValueError(f"unrecognized format: {format}")

    logs = hosts.logs()

    if format == "txt":
        for l in logs:
            print(l.client.id,
                  l.id,
                  l.name,
                  l.runtime)

    if format == "json":
        out = []
        for l in logs:
            out.append({
                "host": str(l.client.id),
                "logid": str(l.id),
                "name": l.name,
                "runtime": l.runtime})

        print(json.dumps(out, indent=2))

    if format == "table":
        table = PrettyTable(["host", "id", "name", "runtime"])
        for l in logs:
            table.add_row([
                l.client.id,
                l.id,
                l.name,
                timedelta(seconds=l.runtime)])
        print(table)


@log.command("fetch", help="fetch log archive tar.gz", cls=GAC)
@click.argument("logs")
def fetch_logs(logs, verbose, outdir="/tmp"):
    for l in hosts.logs([], logs):
        l.fetch(outdir, poller=progress_bar)


@log.group(help="manage local execution log caches")
def cache():
    pass


@cache.command("list", help="list cached logs", cls=GAC)
def list_cache(verbose):
    for data in os.walk(os.path.expanduser(settings.cachedir)):
        for leaf in data[2]:
            if leaf.endswith(".bin"):
                print(os.path.join(data[0], leaf))


@cache.command("clear", help="clear cached logs", cls=GAC)
def clear_cache(verbose):
    shutil.rmtree(settings.cachedir)
    os.makedirs(settings.cachedir, exist_ok=True)


@top.group(help="process configuration files")
def config():
    pass


@config.command("edit", help="change configuration scenarios", cls=GAC)
@click.option("--configpath")
@click.option("--outfile")
@click.option("--filter")
def edit_config(configpath, outfile, value, filter):

    c = Config(configpath)

    if filter:
        rx = re.compile(filter)
        for s in c.scenarios():
            if not rx.search(s.name):
                c.remove(s)

    c.dump(outfile)


@log.group(help="edit/fetch configurations")
def stat():
    pass

def stat_options(func):
    @click.option("-l", "--log", "log_ids", multiple=True, required=True,
                  help="log ID (multiple)")
    @click.option("-s", "--stat", "stats", multiple=True, required=True,
                  help="stat name to dump (multiple)")
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@stat.command("config", help="dump configuration file", cls=GAC)
@stat_options
def dump_config(log_ids, stats, verbose):
    dump("config", log_ids, stats=stats)


@stat.command("gpl", help="dump GPL statistics", cls=GAC)
@stat_options
def dump_gpl(log_ids, stats, verbose):
    dump("gpl", log_ids, stats)


@stat.command("latency", help="dump latency data", cls=GAC)
@stat_options
def dump_latency(log_ids, stats, verbose):
    dump("latency", log_ids, stats)


@stat.command("status_codes", help="dump status code stats", cls=GAC)
@click.option("-l", "--log", "log_ids", multiple=True, required=True,
              help="log ID (multiple)")
def dump_status_codes(log_ids, verbose):
    dump("status_codes", log_ids)


def dump(report, log_ids, *args, **kwargs):
    logs = hosts.logs(log_ids)
    statistics = Statistics(*logs, poller=progress_bar)

    data = getattr(statistics, report)(*args, **kwargs)
    results = []

    for s in data:

        results.append({
            "log": s.log.name,
            "stat": s.type,
            "values": s._data})

    print(json.dumps(results, indent=2))


@stat.group(help="Generate reports from stats")
def report():
    pass


shared_report_options = [
    click.option("-o", "--outfile", help="output filename"),
    click.option("-s", "--summarize", is_flag=True, help="create summary worksheet"),
    click.option("-m", "--merge", is_flag=True, help="merge each log stat type on a single worksheet"),
    click.option("-c", "--config", multiple=True, help="config stats to include (multiple)"),
    click.option("-g", "--gpl", multiple=True, help="GPL stats to include (multiple)"),
    click.option("-a", "--latency", multiple=True, help="latency stats to include (multiple)"),
    click.option("-i", "--interval", help="interval for GPL stats"),
    click.option("-u", "--status_codes", is_flag=True, help="include status code info"),
    click.option("-t", "--timestamp", type=int, help="timestamp to use with GPL stats")]


def report_options(func):
    for option in reversed(shared_report_options):
        func = option(func)
    return func


@report.command(help="Generate report via execution log dir", cls=GAC)
@click.option("-d", "--directory", help="TitanSim execution log")
@report_options
def local(**kwargs):
    args = SimpleNamespace(**kwargs)
    stats = load_from_directory(args)
    xls_report = XLS(stats)
    report_file = xls_report.write(args.outfile, args.summarize, args.merge)
    logger.info(f"write file: {report_file}")
    return report_file


@report.command(help="generate XLS report via host log ID", cls=GAC)
@click.option("-l", "--log", "log_ids", multiple=True, required=True,
              help="log ID (multiple)")
@report_options
def remote(**kwargs):
    args = SimpleNamespace(**kwargs)
    logs = hosts.logs(args.log_ids)
    stats = Statistics(*logs, timestamp=args.timestamp).all(
        gpl=args.gpl,
        config=args.config,
        latency=args.latency,
        interval=args.interval,
        status_codes=args.status_codes)

    xls_report = XLS(stats)
    report_file = xls_report.write(args.outfile, args.summarize, args.merge)

    logger.info(f"write file: {report_file}")
    return report_file


@top.group(help="TitanSim DsREST API interface")
def api():
    pass


@api.command("start", help="start traffic", cls=GAC)
@click.option("-i", "--host_id", "host_ids", help="host ID", multiple=True)
def start_traffic(host_ids):
    hosts.do(lambda hc: hc.api.start_all(), host_ids)


@api.command("stop", help="stop traffic", cls=GAC)
@click.option("-i", "--host_id", "host_ids", help="host ID", multiple=True)
def stop_traffic(hostids):
    hosts.do(lambda hc: hc.api.stop_all(), host_ids)


@api.group(help="execute automated playlists")
def playlist():
    pass


@playlist.command("run", help="execute YAML playlist", cls=GAC)
def run_playlist(playlist, dry_run=False, outdir=None):
    Playlist(playlist, outdir=outdir, dry_run=dry_run).run()


@api.group(help="query and change runtime stats values")
def stats():
    pass


@stats.command("list", help="list available stats", cls=GAC)
def list_stats(verbose):
    for v in Values.TRAFFIC:
        print(v.get("name"))

@stats.command("get", help="show stat values", cls=GAC)
@click.option("-i", "--host_id", "host_ids", help="host ID", multiple=True)
@click.option("-s", "--stat", "stats", multiple=True, required=True,
              help="stat name to dump (multiple)")
def get_stats(host_ids, stats, verbose):
    data = {}
    for hc in hosts.hosts(host_ids=host_ids):
        data[hc] = hc.api.batch(stats)

    table = PrettyTable(["host id"] + sorted(stats))
    for hc, values in data.items():
        table.add_row([hc.id] + [ values.get(s) for s in sorted(stats)])

    print(table)


@stats.command("set", help="set stat values", cls=GAC)
def set_stats(verbose, json_file=None, value=None):
    raise NotImplementedError

@stats.command("reset", help="reset runtime stat counters", cls=GAC)
@click.option("-i", "--host_id", "host_ids", help="host ID", multiple=True)
def reset_stats(hostids, verbose):
    hosts.do(lambda hc: hc.api.reset(), host_ids)


if __name__ == "__main__":
    top()
