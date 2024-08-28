import os
import csv
import glob

class StatusCodeData:

    def __init__(self, csv_file, name=None):
        self.stats = dict()
        self.name = str(name)
        if os.path.isdir(csv_file):
            filenames = glob.glob(os.path.join(csv_file, "*.csv"))
            if filenames:
                csv_file = filenames[0]
        else:
            csv_file = csv_file[0] if isinstance(csv_file, list) else csv_file
        with open(csv_file, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=";")
            self.headers = next(reader)
            for row in reader:
                case, request, direction, message, correlated, amount = row[0:-1]
                if not self.stats.get(case):
                    self.stats[case] = {}
                if not self.stats[case].get(correlated):
                    self.stats[case][correlated] = {}
                prev_val = self.stats[case][correlated].get(request)
                amount = int(amount)
                self.stats[case][correlated].update({
                    request: (prev_val + amount) if prev_val else amount
                })

    def __repr__(self):
        return f"<StatusCodeData {self.name}>"

    def get_traffic_cases(self):
        return self.stats.keys()

    def get_correlations(self,  request):
        result = set()
        for case, value in self.stats.items():
            statuses = self.get_statuses(case, request)
            list(map(result.add, statuses))
        return sorted(list(result))

    def get_requests(self, case=None):
        if not case:
            requests = [ self.get_requests(case) for case in self.get_traffic_cases()]
            return list(set([item for sublist in requests for item in sublist]))
        else:
            return self.stats.get(case, {}).keys()

    def get_statuses(self, case, request):
        return list(self.stats.get(case, {}).get(request, {}))

    def get_amount(self, case, request, response):
        return self.stats.get(case, {}).get(request, {}).get(response, None)
