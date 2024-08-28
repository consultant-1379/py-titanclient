"""
TitanSim DsREST JSON requests and responses are fairly complex.

DsRequest is a Python abstraction layer to compose and send these
requests. Its primary purpose currently is to aid implementation of the
DsREST API methods in `APIClient`.

> ⛔ This is an alpha quality module and it supports only a limited subset
> of the DsREST JSON schema, such as parameterization, selection,
> filtering and child requests. It's direct use is neither recommended nor
> supported  and the documentation is provided FYI.
"""

import re
import json
import requests
import functools

from types import SimpleNamespace

class DsRequest:

    """
    DsRequest object
    """

    def __init__(self, source, element, method="get", params=None, value=None, tp=None, url=None, key=None):
        self.url = url
        self.siblings = []
        self.method = "setData" if method == "set" else "getData"
        self.request = {
            self.method: {
                "element": element,
                "source": source}}
        self.key = key
        self._cast = str
        self._callback = lambda identity : identity
        self._siblings_callback = lambda identity : identity
        self._post = lambda i: i
        self._silent = False
        if params:
            for k,v in params.items():
                self.param(k,v)
        if self.method == "setData":
            if not value or not tp:
                raise  ValueError("Missing value/tp argument for setData request!")
            self.request[self.method]["content"] = value
            self.request[self.method]["tp"] = tp

    def __repr__(self):
        return f"<DsRequest {self.url}>"

    def child(self, request):
        """Add a child request to request.

        """
        children = self.request[self.method].get("children")
        if not children:
            self.request[self.method]["children"] = [ request ]
        else:
            self.request[self.method]["children"].append(request)
        return self

    def sibling(self, req, siblings_callback=None):
        """
        Add a sibling request to request.
        """
        if not isinstance(req, DsRequest):
            raise ValueError("Only DsRequest objects can be siblings.")
        if siblings_callback:
            self._siblings_callback = siblings_callback
        self.siblings.append(req)
        return self

    def param(self, key, value):
        """
        Set parameter `key` with `value` for request.
        """
        if not self.request[self.method].get("params"):
            self.request[self.method]["params"] = []
        idx = None
        for i, param in enumerate(self.request[self.method]["params"]):
            if param["paramName"] == key:
                idx = i
        param = {
            "paramName": key,
            "paramValue": "%Parent{}%".format(value) if isinstance(value, int) else value
        }
        if idx != None:
           self.request[self.method]["params"][idx] = param
        else:
            self.request[self.method]["params"].append(param)
        return self

    def timeline(self, period, maxpoints, since=0):
        """
        Set timeline for request. A maximum of `maxpoints` samples are
        collected each `period` seconds, starting with `since`. A
        since=0 value means the timestamp for the request.

        The values of the timeline must be queried in a separate
        request. Subsequent requests should return the expanding list
        of y/x values.


        """
        raise NotImplementedError

    def callback(self, function=lambda i: i, cast=str):
        """
        Apply `function` to return value before returning (but after
        processing the response). `function` should have an arity of
        one. Note that for list of values, it takes the list as its
        argument, it isn't mapped over it.
        """
        self._callback = function
        self._cast = cast

        return self

    def ptc(self, ptcname):
        """
        Set the PTCname attribute for request.
        """
        self.request[self.method]["ptcname"] = ptcname if isinstance(ptcname, str) else "%Parent{}%".format(ptcname)
        return self

    def send(self, url=None, timeout=0):
        """
        Send `DsRequest` to `url` with `timeout`. If `all` is true,
        sibling DsRequests are also sent and a list of values is
        returned instead of one primitive value.

        If no `url` is provided, the request is sent to the default
        `self.url` provided during instantiation. Since both the
        object itself and `send` can be parameterized with an address,
        it's possible to send the same `DsRequest` to the same address
        repeatedly or to different TitanSims depending on the `url`
        parameter.
        """
        siblings = self.siblings if all else []
        reqlist = []
        reqlist.append(self)
        reqlist = reqlist + siblings
        bundle = { "requests": reqlist, "timeOut": timeout }
        payload = json.dumps(bundle, cls=self._Encode)
        response = requests.post(url or self.url, data=payload, timeout=5)
        content = json.loads(response.text)["contentList"]
        result = self._process_response(content, reqlist)
        #print(result)
        if not self._silent:
            if self.siblings:
                values = self._siblings_callback([ reqlist[i]._callback(r) for i, r in enumerate(result) ])
                # refactor "_post" into something proper for
                # postprocessung the entire response
                return self._post(values)
            else:
                return self._callback(result)
        else:
            return None

    def _process_response(self, response, request):
        if not response:
            return None
        if isinstance(response, list):
            return [ self._process_response(obj, (request[i] if isinstance(request, list) else request))
                     for i, obj in enumerate(response) ]
        if isinstance(response, object):
            if response.get("node"):
                try:
                    value = response["node"].get("val", None)
                    value = request._cast(value)
                except ValueError:
                    #print("couldn't cast value", value)
                    value = None
                node_data = { request.key if request.key else request.request[request.method]["element"]: value}
                resp_children = response["node"].get("childVals")
                reqs_children = request.request[request.method].get("children", None)
                if resp_children:
                    node_data["children"] = [ self._process_response(child, reqs_children[i] if reqs_children else request)
                                              for i, child in enumerate(resp_children) ]
                return node_data
            if response.get("list"):
                return [ self._process_response(obj, request) for obj in response.get("list") ]

    def _json(self,timeout=5):
        """
        Return request bundle as JSON.
        """
        siblings = self.siblings if all else []
        reqlist = []
        reqlist.append(self)
        reqlist = reqlist + siblings
        bundle = { "requests": reqlist, "timeOut": timeout }
        return self._Encode().encode(bundle)

    class _Encode(json.JSONEncoder):

        """
        _Encode alters JSONEncoder to return only the `request` class
        attribute of `DsRequest` for encoding in JSON.
        """
        def default(self, o):
            return o.__dict__["request"]

class LED():
    """
    Parse and access LED string as an object
    """
    def __init__(self, string):
        self.__rx = re.compile(r"\[led:([^\]]+)\](.*)")
        match = self.__rx.match(string)
        self.color, self.status = match.groups() if match else (None, None)

class StatusLED(LED):
    """
    Parse and access LED string as an object
    """
    def __init__(self, string):
        super().__init__(string)
        self.phase, self.state = self.status.split(" - ") if self.status else [None, None]

def deferable(f):
    """
    Decorator for functions that return DsRequest objects. If the
    decorated function is passed the `defer=True` keyword argument,
    return the DsRequest object as-is. Otherwise, call its send()
    method and return the processed response.
    """

    @functools.wraps(f)
    def optionally_defer(self, *args, **kwargs):
        defer = kwargs.get("defer", False)
        if defer: del kwargs["defer"]
        request = f(self, *args, **kwargs)
        if request:
            val = request if defer else request.send()
            return val
    return optionally_defer

def only(conditions, operator=all):

    conditionals = {
        "orig": lambda s: s._loadgen in ["CallOrig", "ConferenceCreator", "MessageOrig"],
        "term": lambda s: s._loadgen in ["CallTerm", "MessageTerm"],
        "call": lambda s: s._loadgen in ["CallOrig", "ConferenceCreator", "CallTerm"],
        "xcap": lambda s: "XCAP" in s.cases,
        "sms":  lambda s: any(map(lambda c: c.startswith("Message"), s.cases)),
        "dereg": lambda s: "deRegistration" in s.cases,
        "reg": lambda s: "Registration" in s.cases,
        "subscribe": lambda s: "Subscribe" in s.cases,
        "conference": lambda s: "ConferenceCreator" in s.cases,
        "not_conference": lambda s: not "ConferenceCreator" in s.cases,
        "has_loadgen": lambda s: s._loadgen and s._loadgen != "XCAP",
        "has_gos": lambda s: s._loadgen in ["CallOrig", "CallTerm", "ConferenceCreator", "MessageOrig", "MessageTerm", "XCAP"]}

    def func_wrapper(f):
        @functools.wraps(f)
        def args_wrapper(self, *args, **kwargs):
            applies = []
            for cond in conditions if isinstance(conditions, list) else [conditions]:
                applies.append(conditionals[cond](self))
            if not conditions or operator(applies):
                return f(self, *args, **kwargs)
            else:
                # invalid requests spam the TitanSim log with useless
                # messages. 'only' annotates each method to indicate
                # whether it applies to the given scenario. If it
                # doesn't, it returns a no-op (placeholder) request.
                return DsRequest("DataSource", "not", url=self.url).callback(cast=helpers.nop)
        return args_wrapper
    return func_wrapper

def __cast(function):
    """
    Apply cast function both to individual values and lists. In some
    cases, we want to evaluate a DsREST API response instead of
    returning it as-is. For example, "ScIsWeighted" has values like
    "Weighted" or "Decl", which is not as useful as a boolean return
    value.
    """
    return lambda arg: list(map(function, arg)) if isinstance(arg, list) else function(arg)

helpers = SimpleNamespace(
    nop=lambda v: None,
    gos=lambda v:  float(LED(v).status) if LED(v).status else None,
    sec=__cast(lambda v: int(v.rstrip("s"))),
    phase=__cast(lambda v: StatusLED(v).phase),
    state=__cast(lambda v: StatusLED(v).state),
    is_weighted=lambda v: v == "Weighted",
    is_running=lambda v: v == "Running",
    is_ready=lambda v: LED(v).status == "ReadyToRun")
