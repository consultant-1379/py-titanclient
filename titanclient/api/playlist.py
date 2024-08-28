""" .. include:: ../../docs/api/playlist.md """
import os
import re
import sys
import time
import yaml
import argparse
import datetime

from prettytable import PrettyTable

from ..api.client import APIClient
from ..common.logger import logger

padding = 0

class Playlist:

    """
    Control state/timing of one or multiple TitanSim using a playlist
    defined in YAML format. If `outdir` is defined and the playlist
    contains stats operations, save stats data to the designated
    directory.
    """

    def __init__(self, filepath, outdir=None, dry_run=False):
        self.playlist_path = os.path.abspath(filepath)
        self.playlist = yaml.safe_load(open(filepath, "r"))
        self.dry_run = dry_run
        self.outdir = outdir if outdir else None
        sims = self.playlist.get("simulators", [])
        steps = self.playlist.get("playlist", [])
        self._ops = []
        self._pool = []
        if sims:
            self._pool = _connect_sims(sims)
            if steps:
                global padding
                padding = len(str(len(steps)))
                self._ops = self._create_ops(steps, self._pool)

    def run(self):
        """
        Execute playlist.
        """
        sims = self.playlist.get("simulators", [])
        steps = self.playlist.get("playlist", [])
        global padding
        _pad = " " * (padding + 1)

        if not sims:
            raise Exception("No simulators defined for playlist.")

        if not self._ops:
            raise Exception("Playlist contains no steps.")

        is_dry_run = self.dry_run
        # in any case, print the Playlist contents at the top

        self.dry_run = True
        logger.info("{} playlist {}".format(_pad, self.playlist_path))

        self._execute(self._ops)
        logger.info("{} (end printout)\n\n".format(_pad))

        if not is_dry_run:
            self.dry_run = False
            logger.info("{} START".format(_pad))
            self._execute(self._ops)
            logger.info("{} FINISH".format(_pad))

    def _execute(self, ops):
        label_idx = {}
        for i, op in enumerate(ops):
            if isinstance(op, Label):
                label_idx[op.label] = i + 1
        pc = 0
        if self.dry_run:
            [op.exec(dry_run=self.dry_run) for op in ops]
        else:
            while pc < len(ops):
                op = ops[pc]
                result = op.exec(dry_run=self.dry_run)
                pc = label_idx[result] if result else pc + 1

    def _create_ops(self, steps, pool):
        ops = []
        for i, step in enumerate(steps, 1):
            op = list(step.keys())[0] if isinstance(step, dict) else step
            args = step[op] if isinstance(step, dict) else {}
            if op == "set":
                ops.append(Set(args, pool, index=i))
            elif op == "label":
                ops.append(Label(args, index=i))
                i -= 1
            elif op == "jump":
                ops.append(Jump(args, index=i))
            elif op == "jumpif":
                ops.append(JumpIf(args, pool, index=i))
            elif op == "stat":
                ops.append(Stat(args, pool, self.outdir, index=i))
            elif op == "ready":
                ops.append(Ready(args, pool, index=i))
            elif op == "wait":
                ops.append(Wait(args, pool, index=i))
            elif op == "start":
                ops.append(Start(args, pool, index=i))
            elif op == "stop":
                ops.append(Stop(args, pool, index=i))
            elif op == "reset":
                ops.append(Reset(args, pool, index=i))
            elif op == "exit":
                ops.append(Exit(args, pool, index=i))
            else:
                raise Exception("Unhandled operation:", op)
        return ops

# HELPERS

def _connect_sims(sims):
    pool = {}
    for sim in sims:
        address = sim.get("address")
        port = sim.get("port", 8080)
        client = APIClient(address, port)
        try:
            default = client.batch(["call_cps", "message_cps", "cps", "rps"])
        except Exception:
            raise ConnectionError("Couldn't connect to TitanSim at {}:{}".format(address, port))
        pool[sim["name"]] = {
            "default": default,
            "client": client
        }
    return pool

def _select_titansims(args, pool):
    try:
        if isinstance(args, str) or (not args.get("titansim") or args.get("titansim") == "all"):
            return { ts: pool[ts] for ts in pool.keys()}
        else:
            return { ts.strip(): pool[ts.strip()] for ts in args.get("titansim").split(",")}
    except Exception:
        raise Exception("Simulator not found:", args.get("titansim"))

def _poll(titansims, phase, state, timeout=300, scenario_filter=""):
    phase_ready = phase == "ready"
    ts_status = { ts: False for ts in titansims.keys() }
    ts_client = { ts: settings.get("client") for ts, settings in titansims.items() }
    expected_values = { "phase": phase, "state": state }
    value_names = list(expected_values.keys())
    start = time.time()
    while time.time() < start + timeout:
        for name, client in ts_client.items():
            if not ts_status[name]:
                result = client.ready() if phase_ready else client.batch(value_names, scenario_filter=scenario_filter)
                if not phase_ready:
                    # TODO: handle cases where the scenario has
                    # already gone beyond the expected phase/state
                    bool_list = []
                    for s in result.keys():
                        for v in value_names:
                            bool_list.append(result[s].get(v, "").lower() == expected_values[v])
                    result = all(bool_list)
                if result:
                    ts_status[name] = True
        if all([ status for ts, status in ts_status.items() ]):
            return
        time.sleep(5)

# OPS

class Label():

    def __init__(self, args, index):
        self.label = args # string
        self.idx = str(" ").rjust(padding, " ")

    def exec(self, dry_run=False):
        logger.info("{}  LABEL  {}".format(self.idx, self.label))


class Jump():

    def __init__(self, args, index):
        self.jump_to = args # string
        self.idx = str(index).rjust(padding, " ")

    def exec(self, dry_run=False):
        logger.info("{}: JUMP   {}".format(self.idx, self.jump_to))
        return None if dry_run else self.jump_to


class Op:

    def __init__(self, args, titansims, index):
        self.args = args
        self.idx = str(index).rjust(padding, " ")
        self.titansims = _select_titansims(args, titansims)
        self._scenario = args.get("scenario") if isinstance(args, dict) else None
        self._filter = "" if not self._scenario or self._scenario == "all" else self._scenario

    def exec(self):
        pass


class JumpIf(Op):

    def __init__(self, args, titansims, index):
        super().__init__(args, titansims, index)
        self.condition = args.get("cond")
        self.jump_to = args.get("to")

    def exec(self, dry_run=False):
        logger.info("{}: JUMPIF {} on {} to {}".format(self.idx, self.condition, ", ".join(list(self.titansims.keys())), self.jump_to))
        mode, value, operator, operand = self._parse_cond(self.condition)
        results = []

        if mode and not mode in ["all", "avg"]:
            raise Exception("unknown term: {}".format(mode))

        for ts, settings in self.titansims.items():
            client = settings.get("client")
            values = client.batch([value], scenario_filter=self._filter)
            results.append(self._evaluate(mode, value, values, operator, operand))

        if mode == "all":
            return self.jump_to if all(results) else None
        else:
            return self.jump_to if any(results) else None

    def _evaluate(self, mode, value, values, operator, operand):
        comp = None
        _operand = float(operand)
        if operator == "<" : comp = getattr(_operand, "__gt__")
        if operator == ">" : comp = getattr(_operand, "__lt__")
        if operator == "<=": comp = getattr(_operand, "__ge__")
        if operator == ">=": comp = getattr(_operand, "__le__")
        if operator == "==": comp = getattr(_operand, "__eq__")
        if mode == "avg":
            values = [ value_dict[value] for s, value_dict in values.items() ]
            left = sum(values) / len(values)
            return comp.__call__(left)
        else:
            result = []
            for s, value_dict in values.items():
                v = value_dict.get(value)
                if v is None: continue
                _ = comp.__call__(v)
                result.append(_)
                if mode == "all" and not _:
                    return False
            return result and any(result)

    def _parse_cond(self, string):
        cond_rx = re.compile(r"(all)?\s*([a-z_]+)\s*(<|>|<=|>=|==)\s*(\d+(\.\d+)?)")
        cond = None if not isinstance(string, str) else cond_rx.match(string)
        return cond.groups()[0:4] if cond else [ None, None, None, None ]


class Start(Op):

    def __init__(self, args, titansims, index):
        super().__init__(args, titansims, index)
        self._client_method = "start"
        self.phase = "loadgen"
        self.state = "running"
        self.timeout = self.args.get("timeout", 600)

    def exec(self, dry_run=False):

        log_message = []
        for ts, settings in self.titansims.items():
            client = settings.get("client")
            log_message.append("{} ({})".format(ts, len(client.scenarios(self._filter)) if self._filter else "all"))

        logger.info("{}: {}{}".format(self.idx, self._client_method.upper().ljust(7), ", ".join(log_message)))

        if dry_run:
            return

        for ts, settings in self.titansims.items():
            client = settings.get("client")
            if not self._filter:
                getattr(client, self._client_method + "_all")()
            else:
                client.batch(self._client_method, scenario_filter=self._filter)
        _poll(self.titansims,
              self.phase,
              self.state,
              self.timeout,
              scenario_filter=self._filter)


class Stop(Start):

    def __init__(self, args, titansims, index):
        super().__init__(args, titansims, index)
        self._client_method = "stop"
        self.phase = "preamble"
        self.state = "idle"


class Exit(Op):

    def __init__(self, args, titansims, index):
        super().__init__(args, titansims, index)

    def exec(self, dry_run=False):

        logger.info("{}: EXIT   {}".format(self.idx, ", ".join(list(self.titansims.keys()))))

        if dry_run:
            return

        for ts, settings in self.titansims.items():
            client = settings.get("client")
            client.exit()


class Ready(Op):

    def __init__(self, args, titansims, index):
        super().__init__(args, titansims, index)

    def exec(self, dry_run=False):
        logger.info("{}: READY  {}".format(self.idx, ", ".join(list(self.titansims.keys()))))

        if dry_run:
            return

        _poll(self.titansims, "ready", None)

class Stat(Op):

    def __init__(self, args, titansims, outdir, index):
        super().__init__(args, titansims, index)
        self.stats = list(map(lambda v: v.strip(), args.get("name").split(",")))
        self.outdir = outdir

    def exec(self, dry_run=False):

        def _avg(outdata, stats):
            value_dict = {}
            for ts, values in outdata.items():
                for s in stats:
                    value_dict[s] = []
                    for scen, v in outdata[ts].items():
                        if v.get(s) is not None:
                            value_dict[s].append(v.get(s))
                    if len(value_dict[s]) > 0:
                        value_dict[s] = sum(value_dict[s]) / len(value_dict[s])
                    else:
                        value_dict[s] = ""
            return value_dict

        logger.info("{}: STAT   {} ({})".format(self.idx, ", ".join(self.stats), ", ".join(list(self.titansims.keys()))))
        if dry_run: return
        outdata = {}
        table = PrettyTable()
        table.field_names = ["scenario", "simulator"] + self.stats
        table.align["scenario"] = "l"
        for ts, settings in self.titansims.items():
            client = settings.get("client")
            stats = client.batch(self.stats, scenario_filter=self._filter)
            outdata[ts] = stats
            for s in self.stats: table.align[s] = "r"
            for scenario, values in stats.items():
                table.add_row([ scenario, ts ] + list(map(lambda s: values[s] if values[s] is not None else "", self.stats)))
        logger.info("          (table)\n{}".format(table))

        avg = self.args.get("avg")
        if avg:
            average = _avg(outdata, list(map(lambda s: s.strip(), avg.split(","))))
            for key in average.keys():
                logger.info("average {}: {}".format(key, average.get(key)))

        if self.outdir:
            outfile_name = "{}_{}.yaml".format(
                datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'),
                "_".join(self.stats)
            )
            outfile_full = os.path.join(self.outdir, outfile_name)

            if not os.path.exists(self.outdir):
                os.makedirs(self.outdir, exist_ok=True)

            with open(outfile_full, "w") as file:
                file.write(yaml.dump(outdata))


class Reset(Op):

    def __init__(self, args, titansims, index):
        super().__init__(args, titansims, index)

    def exec(self, dry_run=False):
        logger.info("{}: RESET  {}".format(self.idx, ", ".join(list(self.titansims.keys()))))
        if dry_run:
            return
        for ts, settings in self.titansims.items():
            client = settings.get("client")
            client.reset()


class Wait(Op):

    def __init__(self, args, titansims, index):
        super().__init__(args, titansims, index)
        self.secs, self.time, self.name = self._parse(args) # string

    def exec(self, dry_run=False):
        logger.info("{}: WAIT   {} {}".format(self.idx, self.time, self.name))
        if dry_run: return
        time.sleep(self.secs)

    def _parse(self, string):
        time_rx = re.compile(r"^(\d+)(s|m|h|d)?$")
        is_time = time_rx.match(string)
        if is_time:
            time, unit = is_time.groups()
            multiplier = 1
            name = "second{}".format("s" if multiplier == 1 else "")
            if unit == "m":
                name = "minute{}".format("s" if multiplier == 1 else "")
                multiplier = 60
            if unit == "h":
                name = "hour{}".format("s" if multiplier == 1 else "")
                multiplier = 3600
            if unit == "d":
                name = "day{}".format("s" if multiplier == 1 else "")
                multiplier = 86400
            return int(time) * multiplier, time, name
        else:
            raise Exception("Couldn't parse time operand", string)

class Set(Op):

    def __init__(self, args, titansims, index):
        super().__init__(args, titansims, index)
        self.value_names = list(set(args) - set(["scenario", "titansim"]))

    def exec(self, dry_run=False):
        values_to_send_all = {}
        for ts, settings in self.titansims.items():
            values = {}
            client = settings.get("client")
            for s in client.scenarios(self._filter):
                for value in self.value_names:
                    if not values.get(s.name):
                        values[s.name] = {}
                    values[s.name][value] = self.args.get(value)
            # before running, ensure that current/original etc is handled properly
            values_to_send = self._resolve_values(values, settings)
            n=len(values_to_send.keys()) if self._filter else "all"
            values_to_send_all[ts] = { "length": n, "values": values_to_send }

        self._log(values_to_send_all)

        if dry_run: return

        for ts, settings in self.titansims.items():
            values = values_to_send_all[ts].get("values")
            client = settings.get("client")
            client.batch(self.value_names, values=values, scenario_filter=self._filter)

    def _log(self, values):

        ts_list = list(values.keys())
        i = 0
        for ts in ts_list:
            for value in self.value_names:
                change = self.args[value]
                ts_filter = self.args.get("titansim")
                n = values[ts]["length"]
                if i == 0:
                    i += 1
                    logger.info("{}: SET    {} to {} on {} ({} scen.)".format(self.idx, value, change, ts, n))
                else:
                    logger.info("{} to {} on {} ({} scen.)".format(value, change, ts, n))

        for ts in ts_list:
            if values[ts]["length"] == "all":
                continue
            for s in values[ts]["values"].keys():
                logger.info("{} on {}".format(s, ts))

    def _parse_expression(self, string):
        expression_rx = re.compile(r"(current|default)\s*([\*+-\/])?\s*([\d\.]*)?(%)?")
        expression = None if not isinstance(string, str) else expression_rx.match(string)
        return expression.groups() if expression else [ None, None, None, None ]

    def _resolve_values(self, values, settings):
        current = None
        client = settings.get("client")
        values_to_send = {}
        for value_name in self.value_names:
            for s in client.scenarios(self._filter):
                expression = values[s.name][value_name]
                value = expression
                if str(value).isdigit():
                    pass
                elif isinstance(value, str):
                    base, operator, operand, percentage = self._parse_expression(expression)

                    variable = base
                    if base == "current" and not current:
                        current = client.batch(["call_cps", "message_cps", "cps", "rps"])
                    _base = None
                    if (base == "current" or not base) and current:
                        _ = current.get(s.name, {}).get(value_name)
                        _base = float(_) if _ is not None else None
                    if base == "default":
                        _ = settings["default"][s.name][value_name]
                        _base = float(_) if _ is not None else None
                    if _base is None: continue

                    if _base is not None and not operator:
                        base = _base

                    if operator:

                        if not operand:
                            raise Exception("Missing operand in", value)

                        operand = float(operand)
                        pct_dec = operand / 100

                        if operator == "*":
                            value = _base * pct_dec if percentage else _base * operand
                        elif operator == "/":
                            value = _base / pct_dec if percentage else _base / operand
                        elif operator == "+":
                            value = _base + pct_dec * _base if percentage else _base + operand
                        elif operator == "-":
                            value = _base - pct_dec * _base if percentage else _base - operand
                    else:
                        value = base
                if value is not None:
                    if not values_to_send.get(s.name):
                        values_to_send[s.name] = {}
                    values_to_send[s.name][value_name] = value
        return values_to_send

__all__ = ["Playlist"]
