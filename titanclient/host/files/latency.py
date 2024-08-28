import re
import os
import glob

class  LatencyData():

    def __init__(self, filename="", name=None):
        self.name = str(name)
        self._cases = {}
        if os.path.isdir(filename):
            filenames = glob.glob(os.path.join(filename, "*.txt"))
            if filenames:
                filename = filenames[0]
        else:
            filename = filename if isinstance(filename, str) else filename[0]
        sed = "sed -n '/Statistics Type: Latency - Total/,/Statistics Type/p' "
        run = "{command} {file}".format(command=sed, file=filename)
        string = os.popen(run).read()
        if string:
            # some files have a prefix for each line in the form of
            # <TypeOfStat: Latency - Total>:
            # or similar. Remove this if it's present.
            string = re.sub(r"<[^>]*>:", "", string)
            self.read(string)

    def __repr__(self):
        return f"<LatencyData {self.name}>"


    def read(self, string):
        rx = re.compile(r"[^ ] [SBIHNPR]")
        cases = string.split("Traffic Case   : ")[1:] # ignore top header
        for case in cases:
            tmp = case.split("\n", 3)
            body = tmp[3]
            case_name = tmp[0]
            match = re.finditer(rx, body)
            indices = [ m.span()[0] for m in match ]
            records = [ body[i:j].strip("\n ") for i,j in zip(indices, indices[1:]+[ None ]) ]
            self._cases[case_name] = self._parse_records(records)

    def query(self, case, requests=None):
        _case = self._cases.get(case, None)
        if not requests:
            return _case
        else:
            return dict([(req, _case.get(req)) for req in requests])

    def get_requests(self, case):
        return self._cases.get(case, {}).keys()

    def get_traffic_cases(self):
        return self._cases.keys()

    def get_keys(self):
        s = set()
        for case in self._cases:
            for req in self._cases[case].keys():
                list(map(s.add, self._cases[case][req].keys()))
        return list(sorted(s))[::-1]

    def _parse_records(self, array):
        headers = ["amount", "latency", "max", "min", "95%", "90%"]
        result = {}
        for record in array:
            items = record.split()
            # re-attach severed names
            request = items[0] + "".join(items[7:])
            try:
                rest = dict(zip(headers, map(float, items[1:7])))
                result[request] = rest
            except ValueError:
                # gulp the map(float, ...) error for non-records,
                # e.g. the "Statistics Type" matched at the end
                pass

        return result
