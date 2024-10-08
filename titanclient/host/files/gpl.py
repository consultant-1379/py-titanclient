import os
import re
import glob
import json
import math

from types import SimpleNamespace
from datetime import datetime, timedelta
from bisect import bisect_left, bisect_right

class GPLData:
    """
    Load and query a set of *.gpl statistics files generated by a TitanSim
    execution. Provide both aggregate and timeline statistics.

    """

    def __init__(self, pathname=None, regex=None, name=None, connection=None):
        self.name = name if name else ""
        self.stats = dict()

        if not pathname:
            return

        if os.path.isdir(pathname):
            files = glob.glob(os.path.join(pathname, "*.gpl"))
            list(map(self.load, files)) # CPU-bound
        elif pathname and os.path.exists(pathname):
            self.load(pathname)

    def __repr__(self):
        return f"<GPLData {self.name}>"

    def load(self, pathname, fmt="gpl"):
        """
        Load and parse *.gpl file at `pathname'.
        """
        try:
            with open(pathname, "r") as file:
                self.read(file.read())
        except IOError as error:
            raise error

    def read(self, string):
        """
        Take a gpl string and read all records and header sets.
        """
        self.stats.update(self._read(string))

    def _read(self, string):
        header_groups = []
        header_columns = []
        record_indices = []
        timestamps = []
        records = []

        value_group = string.rstrip("\n").split("#ValueHeader")
        # return if no capture groups/value header lines are found
        if not value_group[1:]:
            return {}

        date_format = "%Y-%m-%d-%H:%M:%S.%f"
        case_name = re.findall("#CaptureGroup\[\"(.+)\"\]", value_group[0])[0]
        date_string = re.findall("#TimeStampBase: ([^ ]+)", value_group[0])[0]
        origin = datetime.strptime(date_string, date_format)

        column_rx = re.compile(
            "(SIP|MLSimPlus|registration|subscribe|call(Orig|Term)|(?<=[\._])call|"
            "conferenceCreator|message(Orig|Term)|xcap|publish).*")

        def strip_case_name(column_name):
            match = re.search(column_rx, column_name)
            if not match:
                print(column_name)
            from_i, to_i = match.span()
            return column_name[from_i:]

        for i, group in enumerate(value_group[1:]):
            lines = group.rstrip("\n").splitlines()
            # strip the case name from the beginning of the columns so
            # that the header columns and the record values line up.
            # Exclude the '&ValueHeader[".*"]' first column.
            headers = list(map(strip_case_name, lines[0].rstrip(" ").split()[1:]))
            header_groups.append(headers)
            header_columns.append(dict(zip(headers, list(range(len(headers))))))
            # records
            for line in lines[1:]:
                if not line.startswith("#"):
                    # ww split the first two fields (name and
                    # timedelta) only, for searching,
                    row = line.rstrip(" ").split(" ", 2)
                    elapsed = float(row[1])
                    timestamp = origin + timedelta(seconds=elapsed)
                    record_indices_tuple = (i, len(records))
                    # row[2] is a long string of all the remaining
                    # fields, split on-demand in e.g. _get.
                    records.append(row[2])
                    record_indices.append(record_indices_tuple)
                    timestamps.append(timestamp.timestamp())

        result = {
            case_name: {
                # First. the header groups: For each header group,
                # (the "#ValueHeader" lines), store an array.
                "header_groups": header_groups,
                # a dict of column name: column index paris is stored
                # for each set of headers for faster lookup or
                # traversal. The dict length should equal the number
                # of columns in associated records.
                "header_columns": header_columns,
                # records are associated with a header group. For each
                # record, store a tuple (<group index>, <record
                # index>), the first being the set of headers and the
                # second the record itself.
                "record_indices": record_indices,
                # store a timestamp for each record. Used to bisect
                # and search the records.
                "timestamps": timestamps,
                # Store record array
                "records": records
            }
        }
        return result

    # INTERFACE TO THE GPL DATA

    def get_traffic_cases(self):
        return self.stats.keys()

    # The same value goes by many different aliases in these gpl files
    # (also see comments in in _get()), and we don't want this
    # proliferation of names to extend to clients or intrude on the
    # naming convention. We stick to our own, but it remains to be
    # seen if this is just compounding the issue.

    # REGISTRATION

    def registration_total(self, case, timestamp=None):
        return self._get(case, ["registration.nofTotal"], timestamp)

    def registration_success(self, case, timestamp=None):
        return self._get(case, ["registration.nofSucc"], timestamp)

    def registration_failed(self, case, timestamp=None):
        return self._get(case, ["registration.nofUnsucc"], timestamp)

    def registration_retry(self, case, timestamp=None):
        return self._get(case, ["registration.nofRetryAfter"], timestamp)

    def registration_gos(self, case, timestamp=None):
        return self._get(case, ["registration.gos"], timestamp, cast=gos)

    def registration_gos_excluding_retry(self, case, timestamp=None):
        return self._get(case, ["registration.gosExclRetry"], timestamp, cast=gos)

    def rps(self, case, timestamp=None):
        return self._get(case, ["registration.stat.rps"], timestamp, cast=cps)

    def registration_trps(self, case, timestamp=None):
        return self._get(case, ["registration.trPerSec"], timestamp, cast=cps)

    # SUBSCRIBE

    def subscribe_total(self, case, timestamp=None):
        return self._get(case, ["subscribe.nofTotal"], timestamp)

    def subscribe_success(self, case, timestamp=None):
        return self._get(case, ["subscribe.nofTotalSucc"], timestamp)

    def subscribe_failed(self, case, timestamp=None):
        return self._get(case, ["subscribe.nofTotalUnsucc"], timestamp)

    def subscribe_gos(self, case, timestamp=None):
        return self._get(case, ["subscribe.gosTotal"], timestamp, cast=gos)

    # SIP

    def sip_outgoing_bye (self, case, timestamp=None):
        return self._get(case, ["SIP_nofOutBYE"], timestamp)

    def sip_outgoing_retransmitted_bye (self, case, timestamp=None):
        return self._get(case, ["SIP_nofOutRetransBYE"], timestamp)

    def sip_incoming_bye (self, case, timestamp=None):
        return self._get(case, ["SIP_nofIncBYE"], timestamp)

    def sip_outgoing_invite (self, case, timestamp=None):
        return self._get(case, ["SIP_nofOutINVITE"], timestamp)

    def sip_outgoing_retransmitted_invite (self, case, timestamp=None):
        return self._get(case, ["SIP_nofOutRetransINVITE"], timestamp)

    def sip_incoming_invite (self, case, timestamp=None):
        return self._get(case, ["SIP_nofIncINVITE"], timestamp)

    def sip_outgoing_register (self, case, timestamp=None):
        return self._get(case, ["SIP_nofOutREGISTER"], timestamp)

    def sip_outgoing_retransmitted_bye (self, case, timestamp=None):
        return self._get(case, ["SIP_nofOutRetransREGISTER"], timestamp)

    # MEDIA

    def media_total(self, case, timestamp=None):
        return self._get(case, ["MLSimPlus.nrOfSessions"], timestamp)

    def media_success(self, case, timestamp=None):
        return self._get(case, ["MLSimPlus.nrOfSuccessful"], timestamp)

    def media_failed(self, case, timestamp=None):
        return self._get(case, ["MLSimPlus.nrOfUnsuccessful"], timestamp)

    def media_unknown(self, case, timestamp=None):
        return self._get(case, ["MLSimPlus.nrOfInconclusive"], timestamp)

    def media_dropped(self, case, timestamp=None):
        return self._get(case, ["MLSimPlus.nrOfDropped"], timestamp)

    def media_error (self, case, timestamp=None):
        return self._get(case, ["MLSimPlus.nrOfRecError"], timestamp)

    def media_packets_sent (self, case, timestamp=None):
        return self._get(case, ["MLSimPlus.nrOfSentPackets"], timestamp)

    def media_packets_received (self, case, timestamp=None):
        return self._get(case, ["MLSimPlus.nrOfReceivedPackets"], timestamp)

    def media_packets_lost (self, case, timestamp=None):
        return self._get(case, ["MLSimPlus.nrOfLostPackets"], timestamp)

    def media_packets_duplicated (self, case, timestamp=None):
        return self._get(case, ["MLSimPlus.nrOfDuplicatedPackets"], timestamp)

    def media_packets_late (self, case, timestamp=None):
        return self._get(case, ["MLSimPlus.nrOfLatePackets"], timestamp)

    def media_packets_reordered (self, case, timestamp=None):
        return self._get(case, ["MLSimPlus.nrOfReorderedPackets"], timestamp, cast=quoted_float)

    def media_latency_95 (self, case, timestamp=None):
        return self._get(case, ["MLSimPlus.latency95PCT"], timestamp, cast=quoted_float)

    # XCAP

    def xcap_put_gos(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPutGoS"], timestamp, cast=gos)

    def xcap_put_sent(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPutSent"], timestamp)

    def xcap_put_success(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPutOk"], timestamp)

    def xcap_put_failed(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPutNOk"], timestamp)

    def xcap_put_timeout (self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPutTimeout"], timestamp)

    def xcap_get_gos(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPGetGoS"], timestamp, cast=gos)

    def xcap_get_sent(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPGetSent"], timestamp)

    def xcap_get_success(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPGetOk"], timestamp)

    def xcap_get_failed(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPGetNOk"], timestamp)

    def xcap_get_timeout(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPGetTimeout"], timestamp)

    def xcap_delete_gos(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPDeleteGoS"], timestamp, cast=gos)

    def xcap_delete_sent(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPDeleteSent"], timestamp)

    def xcap_delete_success (self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPDeleteOk"], timestamp)

    def xcap_delete_failed (self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPDeleteNOk"], timestamp)

    def xcap_delete_timeout (self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPDeleteTimeout"], timestamp)

    def xcap_post_create_gos(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPostCreateGoS"], timestamp, cast=gos)

    def xcap_post_create_sent (self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPostCreateSent"], timestamp)

    def xcap_post_create_success (self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPostCreateOk"], timestamp)

    def xcap_post_create_failed (self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPostCreateNOk"], timestamp)

    def xcap_post_create_timeout (self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPostCreateTimeout"], timestamp)

    def xcap_post_delete_gos(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPostDeleteGoS"], timestamp, cast=gos)

    def xcap_post_delete_sent (self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPostDeleteSent"], timestamp)

    def xcap_post_delete_success (self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPostDeleteOk"], timestamp)

    def xcap_post_delete_failed (self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPostDeleteNOk"], timestamp)

    def xcap_post_delete_timeout (self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPPostDeleteTimeout"], timestamp)

    def xcap_all_gos(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPAllGoS"], timestamp, cast=gos)

    def xcap_all_sent(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPAllSent"], timestamp)

    def xcap_all_success(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPAllOk"], timestamp)

    def xcap_all_failed(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPAllNOk"], timestamp)

    def xcap_all_timeout(self, case, timestamp=None):
        return self._get(case, ["xcap.nrOfXCAPAllTimeout"], timestamp)

    # CALL


    def call_cps(self, case, timestamp=None):
        return self._get(case, [ "callOrig.stat.cps", "conferenceCreator.stat.cps"], timestamp, cast=cps)

    def call_total(self, case, timestamp=None):
        return self._get(case, [ "callTerm.nofTotal", "callOrig.nofTotal", "conferenceCreator.nofTotal"], timestamp)

    def call_success(self, case, timestamp=None):
        return self._get(case, ["callTerm.nofSucc", "callOrig.nofSucc", "conferenceCreator.nofSucc"], timestamp)

    def call_failed(self, case, timestamp=None):
        return self._get(case, [ "callTerm.nofUnsucc", "callOrig.nofUnsucc", "conferenceCreator.nofUnsucc",], timestamp)

    def call_retry(self, case, timestamp=None):
        return self._get(case, ["callTerm.nofRetryAfter", "callOrig.nofRetryAfter", "conferenceCreator.nofRetryAfter"], timestamp)

    def call_gos(self, case, timestamp=None):
        return self._get(case, ["callTerm.gos", "callOrig.gos", "conferenceCreator.gos"], timestamp, cast=gos)

    def call_gos_excluding_retry(self, case, timestamp=None):
        return self._get(case, [
            "callTerm.gosExclRetry",
            "callOrig.gosExclRetry",
            "conferenceCreator.gosExclRetry"
        ], timestamp, cast=gos)

    # SMS

    def message_cps(self, case, timestamp=None):
        return self._get(case, [ "messageOrig.trPerSec"], timestamp, cast=cps)

    def message_total(self,  case, timestamp=None):
        return self.message_sent(case, timestamp=None) or self.message_received(case, timestamp=None)

    def message_sent(self, case, timestamp=None):
        return self._get(case, [ "messageOrig.nofSentMessage", "messageTerm.nofSentMessage"], timestamp)

    def message_received(self, case, timestamp=None):
        return self._get(case, [ "messageOrig.nofReceivedMessage", "messageTerm.nofReceivedMessage"], timestamp)

    def message_success(self, case, timestamp=None):
        return self._get(case, [ "messageOrig.nofSucc", "messageTerm.nofSucc"], timestamp)

    def message_failed(self, case, timestamp=None):
        return self._get(case, [ "messageOrig.nofUnsucc", "messageTerm.nofUnsucc"], timestamp)

    def message_retry(self, case, timestamp=None):
        return self._get(case, [ "messageOrig.nofRetryAfter", "messageTerm.nofRetryAfter"], timestamp)

    def message_gos(self, case, timestamp=None):
        return self._get(case, [ "messageOrig.gos", "messageTerm.gos"], timestamp, cast=gos)

    # QUERY STATISTICS

    def query(self, cases=None, fields=None, start=None, end=None, rate=20):
        """Query the `start'-`end' range of the statistics for `rate'
        samples. Filter for fields (required) and for cases (optional).
        """
        
        data = {
            "rate": rate,
            "from":start,
            "to": end,
            "items": []}
        
        if not fields:
            return data
        for case in cases if cases else self.get_traffic_cases():
            try:
                si, ei = timeline_range(self.stats[case]["timestamps"], start, end)
                if start or end:
                    if not si and not ei:
                        continue
                sample = sample_indices(self.stats[case]["timestamps"], si, ei, rate)
                timestamps = sample["values"]
                _values = []
                for ts in timestamps:
                    data_point = { "timestamp": int(ts) }
                    for field in fields:
                        method = getattr(self, field)
                        data_point[field] = method(case, ts)
                    _values.append(data_point)
                data["items"].append({
                    "scenario": case,
                    "data": _values
                })
            except KeyError as error:
                print("No GPL stats for case", case)
        return data

    # INTERNAL

    def _get(self, case, names, timestamp, cast=int):
        """
        Fetch value at 'timestamp' under the first name that is found from
        `names'. Convert the value using the function parameter
        `cast'.
        """
        # Find index for timestamp parameter or default to the tail
        if timestamp is not None:
            timeline = self.stats[case]["timestamps"]
            index = find_timestamp(timeline, timestamp)
            if len(timeline) <= index:
                index = len(timeline) - 1
        else:
            index = -1
        result = None

        _case = self.stats.get(case)
        if not _case:
            return
        header_idx, record_idx = _case["record_indices"][index]
        if not record_idx:
            return
        # previous implementation: "... as they may contain escaped
        # fields e.g. "MLSim R10A", so they cannot be parsed using
        # split...". A cursory grep did not hit any spaces within
        # double quotes in Capture Version 2.2, but who knows?
        record = self.stats[case]["records"][record_idx].split()
        # names are passed in an array, and the reason is as discussed
        # above the API calls: the same thing goes by different names
        # in various files according to scenario type or worse,
        # capture version. The previous implementation accrued an
        # ever-growing list of special cases for the column names. It
        # is useful support this "buildup" of legacy names to past-
        # and future-proof things, but we should use the names
        # themselves for value retrieval only, and certainly not
        # publicly.  So, we use a priority list for the names -- as
        # soon as we get one with a value, we grab that and return.
        for name in names:
            column_idx = self.stats[case]["header_columns"][header_idx].get(name)
            if column_idx is not None:
                result = record[column_idx]
                return cast(result)

def gos(string):
    gos_rx = re.compile("^\[led:(green|red)\](.*)$")
    return float(re.findall(gos_rx, string)[0][1])

def cps(string):
    return float(string) if string else None

def quoted_float(string):
    return float(string.strip("\"s"))

def sample_indices(items, start=None, end=None, rate=20):
    samples = {
        "values": [],
        "indices": []
    }
    range_start = start if start else 0
    range_end = (end if end else len(items)) - 1
    items_range = items[range_start:range_end]
    if not items or not items_range:
        return samples

    items_length = len(items_range)
    quotient = items_length / rate
    step = math.ceil(quotient)

    if items_length < rate:
        samples["values"] = items_range
        samples["indices"] = list(range(range_start, range_end))
        return samples

    for i, item in enumerate(items_range[::step]):
        offset = (i * step)
        result_index = range_start + offset
        if result_index > range_end:
            return samples
        else:
            samples["indices"].append(result_index)
            samples["values"].append(item)

    if samples["indices"][-1] > range_end:
        samples["indices"][-1] = range_end
        samples["values"][-1] = items_range[range_end]
    elif samples["indices"][-1] != range_end:
        samples["indices"] += [ range_end ]
        try:
            samples["values"]  += [ items[range_end] ]
        except IndexError as error:
            print("last index", range_end, "was dropped.")

    return samples

def find_timestamp(timeline, timestamp=0):
    return bisect_left(timeline, timestamp)

def timeline_range(timeline, start=None, end=None):
    # first, check a few unusual cases: a range falls outside of a
    # timeline's minimum values or start and end are swapped.
    if start and end and start > end:
        raise ValueError("Range start is bigger than range end!")
    if (start and float(start) and start > timeline[-1]) or (end and float(end) and end < timeline[0]):
        print("No value in range", start, end)
        return None, None
    # go ahead and search
    start_index = bisect_left(timeline, start or timeline[0])
    end_index = bisect_right(timeline, end or timeline[-1])
    return start_index, end_index

def round_timestamp(timestamp, up=False):
    date = datetime.fromtimestamp(int(timestamp))
    add = 60 - date.second if up else - date.second
    date = date + timedelta(seconds=add)
    return datetime.timestamp(date)
