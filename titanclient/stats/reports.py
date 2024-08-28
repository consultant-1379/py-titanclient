import tempfile

from abc import ABC, abstractmethod
from types import SimpleNamespace
from shutil import copyfile

import xlsxwriter

from ..common.util import defattr

class XLS:

    def __init__(self, stats):
        self.stats = stats.stats if hasattr(stats, "stats") else stats

    def write(self, outfile=None, summarize=False, merge=False):

        with tempfile.NamedTemporaryFile(dir="/tmp", suffix=".xls", delete=False) as tmp:
            tmpfile = tmp.name

        workbook = xlsxwriter.Workbook(tmpfile)

        if defattr(self.stats, "config"):
            config_ws = ConfigWorksheet(self.stats.config)
            config_ws.write(workbook, merge=merge)

        if defattr(self.stats, "gpl"):
            gpl_ws = GPLWorksheet(self.stats.gpl)
            gpl_ws.write(workbook, summarize=summarize, merge=merge)

        if defattr(self.stats, "latency"):
            latency_ws = LatencyWorksheet(self.stats.latency)
            latency_ws.write(workbook, merge=merge)

        if defattr(self.stats, "status_codes"):
            status_code_ws = StatusCodeWorksheet(self.stats.status_codes)
            status_code_ws.write(workbook, merge=merge)

        if defattr(self.stats, "interval"):
            interval_ws = IntervalWorksheet(self.stats.interval)
            interval_ws.write(workbook, merge=merge)

        workbook.close()

        if outfile:
            copyfile(tmpfile, outfile)
            result_file = outfile
        else:
            result_file = tmpfile


        return result_file


class Worksheet(ABC):

    def __init__(self, statsobj, title="UNKNOWN"):
        self.statsobj = statsobj
        self.formats = SimpleNamespace()
        self.title = title

    def write(self, workbook, summarize=False, merge=False):

        for fmt, v in xls.items():
            setattr(self.formats, fmt, workbook.add_format(v))

        summary = sum(self.statsobj)

        climit = 31

        if summarize and summary.summary:
            name = f"{self.title} {summary.name}"
            name = name[0:climit] if len(name) > climit else name
            worksheet = workbook.add_worksheet(name)
            self._write_headers(summary, worksheet)
            self._write_rows(summary, worksheet)

        if merge:
            name = f"{self.title} Merged({len(self.statsobj)})"
            name = name[0:climit] if len(name) > climit else name

            worksheet = workbook.add_worksheet(name)
            headers = self._write_headers(summary, worksheet)
            offset = 0
            for statsobj in sorted(self.statsobj, key=lambda o: o.name):
                offset = self._write_rows(statsobj, worksheet, offset=offset, headers=headers)
        else:
            for statsobj in self.statsobj:
                name = f"{self.title} {statsobj.name}"
                name = name[0:climit] if len(name) > climit else name
                worksheet = workbook.add_worksheet(name)
                headers = self._write_headers(statsobj, worksheet)
                self._write_rows(statsobj, worksheet, headers=headers)

    def fmt(self, value):
        if isinstance(value, float):
            return self.formats.floating
        if isinstance(value, int):
            return self.formats.integer
        if isinstance(value, str):
            return self.formats.string
        if value == None:
            return self.formats.na

    @abstractmethod
    def _write_headers(obj, worksheet):
        pass

    @abstractmethod
    def _write_rows(obj, worksheet):
        pass


class GPLWorksheet(Worksheet):

    def __init__(self, gpls):
        super().__init__(gpls, title="GPL")

    def _write_headers(self, gpl, worksheet):

        worksheet.freeze_panes(1, 1)
        worksheet.freeze_panes(2, 1)
        worksheet.merge_range(0, 0, 1, 0, "Scenario", self.formats.title)

        curr = 1
        for i, group in enumerate(gpl.groups()):
            members = gpl.members(group)
            end = curr + len(members) - 1
            fmt = self.formats.header_dark if i % 2 == 0 else self.formats.header_mid
            if len(members) == 1:
                worksheet.write(0, curr, group, fmt)
            else:
                worksheet.merge_range(0, curr, 0, end, group, fmt)

            for i, col in enumerate(members):
                worksheet.write(1, curr + i, col, self.formats.header)
            curr = end + 1

    def _write_rows(self, gpl, worksheet, offset=0, headers=None):
        scenarios = gpl.scenarios()

        if not scenarios:
            return

        longest = max(scenarios or [""], key=len)
        worksheet.set_column(0, 0, len(longest), self.formats.scenario)

        offset = offset + (3 if offset == 0 else 4)

        # summary
        overall = gpl.overall()
        worksheet.write(2 + offset, 0, "OVERALL", self.formats.scenario)

        for i, name in enumerate(gpl.stats()):
            val = overall.get(name)
            fmt = self.formats.percentage if val and "gos" in name else self.fmt(val)
            worksheet.write(2 + offset, i + 1,  val, fmt)

        # individual scenarios
        for i, row in enumerate(gpl.rows()):
            for j, value in enumerate(row):
                fmt = self.formats.scenario if j == 0 else self.fmt(value)
                worksheet.write(i + 3 + offset, j, value, fmt)

        worksheet.write(offset, 0, gpl.name)
        worksheet.set_row(offset, None, self.formats.header_log)

        return len(scenarios) + offset


class IntervalWorksheet(GPLWorksheet):

    def _write_headers(self, gpl, worksheet):
        pass

    def _write_rows(self, gpl, worksheet):
        pass


class ConfigWorksheet(Worksheet):

    def __init__(self, configs):
        super().__init__(configs, title="Config")

    def _write_headers(self, config, worksheet):

        worksheet.freeze_panes(1, 1)
        worksheet.freeze_panes(1, 1)
        worksheet.write(0, 0, "Scenario", self.formats.title)

        floating = ["rps", "rrps", "cps"]

        # header
        for i, stat in enumerate(config.stats()):
            fmt = self.formats.header_dark if i % 2 == 0 else self.formats.header_mid
            worksheet.set_column(0, i + 1, len(stat), fmt)
            worksheet.write(0, i + 1, stat, fmt)

    def _write_rows(self, config, worksheet, offset=0, headers=None):
        scenarios = config.scenarios()
        if not scenarios:
            return
        longest = max(scenarios, key=len)
        worksheet.set_column(0, 0, len(longest), self.formats.scenario)

        offset = offset + 3

        # write rows
        for i, row in enumerate(config.rows()):
            for j, value in enumerate(row):
                if isinstance(value, list):
                    value = ",".join(value)
                if j == 0:
                    fmt = self.formats.scenario
                    worksheet.write(i + 1 + offset, j, value, fmt)
                else:
                    fmt = self.fmt(value)
                    worksheet.write(i + 1 + offset, j, value, self.fmt(value))

        worksheet.write(offset - 1, 0, config.name)
        worksheet.set_row(offset - 1, None, self.formats.header_log)

        return len(scenarios) + offset


class LatencyWorksheet(Worksheet):

    def __init__(self, latencies):
        super().__init__(latencies, title="Latency")

    def _write_headers(self, latency, worksheet):
        worksheet.freeze_panes(1, 1)
        worksheet.freeze_panes(2, 1)
        worksheet.merge_range(0, 0, 1, 0, "Scenario", self.formats.title)

        start = 1
        end = len(latency.keys)
        for i, req in enumerate(latency.requests()):
            fmt = self.formats.header_dark if i % 2 == 0 else self.formats.header_mid
            worksheet.merge_range(0, start, 0, end, req, fmt)
            for j, k in enumerate(latency.keys):
                worksheet.write(1, start + j, k, self.formats.integer)
            start = end + 1
            end = start + (len(latency.keys) - 1)

    def _write_rows(self, latency, worksheet, offset=0, headers=None):
        scenarios = latency.scenarios()

        if not scenarios:
            return

        longest = max(scenarios, key=len)
        worksheet.set_column(0,0, len(longest), self.formats.scenario)

        offset = (offset or 0) + 3

        # TODO: use rows() call here
        start = 1
        end = len(latency.keys)
        for req in latency.requests():
            for i, scenario in enumerate(sorted(latency.scenarios())):
                worksheet.write(i + 2 + offset, 0, scenario, self.formats.scenario)
                values = latency.values(scenario, req)
                for j, key in enumerate(latency.keys):
                    v = values.get(key) if values else None
                    if key == "amount":
                        fmt = self.formats.integer if v else self.formats.na
                    else:
                        fmt = self.formats.floating2 if v else self.formats.na
                    worksheet.write(i + 2 + offset, start + j, v, fmt)
            start = end + 1
            end = start + (len(latency.keys) - 1)

        worksheet.write(offset, 0, latency.name)
        worksheet.set_row(offset, None, self.formats.header_log)

        return len(scenarios) + offset


class StatusCodeWorksheet(Worksheet):

    def __init__(self, status_codes):
        super().__init__(status_codes, title="Status")

    def _write_headers(self, sc, worksheet):
        worksheet.freeze_panes(1, 1)
        worksheet.freeze_panes(2, 1)
        worksheet.merge_range(0, 0, 1, 0, "Scenario", self.formats.title)

        start = 1
        headers = {}
        for i, request in enumerate(sc.requests()):
            corr = sc.correlations(request)
            end = start + len(corr) - 1
            fmt = self.formats.header_dark if i % 2 == 0 else self.formats.header_mid
            reqtext = "SIP" if request == "-" else request
            if start == end:
                worksheet.write(0, start, reqtext, fmt)
            else:
                worksheet.merge_range(0, start, 0, end, reqtext, fmt)
            for j, c in enumerate(corr):
                worksheet.write(1, start + j, c, self.formats.centered)
            start = end + 1

            headers.setdefault(request, [c for j, c in enumerate(corr)])

        return headers

    def _write_rows(self, sc, worksheet, offset=0, headers=None):
        scenarios = sc.scenarios()

        if not scenarios:
            return

        longest = max(scenarios, key=len)
        worksheet.set_column(0, 0, len(longest), self.formats.scenario)

        offset = offset + (3 if offset == 0 else 4)

        worksheet.write(2 + offset, 0, "OVERALL")

        overall = sc.overall()
        oi = 1
        for r, corrs in headers.items():
            for j, c in enumerate(corrs):
                oval = overall.get(r, {}).get(c, None)
                fmt = self.fmt(oval)
                worksheet.write(2 + offset, oi, oval, fmt)
                oi += 1

        # write rows
        for i, s in enumerate(scenarios):
            row = [s]
            for r, corrs in headers.items():
                for j, c in enumerate(corrs):
                    row += [sc.amount(s, r, c)]

            for j, value in enumerate(row):
                fmt = self.formats.scenario if j == 0 else self.fmt(value)
                worksheet.write(i + 3 + offset, j, value, fmt)

        worksheet.write(offset, 0, sc.name, self.formats.header_log)
        for i in range(1, oi):
            worksheet.write(offset, i, None, self.formats.header_log)

        return len(scenarios) + offset


xls = {
    "title": {
        "bold": 1,
        "align": "center_across",
        "border": 1,
        "bg_color": "#0051B1",
        "color": "#FFFFFF",
        "align": "center",
        "locked": 0,
        "valign": "vcenter"
    },
    "header": {
        "align": "center"
    },
    "header_dark":{
        "bold": 1,
        "align": "center",
        "border": 1,
        "bg_color": "#4797D7",
        "color": "#FFFFFF"
    },
    "header_mid": {
        "bold": 1,
        "align": "center",
        "border": 1,
        "bg_color": "#C2DBEF",
        "color": "#000000"
    },
    "header_log": {
        "bold": 1,
        "bg_color": "#C2DBEF",
        "align": "left",
    },
    "centered": {
        "align": "center",
        "locked": 0
    },
    "scenario": {
        "align": "left"
    },
    "string":{
        "align": "center"
    },
    "integer": {
        "align": "center",
        "num_format": "0"
    },
    "floating": {
        "align": "center",
        "num_format": "0.0000",
        "locked": 0
    },
    "floating2": {
        "align": "center",
        "num_format": "0.00",
        "locked": 0
    },

    "percentage": {
        "align": "center",
        "num_format": "0.000000",
        "locked": 0
    },
    "na":{
        "diag_type": 1,
        "diag_border": 1,
        "diag_color": "#D5D5D5"
    }
}
