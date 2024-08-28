""" .. include:: ../../docs/api/client.md """

import re
from typing import Union
from inspect import signature
from contextlib import suppress
from functools import wraps

import requests

import tagexpressions

from ..api.dsrequest import (
    DsRequest,
    deferable,
    only,
    helpers)


class APIClient:

    """
    DsREST API client.
    """

    def  __init__(
            self,
            ip: str,
            port: int = 8080):

        self.ip = ip
        "DSRest API address"
        self.port = port
        "DsREST API port"
        self.url = f"http://{ip}:{port}/api.dsapi"
        "DsREST API endpoint URL"

        self._scenarios = []
        self._fetched = False

    def __repr__(self):
        return f"<APIClient {self.ip}:{self.port}>"

    def ping(self):
        """
        Test DsREST API endpoint for availability
        """
        try:
            resp = requests.get(self.url)
            if resp and resp.status_code == 200:
                return True
        except:
            return False

    def _fetch(self):
        """
        Fetch scenario data and add Scenario objects into instance.
        """

        # try to load any scenario tags

        tags = DsRequest("Setup", "tCName", url=self.url)
        tags_child = DsRequest("Setup", "tags")
        tags_child.param("tCIDx", "%Parent0::idx%")
        tags.child(tags_child)

        resp = tags.send()

        tags = {}

        with suppress(Exception):
            for tc in resp[0]:
                tags[tc["tCName"]] = [t["tags"] for t in (tc["children"][0] or [])]

        # fetch scenario data

        eg = DsRequest("ExecCtrl", "EntityGroups", key="entity_group", url=self.url)
        sc = DsRequest("ExecCtrl", "Scenarios", key="scenario")
        sc.param("EntityGroup", 0)
        gr = DsRequest("ExecCtrl", "ScGroupOfSc", key="group")
        gr.param("EntityGroup", 0)
        gr.param("Scenario", 1)
        tc = DsRequest("ExecCtrl", "TrafficCases", key="traffic_case")
        tc.param("EntityGroup", 0)
        tc.param("Scenario", 1)
        eg.child(sc.child(tc).child(gr))

        resp = eg.send()

        if not resp[0:]:
            return

        # add scenarios to instance

        for eg in resp[0]:

            entity_group = eg["entity_group"]
            group = eg["children"][0][0]["children"][1]["group"]
            scenario = eg["children"][0][0]["scenario"]
            traffic_case = []

            for tc in eg["children"][0][0]["children"][0]:
                traffic_case.append(tc["traffic_case"])

            self._scenarios.append(Scenario(
                entity_group,
                group,
                scenario,
                traffic_case,
                tags.get(scenario),
                url=self.url))


    @deferable
    def batch(self,
              stats: Union[str, list],
              values: dict = None,
              name_filter: str = "",
              tag_filter: str = ""):
        """
        Return values associated with `stats`. Return values for those
        scenarios that match `name_filter` or `tag_filter` only. `batch`
        rolls each scenario request into one for a significant speedup.

        # Request stats:

        ``` python
        >>> client.batch(\"call_cps\")
        {'0010PsPs_A': {'call_cps': 4.23156}, '0010PsPs_B': {'call_cps': None}, ... }
        ```

        # Deferred calls

        `batch` requests can be deferred to be sent repeatedly:

        ``` python
        >>> client.batch(\"total\", defer=True)
        <__main__.DsRequest object at 0x7f81a7bd9908>
        ```

        ⚠ NOTE: the `defer` argument is a sneaky presence: it's not shown in
        the individual function signatures, as it is handled by a
        decorator that removes it from the list of kwargs it passes to
        the original function.

        # Set values

        To set any (settable) runtime values, pass a dict mirroring the
        format `batch` response as the `values` kwarg, e.g.:

        ``` python
        >>> values = {"0010PsPs_A": { "call_cps": 2 }}
        >>> client.batch("call_cps", values=values, name_filter="0010PsPs_A")
        {'0010PsPs_A': {'call_cps': 2.0}}
        ```
        """

        return self._batch(
            stats,
            values=values,
            name_filter=name_filter,
            tag_filter=tag_filter)


    def _batch(self, stats, values=None, name_filter="", tag_filter=""):

        def _merge_batch(response):
            data = {}
            for req_resp in response:
                name = req_resp[0]["Scenarios"]
                data[name] = {}
                for child in req_resp[0]["children"]:
                    for stat in stats_list:
                        value = child.get(stat, None)
                        if value is not None or stat in child.keys():
                            data[name][stat] = value
            return data

        stats_list = [ stats ] if isinstance(stats, str) else stats
        scenarios = self.scenarios(
            name_filter=name_filter,
            tag_filter=tag_filter)

        main = None
        for s in scenarios:
            req = DsRequest("ExecCtrl", "Scenarios", url=self.url)
            req.param("EntityGroup", s.entity_group)
            for stat in stats_list:

                if not hasattr(s, stat):
                    continue

                method = getattr(s, stat)

                value_param = signature(method).parameters.get("value")
                stat_value = values and values.get(s.name) and values[s.name].get(stat)

                if value_param and stat_value is not None:
                    child = method(values[s.name][stat], defer=True)
                else:
                    child = method(defer=True)
                child.key = stat

                if child.request[child.method].get("ptcname"):
                    child.ptc(0)

                req.child(child)

            if not main:
                main = req
                main._post = _merge_batch
            else:
                main.sibling(req)

        if main and not main.siblings:
            main.callback(_merge_batch)

        return main or {}


    def prefetch(f):
        """
        @private
        """
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if not self._fetched or len(self._scenarios) == 0:
                self._fetch()
                self._fetched = True

            return f(self, *args, **kwargs)

        return wrapper

    @prefetch
    def scenarios(self,
                  name_filter: str = "",
                  tag_filter: str = ""):
        """
        Return list of scenarios that match regular expression
        `name_filter` and/or tag expression `tag_filter`.

        e.g., for name-based filtering:

        ``` python
        >>> client.scenarios(name_filter=\"PsCs\")
        [<scenario 0011PsCs_A>, <scenario 0011PsCs_B>]
        ```

        or use scenario tags:

        ``` python
        >>> client.scenarios(tag_filter="sms and wifi")
        [<scenario 0016WifiPs_A>, ..., <scenario 0500PsPs_SMSoIP_B>]
        ```

        *Note: tag filter syntax is documented in the
        [tagexpressions](https://github.com/timofurrer/tag-expressions)
        library.*

        *Tags have to be configured in the TTCN configuration used to
        launch the TitanSim execution being queried.*
        """

        sf = re.compile(name_filter) if name_filter else None
        tf = tagexpressions.parse(tag_filter) if tag_filter else None

        def _match(s):
            sf_match = sf.search(s.name) or sf.search(s.group) if sf else True
            tf_match = tf.evaluate(s.tags) if tf else True

            return sf_match and tf_match

        return list(filter(_match, self._scenarios))

    @prefetch
    def group_of(self, scenario: str):
        """
        Return scenarios that belong to the same group as `scenario`.
        """
        return list(filter(lambda s: s.group == scenario.group, self.scenarios))

    @prefetch
    def get(self, name: str):
        """
        Return scenario with `name`. Exact match only.
        """
        scenario = list(filter(lambda s: s.name == name, self._scenarios))
        if scenario[0:]:
            return scenario[0]

    def ready(self):
        """
        Return true if TitanSim is traffic-ready. Non-deferable.
        """
        request = DsRequest("ExecCtrl", "ReadyToRun", url=self.url,
                            key="ready").callback(cast=helpers.is_ready)
        try:
            result = request.send()
            return result[0]["ready"]
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError):
            return False

    def exit(self):
        """
        Exit TitanSim. After this call is issued, the simulator becomes
        unavailable until it's restarted.

        *Non-deferrable.*
        """
        request = DsRequest("ExecCtrl", "Exit", method="set", value="1", tp=1, url=self.url)
        try:
            request.send()
        except (requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout):
            pass

    @deferable
    def reset(self):
        """
        Reset all resettable statistics counters.
        """
        return DsRequest("Setup", "resetStatButton", method="set", value="0", tp=1, url=self.url)

    @deferable
    def cps(self, values=None, name_filter="", tag_filter=""):
        """
        Return CPS/RPS/RRPS/SPS for each scenario matched by name or tag
        filter.
        """
        stats = ["call_cps", "message_cps", "rps", "rrps", "drps", "sps"]
        return self._batch(
            stats,
            values=values,
            name_filter=name_filter,
            tag_filter=tag_filter)

    @deferable
    def gos(self, name_filter="", tag_filter=""):
        """
        Return GoS for each scenario matched by name or tag filter.
        """
        return self._batch(
            "call_gos",
            name_filter=name_filter,
            tag_filter=tag_filter)

    @deferable
    def total(self, name_filter="", tag_filter=""):
        """
        Return total number of calls/messages/etc. for each scenario
        matched by scenario or tag filter.
        """
        return self._batch(
            "call_total",
            name_filter=name_filter,
            tag_filter=tag_filter)

    @deferable
    def failed(self, name_filter="", tag_filter=""):
        """
        Return number of failed calls/messages/etc. for each scenario
        matched by name or tag filter.
        """
        return self._batch(
            "call_failed",
            name_filter=name_filter,
            tag_filter=tag_filter)

    @deferable
    def success(self, name_filter="", tag_filter=""):
        """
        Return number of successful calls/messages/etc. for each scenario
        matched by name or tag filter.
        """
        return self._batch(
            "call_success",
            name_filter=name_filter,
            tag_filter=tag_filter)

    @deferable
    def stats(self, name_filter="", tag_filter=""):
        """
        Convenience method to return the most frequently used statistics
        for each scenario matched by scenario or tag filter.
        """
        stats = ["gos", "total", "failed", "success",
                 "rps", "rrps", "drps", "sps",
                 "phase", "state"]
        return self._batch(
            stats,
            name_filter=name_filter,
            tag_filter=tag_filter)

    @deferable
    def start_all(self):
        """
        Start all scenario groups.
        """
        return DsRequest("ExecCtrl", "Start", method="set",  value="1", tp=1, url=self.url)

    @deferable
    def stop_all(self):
        """
        Stop all scenario groups.
        """
        return DsRequest("ExecCtrl", "Stop", method="set", value="1", tp=1, url=self.url)


class Scenario():

    """
    Scenario object that exposes statistics and runtime value API
    methods.

    > ⚠ Don't instantiate Scenario directly. Use instances provided by
    client calls such as `APIClient.scenarios`.

    Methods can be used directly on the Scenario object, or indirectly
    via the `batch` method of `APIClient`. The latter is recommended in
    case a large number of scenarios has to be queried.

    Example call:

    ``` python
    >>> s.call_success()
    83214
    ```

    Method calls are also deferable:

    ``` python
    >>> r = scenario.call_success(defer=True)
    >>> r
    <__main__.DsRequest object at 0x7f911d1aeba8>
    >>> r.send()
    83214
    ```
    """

    def __init__(self, eg, sg, name, cases, tags, url):
        """
        Scenario name.
        """
        self.name = name
        """
        Name of scenario group that the scenario belongs to.
        """
        self.group = sg
        """
        A list of traffic cases associated with scenario.
        """
        self.cases = cases
        """
        URL of TitanSim instance the scenario was found on.
        """
        self.url = url
        """
        Entity group of scenario. In IMS, the entity group name usually
        matches the scenarios name, so this value should see limited
        use.
        """
        self.entity_group = eg

        self.tags = tags
        """
        Scenario tag list
        """

        self._type = None
        self._loadgen = None
        self._register = "Registration"

        if "XCAP" in cases:
            self._loadgen = "XCAP"
            return

        if "regDeReg" in cases:
            self._type = "regdereg"
            self._register = "regDeReg"

        if "CallOrig" in cases:
            self._type = "call"
            self._loadgen = "CallOrig"
            return

        if "ConferenceCreator" in cases:
            self._type = "conference"
            self._loadgen = "ConferenceCreator"
            return

        if "MessageOrig" in cases:
            self._type = "message"
            self._loadgen = "MessageOrig"
            return

        if "CallTerm" in cases:
            self._loadgen = "CallTerm"
            return

        if "MessageTerm" in cases:
            self._loadgen = "MessageTerm"
            return


    def __repr__(self):
        return f"<scenario {self.name}>"


    def __stat(self, source, name, value=None, cast=int):
        """
        Return a request for `name` in `source` (no _DS postfix
        needed!). The scenario name is automatically added to the
        request as the \"ptcname\" property.
        """
        callback = lambda v: self._node(v, name)
        if value is not None:
            req = DsRequest(
                source + "_DS", name, method="set",
                value=str(float(value)), tp=2, url=self.url)
        else:
            req = DsRequest(source + "_DS", name, url=self.url)

        req.callback(callback, cast=cast)

        req.ptc(self.name)
        return req

    def __tc_stat(self, case, statistic, cast=int):
        """
        Return a request for TcStat Statistic `statistic` with traffic
        case `case`.
        """
        # this helper was added some time after self.__stat to use
        # with deregistration requests. Consider whether adapting the
        # other functions to use "TcStat" instead of the __stat
        # approach is possible or feasible.
        callback = lambda v: self._node(v, "TcStat")
        req = DsRequest("ExecCtrl", "TcStat", url=self.url)
        req.param("EntityGroup", self.entity_group)
        req.param("Scenario", self.name)
        req.param("TrafficCase", case)
        req.param("Statistic", statistic)
        req.callback(callback, cast=cast)
        return req

    def __scen(self, name, cast=int, handler="node", method="get", value=None, tp=1):
        callback = lambda v: self._list(v, name) if handler == "list" else self._node(v, name)
        req = DsRequest("ExecCtrl", name, method=method, value=value, tp=tp, url=self.url)
        req.param("EntityGroup", self.entity_group)
        req.param("Scenario", self.name)
        req.callback(callback, cast=cast)
        return req

    def __cps(self, value=None, case=None):
        if value is not None:
            req = DsRequest("ExecCtrl", "TcTargetCPSOrWeight",
                            method="set",
                            value=str(float(value)),
                            tp=2,
                            url=self.url)
        else:
            req = DsRequest("ExecCtrl", "TcTargetCPSOrWeight", url=self.url)
        callback = lambda v: self._node(v, "TcTargetCPSOrWeight")
        req.param("EntityGroup", self.entity_group)
        req.param("Scenario", self.name)
        req.param("TrafficCase", case)
        req.callback(callback, cast=float)
        return req

    def _node (self, value, name):
        if isinstance(value, list):
            return value[0][name]

        if isinstance(value, object):
            return value[name]

    def _list (self, value, name):
        lst = []
        for obj in value[0]:
            lst.append(obj[name])
        return lst

    @deferable
    def is_weighted(self):
        """
        Return true if scenario is weighted.
        """
        return self.__scen("ScIsWeighted", cast=helpers.is_weighted)

    @deferable
    def is_running(self):
        """
        Return true if scenario is running.
        """
        return self.__scen("ScStatus", cast=helpers.is_running)

    @deferable
    def start(self):
        """
        Start scenario.
        """
        return self.__scen("ScGrpStart", cast=bool, method="set", value="true", tp=3)

    @deferable
    def stop(self):
        """
        Stop scenario.
        """
        return self.__scen("ScGrpStart", cast=bool, method="set", value="false", tp=3)

    @deferable
    def phases(self):
        """
        Return phases of scenario.
        """
        return self.__scen("Phases", handler="list", cast=str)

    @deferable
    def phase(self):
        """
        Return current phase of scenario.
        """
        return self.__scen("ScGrpScStatus", cast=helpers.phase)

    @deferable
    def state(self):
        """
        Return current phase state of scenario.
        """
        return self.__scen("ScGrpScStatus", cast=helpers.state)

    @deferable
    @only(["orig", "xcap"], any)
    def cps(self, value=None):
        """
        Return calls per second.
        """
        case = "Presence" if self._loadgen == "XCAP" else self._loadgen
        return self.__cps(value, case=case)

    @deferable
    @only("has_gos")
    def gos(self):
        """
        Return general GoS from TC Stats.
        """
        callback = lambda v: self._node(v, "TcGoS")
        req = DsRequest("ExecCtrl", "TcGoS", url=self.url)
        req.param("EntityGroup", self.entity_group)
        req.param("Scenario", self.name)
        req.param("TrafficCase", self._loadgen)
        req.callback(callback, cast=float)
        return req

    @deferable
    @only(["orig", "term"], any)
    def total(self):
        """
        Return the general total from TC Stats.
        """
        return self.__tc_stat(self._loadgen, "Starts", cast=int)

    @deferable
    @only(["orig", "term"], any)
    def success(self):
        """
        Return the general number of successes from TC Stats.
        """
        return self.__tc_stat(self._loadgen, "Success", cast=int)

    @deferable
    @only(["orig", "term"], any)
    def failed(self):
        """
        Return the general number of failures from TC Stats.
        """
        return self.__tc_stat(self._loadgen, "Fail", cast=int)

    @deferable
    @only("call")
    def call_gos(self):
        """
        Return call grade of service percentage.
        """
        return self.__stat(self._loadgen, "gos", cast=helpers.gos)

    @deferable
    @only(["call", "orig"])
    def call_total(self):
        """
        Return the total number of calls.
        """
        return self.__stat(self._loadgen, "nofTotal")

    @deferable
    @only(["call", "orig"])
    def call_success(self):
        """
        Return the number of successful calls.
        """
        return self.__stat(self._loadgen, "nofSucc")

    @deferable
    @only(["call", "orig"])
    def call_failed(self):
        """
        Return the number of failed calls.
        """
        return self.__stat(self._loadgen, "nofUnsucc")

    @deferable
    @only(["call", "orig"])
    def call_retry(self):
        """
        Return the number of retried calls.
        """
        return self.__stat(self._loadgen, "nofRetryAfter")

    @deferable
    @only(["call", "orig"])
    def call_cps(self, value=None):
        """
        Return/set call/sec.
        """
        return self.__cps(value, case=self._loadgen)

    # CALL

    @deferable
    @only(["call", "orig", "not_conference"])
    def call_holding_time_min(self, value=None):
        """
        Return minimum call holding time.
        """
        return self.__stat("CallOrig", "callHoldMin", value=value, cast=float)

    @deferable
    @only(["call", "orig", "not_conference"])
    def call_holding_time_max(self, value=None):
        """
        Return minimum call holding time.
        """
        return self.__stat("CallOrig", "callHoldMax", value=value, cast=float)

    @deferable
    @only(["call", "term"])
    def call_answer_time_min(self):
        """
        Return minimum call answer time.
        """
        return self.__stat("CallTerm", "answeringTimeMin", cast=float)

    @deferable
    @only(["call", "term"])
    def call_answer_time_max(self):
        """
        Return maximum call answer time.
        """
        return self.__stat("CallTerm", "answeringTimeMax", cast=float)

    # CONFERENCE

    @deferable
    @only(["conference", "orig"])
    def conference_duration_min(self, value=None):
        """
        Return or set conference duration minimum.
        """
        return self.__stat("ConferenceCreator", "conferenceDurationMin", value=value, cast=float)

    @deferable
    @only(["conference", "orig"])
    def conference_duration_max(self, value=None):
        """
        Return or set conference duration minimum.
        """
        return self.__stat("ConferenceCreator", "conferenceDurationMax", value=value, cast=float)

    # CONFIG

    @deferable
    def user_range_min(self):
        """
        Return the first number in user range.
        """
        return self.__stat("Config", "idLow")

    @deferable
    def user_range_max(self):
        """
        Return the last number in user range.
        """
        return self.__stat("Config", "idHigh")

    @deferable
    @only("call")
    def codec(self):
        """
        Return scenario codec info.
        """
        return self.__stat("Media", "MLSimPlus.supportedCodecs", cast=str)

    @deferable
    def protocol(self):
        """
        Return traffic case transport protocol name.
        """
        return self.__stat("Config","preferredTransport", cast=str)

    # REGISTRATION

    @deferable
    @only("reg")
    def rps(self,  value=None):
        """
        Return scenario registrations/sec. If a floating-point number
        `value` is provided, set `rps` to that value.
        """
        return self.__cps(value, case=self._register)

    @deferable
    @only("reg")
    def rrps(self, value=None):
        """
        Return scenario re-registration/sec. If a floating-point number
        `value` is provided, set reregistration `cps` to that value.
        """
        return self.__cps(value, case="reRegistration")

    @deferable
    @only("dereg")
    def drps(self, value=None):
        """
        Return scenario de-registration/sec. If a floating-point number
        `value` is provided, set deregistration `cps` to that value.
        """
        return self.__cps(value, case="deRegistration")

    @deferable
    @only("reg")
    def registration_total(self):
        """
        Return the number of total registrations.
        """
        return self.__stat("Registration","nofTotal")

    @deferable
    @only("reg")
    def registration_success(self):
        """
        Return the number of successful registrations.
        """
        return self.__stat("Registration","nofSucc")

    @deferable
    @only("reg")
    def registration_gos(self):
        """
        Return the registrations grade of service percentage.
        """
        return self.__stat("Registration","gos", cast=helpers.gos)

    @deferable
    @only("reg")
    def registration_failed(self):
        """
        Return the number of failed registrations.
        """
        return self.__stat("Registration","nofUnsucc")

    @deferable
    @only("reg")
    def registration_retry(self):
        """
        Return the number of registration retries.
        """
        return self.__stat("Registration","nofRetryAfter")

    @deferable
    @only("reg")
    def registration_gos_excluding_retry(self):
        """
        Return the registrations grade of service percentage.
        """
        return self.__stat("Registration","gosExclRetry", cast=helpers.gos)

    @deferable
    @only("reg")
    def registration_expiry(self, value=None):
        """
        Return registration expiry.
        """
        return self.__stat("Registration","registrationExpires", value=value, cast=float)

    @deferable
    @only("reg")
    def reregistration_margin(self):
        """
        Return reregistration margin.
        """
        return self.__stat("Registration","reRegMargin", cast=float)

    # DEREGISTRATION

    @deferable
    @only("dereg")
    def deregistration_total(self):
        """
        Return the number of successful deregistrations.
        """
        return self.__tc_stat("deRegistration", "Starts")

    @deferable
    @only("dereg")
    def deregistration_success(self):
        """
        Return the number of successful deregistrations.
        """
        return self.__tc_stat("deRegistration", "Success")

    @deferable
    @only("dereg")
    def deregistration_failed(self):
        """
        Return the number of failed deregistrations.
        """
        return self.__tc_stat("deRegistration", "Fail")

    # SUBSCRIBE

    @deferable
    @only("subscribe")
    def sps(self, value=None):
        """
        Return scenario subscribe/sec.If a floating-point number `value` is
        provided, set subscribe `cps` to that value.
        """
        return self.__cps(value, case="Subscribe")

    @deferable
    @only("subscribe")
    def subscribe_total(self):
        """
        Return the number of total subscriptions.
        """
        return self.__stat("Subscribe","nofTotal")

    @deferable
    @only("subscribe")
    def subscribe_success(self):
        """
        Return the number of successful subscriptions.
        """
        return self.__stat("Subscribe","nofTotalSucc")

    @deferable
    @only("subscribe")
    def subscribe_failed(self):
        """
        Return the number of failed subscriptions.
        """
        return self.__stat("Subscribe","nofTotalUnsucc")

    @deferable
    @only("subscribe")
    def subscribe_gos(self):
        """
        Return the subscription grade of service percentage.
        """
        return self.__stat("Subscribe","gosTotal", cast=helpers.gos)

    # SMS

    @deferable
    @only(["sms", "orig"])
    def message_cps(self, value=None):
        """
        Return/set message/sec.
        """
        return self.__cps(value, case="MessageOrig")

    @deferable
    @only("sms")
    def message_gos(self):
        """
        Return the message Grade of Service percentage.
        """
        return self.__stat(self._loadgen, "gos", cast=helpers.gos)

    @deferable
    @only(["sms", "orig"])
    def message_sent(self):
        """
        Return the total number of messages sent.
        """
        return self.__stat("MessageOrig", "nofSentMessage")

    @deferable
    @only(["sms", "term"])
    def message_received(self):
        """
        Return the number of received messages.
        """
        return self.__stat("MessageTerm", "nofReceivedMessage")

    @deferable
    @only(["sms", "orig"])
    def message_success(self):
        """
        Return the number of successful messages.
        """
        return self.__stat('MessageOrig', "nofSucc", cast=int)

    @deferable
    @only(["sms", "orig"])
    def message_failed(self):
        """
        Return the number of failed messages.
        """
        return self.__stat('MessageOrig', "nofUnsucc", cast=int)

    # MEDIA

    @property
    def _mpfx(self):
        """
        MLSimPlus values have a scenario name prefix
        """
        return f"{self.name}_MLSimPlus"

    @deferable
    @only("call")
    def media_total(self):
        """
        Return the total number of media sessions.
        """
        return self.__stat("MLSimPlus", f"{self._mpfx}.nrOfSessions")

    @deferable
    @only("call")
    def media_success(self):
        """
        Return the number of successful media sessions.
        """
        return self.__stat("MLSimPlus", f"{self._mpfx}.nrOfSuccessful")

    @deferable
    @only("call")
    def media_failed(self):
        """
        Return the number of failed media sessions.
        """
        return self.__stat("MLSimPlus", f"{self._mpfx}.nrOfUnsuccessful")

    @deferable
    @only("call")
    def media_unknown(self):
        """
        Return the number of inconclusive media sessions.
        """
        return self.__stat("MLSimPlus", f"{self._mpfx}.nrOfInconclusive")

    @deferable
    @only("call")
    def media_dropped(self):
        """
        Return the number of dropped media sessions.
        """
        return self.__stat("MLSimPlus", f"{self._mpfx}.nrOfDropped")

    @deferable
    @only("call")
    def media_error(self):
        """
        Return the number of media session errors.
        """
        return self.__stat("MLSimPlus", f"{self._mpfx}.nrOfRecError")

    @deferable
    @only("call")
    def media_packets_sent(self):
        """
        Return the number of sent media packets.
        """
        return self.__stat("MLSimPlus", f"{self._mpfx}.nrOfSentPackets")

    @deferable
    @only("call")
    def media_packets_received(self):
        """
        Return the number of received media packets.
        """
        return self.__stat("MLSimPlus", f"{self._mpfx}.nrOfReceivedPackets")

    @deferable
    @only("call")
    def media_packets_lost(self):
        """
        Return the number of list media packets.
        """
        return self.__stat("MLSimPlus", f"{self._mpfx}.nrOfLostPackets")

    @deferable
    @only("call")
    def media_packets_duplicated(self):
        """
        Return the number of duplicated media packets.
        """
        return self.__stat("MLSimPlus", f"{self._mpfx}.nrOfDuplicatedPackets")

    @deferable
    @only("call")
    def media_packets_late(self):
        """
        Return the number of late media packets.
        """
        return self.__stat("MLSimPlus", f"{self._mpfx}.nrOfLatePackets")

    @deferable
    @only("call")
    def media_packets_reordered(self):
        """
        Return the number of reordered media packets.
        """
        return self.__stat("MLSimPlus", f"{self._mpfx}.nrOfReorderedPackets")

    @deferable
    @only("call")
    def media_latency_95(self):
        """
        Return the media latency 95% value.
        """
        return self.__stat("MLSimPlus", f"{self._mpfx}.latency95PCT", cast=helpers.sec)

    # XCAP

    @deferable
    @only("xcap")
    def xcap_put_sent(self):
        """
        Return the number of XCAP PUT requests sent.
        """
        return self.__stat("XCAP", "nrOfXCAPPutSent")

    @deferable
    @only("xcap")
    def xcap_put_success(self):
        """
        Return the number of successful XCAP PUT requests.
        """
        return self.__stat("XCAP", "nrOfXCAPPutOk")

    @deferable
    @only("xcap")
    def xcap_put_failed(self):
        """
        Return the number of failed XCAP PUT requests.
        """
        return self.__stat("XCAP", "nrOfXCAPPutNOk")

    @deferable
    @only("xcap")
    def xcap_put_timeout(self):
        """
        Return the number of timed out XCAP PUT requests.
        """
        return self.__stat("XCAP", "nrOfXCAPPutTimeout")

    @deferable
    @only("xcap")
    def xcap_get_sent(self):
        """
        Return the number of XCAP GET requests sent.
        """
        return self.__stat("XCAP", "nrOfXCAPGetSent")

    @deferable
    @only("xcap")
    def xcap_get_success(self):
        """
        Return the number of successful XCAP GET requests.
        """
        return self.__stat("XCAP", "nrOfXCAPGetOk")

    @deferable
    @only("xcap")
    def xcap_get_failed(self):
        """
        Return the number of failed XCAP GET requests.
        """
        return self.__stat("XCAP", "nrOfXCAPGetNOk")

    @deferable
    @only("xcap")
    def xcap_get_timeout(self):
        """
        Return the number of timed out XCAP GET requests.
        """
        return self.__stat("XCAP", "nrOfXCAPGetTimeout")

    @deferable
    @only("xcap")
    def xcap_delete_sent(self):
        """
        Return the number of XCAP DELETE requests sent.
        """
        return self.__stat("XCAP", "nrOfXCAPDeleteSent")

    @deferable
    @only("xcap")
    def xcap_delete_success(self):
        """
        Return the number of successful XCAP DELETE requests.
        """
        return self.__stat("XCAP", "nrOfXCAPDeleteOk")

    @deferable
    @only("xcap")
    def xcap_delete_failed(self):
        """
        Return the number of failed XCAP DELETE requests.
        """
        return self.__stat("XCAP", "nrOfXCAPDeleteNOk")

    @deferable
    @only("xcap")
    def xcap_delete_timeout(self):
        """
        Return the number of timed out XCAP DELETE requests.
        """
        return self.__stat("XCAP", "nrOfXCAPDeleteTimeout")

    @deferable
    @only("xcap")
    def xcap_post_create_sent(self):
        """
        Return the number of XCAP POSTCREATE requests sent.
        """
        return self.__stat("XCAP", "nrOfXCAPPostCreateSent")

    @deferable
    @only("xcap")
    def xcap_post_create_success(self):
        """
        Return the number of successful XCAP POSTCREATE requests.
        """
        return self.__stat("XCAP", "nrOfXCAPPostCreateOk")

    @deferable
    @only("xcap")
    def xcap_post_create_failed(self):
        """
        Return the number of failed XCAP POSTCREATE requests.
        """
        return self.__stat("XCAP", "nrOfXCAPPostCreateNOk")

    @deferable
    @only("xcap")
    def xcap_post_create_timeout(self):
        """
        Return the number of timed out XCAP POSTCREATE requests.
        """
        return self.__stat("XCAP", "nrOfXCAPPostCreateTimeout")

    @deferable
    @only("xcap")
    def xcap_post_delete_sent(self):
        """
        Return the number of XCAP POSTDELETE requests sent.
        """
        return self.__stat("XCAP", "nrOfXCAPPostDeleteSent")

    @deferable
    @only("xcap")
    def xcap_post_delete_success(self):
        """
        Return the number of successful XCAP POSTDELETE requests.
        """
        return self.__stat("XCAP", "nrOfXCAPPostDeleteOk")

    @deferable
    @only("xcap")
    def xcap_post_delete_failed(self):
        """
        Return the number of failed XCAP POSTDELETE requests.
        """
        return self.__stat("XCAP", "nrOfXCAPPostDeleteNOk")

    @deferable
    @only("xcap")
    def xcap_post_delete_timeout(self):
        """
        Return the number of timed out XCAP POSTDELETE requests.
        """
        return self.__stat("XCAP", "nrOfXCAPPostDeleteTimeout")

    @deferable
    @only("xcap")
    def xcap_all_sent(self):
        """
        Return the number of all XCAP requests sent.
        """
        return self.__stat("XCAP", "nrOfXCAPAllSent")

    @deferable
    @only("xcap")
    def xcap_all_success(self):
        """
        Return the number of all successful XCAP requests.
        """
        return self.__stat("XCAP", "nrOfXCAPAllOk")

    @deferable
    @only("xcap")
    def xcap_all_failed(self):
        """
        Return the number of all failed XCAP requests.
        """
        return self.__stat("XCAP", "nrOfXCAPAllNOk")

    @deferable
    @only("xcap")
    def xcap_all_timeout(self):
        """
        Return the number of all timed out XCAP requests.
        """
        return self.__stat("XCAP", "nrOfXCAPAllTimeout")

    @deferable
    @only(["call", "sms", "reg", "xcap"], operator=any)
    def presence_load_timer(self, value=None):
        """
        Return or set Presence load timer value
        """
        return self.__stat("Presence", "presenceLoadTimerValue", value=value, cast=float)