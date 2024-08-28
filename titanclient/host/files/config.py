""" .. include:: ../../../docs/host/config.md """
import os
import io
from collections import OrderedDict

from arpeggio import *
from arpeggio import RegExMatch as _


class Config():

    """
    Parse and manipulate TitanSim configuration files.

    ```
    >>> from titanclient.config import Config
    >>> Config("/tmp/TrafficMix.cfg")
    <titanclient.Config object at 0x7f8d93f572e8>
    ```
    """

    def __init__(self, pathname, parse_included=True, name=None):
        self.name = name or ""

        self._tree = dict()
        self.__parse_included = parse_included
        self.__main_config_file = pathname
        self._included = OrderedDict()
        self.__config_dir = os.path.dirname(pathname)
        self.__scenarios = []

        if os.path.isdir(pathname):
            for f in os.listdir(pathname):
                if "cfg" in f and not f.endswith("_ims.cfg"):
                    self.__config_dir = pathname
                    self.__main_config_file = os.path.join(self.__config_dir, f)
                    break

        self.load(self.__main_config_file)

        if parse_included:
            self.load_included()

        self.load_scenarios()

    def __repr__(self):
        return f"<TitanSimConfig {self.name}>"

    def to_dict(self):
        return self._tree

    def load(self, pathname):
        """
        Load TitanSim configuration file at `pathname`. If
        `parse_included` is True, load and merge all files in the
        [INCLUDE] section of the config. This is mandatory for correct
        functioning for configuration files that rely on references to
        top-level definitions (e.g. ${PSPS_SCENNAME}). Subsequent
        calls to this function update the stored tree.
        """
        fullpath = os.path.join(self.__config_dir, pathname.strip("\""))
        self._tree.update(self._parse(open(fullpath, "r").read()))

    def included(self):
        """
        Return a list of included files with full paths to their expected
        location. If the configuration file is fetched from a remote
        host, set parse_included to False and fetch each of the
        included files before calling `load_includes`.

        ```
        >>> cfg.includes()
        [\"/tmp/Define.txt\", \"/tmp/TrafficMix_ps_ims.cfg\"]
        >>> cfg.load_includes() # after transferring files
        ```
        """
        return self._tree.get("INCLUDE")

    def load_included(self):
        """
        Update configuration object with information from included
        files. Assumes the files to be in the locations provided by
        the `includes` call.
        """
        for include in self._tree.get("INCLUDE"):
            local_path = os.path.join(self.__config_dir, include.strip("\""))
            with open(local_path, "r") as file:
                self._included[local_path] = self._parse(file.read())

    def group_of(self, scenario):
        """
        Return all scenarios belonging to the same scenario group as
        `scenario`.
        """
        return list(filter(lambda s: s.group == scenario.group, self.scenarios()))

    def add(self, scenario):
        """
        Add `scenario` to config. This function is limited to reinserting
        previously removed Scenario objects.
        """
        if not isinstance(scenario, Scenario):
            raise TypeError(f"{scenario} is not of Scenario type!")

        if self.scenarios(scenario_filter=scenario.name):
            raise ValueError(f"{scenario} is already in config!")

        self.__scenarios.append(scenario)

    def remove(self, scenario):
        """
        Remove scenario object from config. All scenarios belonging to the
        same group are removed.
        """
        if not isinstance(scenario, Scenario):
            raise TypeError(f"{scenario} is not of Scenario type!")

        for s in self.scenarios(scenario.group):
            try:
                self.__scenarios.remove(s)
            except ValueError as e:
                print(f"couldn't remove {s.name}")

        scens = self._get_scen_tree()
        for i, s in enumerate(scens):
            name = _resolve(s.get("scenarioName"), self)
            if scenario.group == name:
                del scens[i]

    def get_traffic_cases(self, scenario_filter=""):
        return self.scenarios(scenario_filter)

    def scenarios(self, scenario_filter=""):
        """
        Return a list of scenarios. if `scenario_filter` is
        provided, only those scenarios the names of which match the
        filter are returned.
        """
        return [ s for s in self.__scenarios if scenario_filter in s.name ]

    def batch(self, value, scenario_filter="", zipped=False):
        """
        Query configuration file for various scenario values. The
        interface is analogous to the one provided by `client.Client`.

        ```
        >>> config.batch(\"cps\")
        [0.3,0.0, ... ]
        ```

        Zipping and scenario_filter are both supported:

        ```
        >>> config.batch(\"cps\", scenario_filter=\"0010PsPs\", zipped=True)
        { \"0010PsPs_A\": 0.3, \"0010PsPs_B\": 0.0 }
        ```
        """
        scenarios = []
        values = []
        for scenario in self.scenarios(scenario_filter=scenario_filter):
            scenarios.append(scenario.name)
            method = getattr(scenario, value, None)
            values.append(method() if method else None)
        return dict(zip(scenarios, values)) if zipped else values

    def _parse(self, string):
        """
        Parse TitanSim config string.
        """
        # temporary fix for invalid config files
        string = string.replace(" = ", " := ")
        try:
            parser = ParserPython(config, comment, debug=False)
            parse_tree = parser.parse(string)
            config_tree = visit_parse_tree(parse_tree, TitanSimConfigVisitor(debug=False))
            return config_tree
        except NoMatch as e:
            raise e

    def load_scenarios(self):

        scens = self._get_scen_tree()

        for scen in scens:
            group = _resolve(scen.get("scenarioName"), self)
            for tc in scen.get("trafficCases"):
                self.__scenarios.append(Scenario(tc, group, self))


    def _get_scen_tree(self):
        section = "MODULE_PARAMETERS"
        varname = "tsp_IMS_Configuration_Scenarios"
        return (
            self._tree.get(section, {}).get(varname)
            or
            self._included_get(section, {}).get(varname, [])
        )


    def _included_get(self, key, default=None):

        for f, tree in self._included.items():
            included = tree.get(key)
            if included:
                return included

        return default


    def dump(self, outfile, indent=4):
        """
        Dump config data as TTCN3 config flle(s).
        """

        class Indenter():

            def __init__(self, n):
                self.n = n
                self.offset = 0
                self.spaces = ""

            def incr(self):
                self.offset = self.offset + self.n
                self.spaces = " "  *  self.offset

            def decr(self):
                self.offset = self.offset - self.n
                self.spaces = " "  *  self.offset

        prettyprint = indent != 0

        i = Indenter(indent)

        def value(val):

            if isinstance(val, dict):
                return object_(val)

            if isinstance(val, list):
                return list_(val)

            if val is None:
                return ""

            return str(val)

        def pair(key, val):
            return f"{i.spaces}{key} := {value(val)}"

        def object_(obj):

            if prettyprint:
                i.incr()
                objs = ",\n".join([pair(k, obj[k]) for k in obj.keys()])
                i.decr()
                return f"{{\n{objs}\n{i.spaces}}}"

            return f"{{ {', '.join([pair(k, obj[k]) for k in obj.keys()])} }}"

        def list_(lst):

            if not lst:
                return "{}"

            if prettyprint:
                i.incr()
                items = f"{{\n{i.spaces}"
                items += f",\n{i.spaces}".join([value(val) for val in lst])
                i.decr()
                return f"{items}\n{i.spaces}}}"

            return f"{{ {', '.join([value(val) for val in lst])} }}"

        def section(section, title):

            out = f"\n[{title}]\n"
            if isinstance(section, dict):
                for key in section.keys():
                    out += pair(key, section[key]) + "\n"

            if isinstance(section, list):
                for item in section:
                    out += value(item) + "\n"

            return out


        def dump_tree(tree, pathname):
            outstr = io.StringIO()

            for key in tree.keys():
                outstr.write(section(tree[key], key))

            with open(pathname, "w") as file:
                file.write(outstr.getvalue())

        outdir = os.path.dirname(outfile)

        for included, data in self._included.items():
            outincl = os.path.join(outdir, os.path.basename(included))
            dump_tree(data, outincl)

        dump_tree(self._tree, outfile)



class Scenario():

    """
    Scenario is the object representation of a Scenario parsed into
    Config. It provides a functional interface similar to `Client`.

    Naturally, runtime data methods are not supported on config
    Scenario objects.
    """

    __origs = ["CallOrig", "ConferenceCreator", "MessageOrig"]
    __terms = ["CallTerm" ]

    def __init__(self, scenario_tree, group, config):
        self.__scenario = scenario_tree
        self.__tree = config._tree
        self._config = config

        self.group = group
        self.name = _resolve(self.__scenario.get("name"), self._config)
        self.case = _resolve(self.__scenario.get("trafficCase"),  self._config)

    def __repr__(self):
        return "<scenario {name}>".format(name=self.name)

    def cps(self, value=None):
        """
        Return/set general CallOrig / MessageOrig / ConferenceCreator
        calls/sec for scenario.
        """
        return self._getset(["trafficSpecific", self.case[0].lower() + self.case[1:], "cps"], value)

    def rps(self, value=None):
        """
        Return/set scenario registrations/sec.
        """
        return self._getset(["trafficSpecific", "registration", "rps"], value)

    def rrps(self):
        """Return scenario reregistration/sec.
        """
        # the number of users divided by registration expiry minus
        # the re-registration margin.
        users = self.user_count()
        expiry = self.registration_expiry()
        margin = self.reregistration_margin()
        if users and expiry and margin:
            return round(float(users) / (float(expiry) - float(margin)), 4)

    def registration_expiry(self, value=None):
        """
        Return/set scenario registration expiry time.
        """
        return self._getset(["trafficSpecific","registration","registrationExpires"], value)

    def reregistration_margin(self, value=None):
        """
        Return/set scenario registration margin.
        """
        return self._getset(["trafficSpecific", "registration", "reRegMargin"], value)

    def call_holding_time_min(self, value=None):
        """
        Return/set minimum holding time.
        """
        return self._getset(["trafficSpecific", "callOrig", "callHoldMin"], value)

    def call_holding_time_max(self, value=None):
        """
        Return/set maximum holding time.
        """
        return self._getset(["trafficSpecific", "callOrig", "callHoldMax"], value)

    def call_answer_time_min(self, value=None):
        """
        Return/set minimum call answer time.
        """
        return self._getset(["trafficSpecific", "callTerm", "answeringTimeMin"], value)

    def call_answer_time_max(self, value=None):
        """
        Return/set maximum call answer time.
        """
        return self._getset(["trafficSpecific", "callTerm", "answeringTimeMin"], value)

    def simultaneous_calls(self, max=False):
        """
        Return the number of simultaneous calls derived from the scenario
        cps and call holding time. Calculated value, cannot set.
        """
        cps = self.cps()
        cht = self.call_holding_time_max() if max else self.call_holding_time_min()
        return round(float(cps) * float(cht), 4) if cps and cht else None

    def _call_range(self, value=None):
        """
        Return call ID range.
        """
        return (            self._getset(["trafficSpecific","callOrig","calledUserDescriptor","basicUserParams", "idRange", 0], value)
            or
            self._getset(["callingUserDescriptor","basicUserParams", "idRange", 0], value)
        )

    def call_range_first(self, value=None):
        """
        Return first call ID in range.
        """
        first, last = self._call_range().split("..")
        call_range = "{}..{}".format(str(value).rjust(6, "0"), last) if value else None
        return self._call_range(call_range).split("..")[0]

    def call_range_last(self, value=None):
        """
        Return last call ID in range.
        """
        first, last = self._call_range().split("..")
        call_range = "{}..{}".format(first, str(value).rjust(6, "0")) if value else None
        return self._call_range(call_range).split("..")[1]

    def call_duration(self, max=False):
        """
        Return scenario call duration minimum or maximum if `max` is true.
        """
        answer_time = 0.0
        holding_time = 0.0
        for case in self._config.scenarios(self.group):
            if case.case in self.__origs:
                ht = case.call_holding_time_min()
                if ht:
                    holding_time +=  ht
            else:
                at = case.call_answer_time_min()
                if at:
                    answer_time += at
        return holding_time + answer_time

    def _ip_range_path(self):
        simulation = self._get(["transport", 0, "hostTransport", 0, "simulationType"])
        stype = list(simulation.keys())[0]
        prefix = "ue" if stype == "icsUE" or stype == "ueTransport" else "media"
        return prefix, stype

    def ip_range_first(self, value=None):
        """
        Return first IP address in range.
        """
        prefix, stype = self._ip_range_path()
        return self._getset(["transport", 0, "hostTransport", 0, "simulationType", stype, prefix + "IpLow"], value)

    def ip_range_last(self, value=None):
        """
        Return last IP address in range.
        """
        prefix, stype = self._ip_range_path()
        return self._getset(["transport", 0, "hostTransport", 0, "simulationType", stype, prefix + "IpHigh"], value)

    def user_count(self):
        """
        Return the number of scenario users.
        """
        call_range = self._call_range()
        if call_range:
            first, last = list(map(int, call_range.split("..")))
            return (last - first) + 1

    def codec(self):
        """
        Return list of supported codecs.
        """
        return self._get(["trafficSpecific","media","generator","mlsim","supportedCodecs"])

    def protocol(self):
        """
        Return scenario transport protocol name.
        """
        return self._get(["transport", 0, "hostTransport", 0, "proxyTransport", "preferredTransport"])

    def subscribe_info(self):
        """Return subscribe information for scenario.
        """
        return self._get(["trafficSpecific", "subscribe"])

    def modifications(self):
        """Return scenario message modifications.
        """
        try:
            return self._get(["trafficSpecific", "messageModify"])
        except ValueError:
            pass

    def templates(self):
        """
        Return scenario templates.
        """
        try:
            return self._get(["trafficSpecific", "templates"])
        except ValueError:
            pass

    def _getset(self, path, value=None):
        if value is not None:
            return self._set(path, value, self.__scenario)
        return self._get(path)

    def _get(self, object_path, tree=None, resolve=True):
        tree = tree if tree else self.__scenario

        if not object_path:
            return None

        next = object_path[0]

        try:
            if isinstance(object_path, str):
                subtree = tree.get(next)
            else:
                subtree = tree[next]
        except (ValueError, KeyError):
            return None

        if len(object_path) == 1:
            return subtree if not resolve else _resolve(subtree, self._config)

        return self._get(
            object_path[1:],
            _resolve(subtree, self._config),
            resolve=resolve
        )

    def _set (self, object_path, value, tree):

        if len(object_path) == 1:
            if _ref(tree.get(object_path[0])):
                return _resolve(tree[object_path[0]], self._config, set_value=value)
            else:
                if tree.get(object_path[0]) is not None:
                    tree[object_path[0]] = value
                return tree.get(object_path[0])

        return self._set(
            object_path[1:],
            value,
            _resolve(tree[object_path[0]], self._config))


def _ref(value):

    if not isinstance(value, str):
        return None

    bre = r"^\$\{([^,]+)"
    if value[0:1] == "$" and value[1:2] != "{":
        ref = value[1:].strip("\"")
    else:
        ref = re.findall(bre, value)
        if ref:
            ref = ref[0]
    return ref

def _resolve(value, config, set_value=None):
    ref = _ref(value)

    value, obj = find_ref_define(ref, config) if ref else (value, config._tree)

    if _ref(value):
        # keep resolving until a non-ref value is found
        return _resolve(value, config, set_value)

    if set_value is not None and obj["DEFINE"][ref] is not None:
        obj["DEFINE"][ref] = set_value

    return value.strip("\"") if isinstance(value, str) else value

def find_ref_define(ref, config):
    main = config._tree.get(ref)

    if main:
        return main, config._tree

    for inc, tree in config._included.items():
        val = tree.get("DEFINE", {}).get(ref)
        if val is not None:
            return val, tree

    return None, {}



# PARSER

def true():            return "true"
def false():           return "false"
def dq_string():       return '"', _(r'((\\")|([^"]))*'),'"'
def sq_string():       return "'", _(r"((\\')|([^']))*"),"'"
def string():          return [ dq_string, sq_string ], Optional(["O", "H"])
def key():             return _(r"[0-9a-zA-Z_\*\.]+")
def octet():           return _(r"(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])")
def number():          return _(r"-?\d*(\.\d+)*")
def ip():              return octet,".",octet,".",octet,".",octet # see test_parser.py!

def comment():         return ["//", "#"], _(".+")
def boolean():         return [ true, false ]
def expression():      return [or_expr, key]   # refine as needed
def or_expr():         return key, ZeroOrMore("|", key)
def reference():       return [ bracketed, variable ]
def bracketed():       return "$", "{", key, Optional(",", key), "}"
def variable():        return "$", key

def array():           return "{", Optional(value_list), "}"
def value():           return [ value_map, ip, number, string, reference, expression, array, boolean ]
def value_list():      return value, ZeroOrMore(",", value)
def pair():            return key, ":=", value
def pair_list():       return pair, ZeroOrMore(",", pair),
def value_map():       return "{", Optional(pair_list), "}"
def assignment():      return pair, Optional(";")

def generic_header():  return "[", key, "]"
def include_header():  return "[", "INCLUDE", "]"
def execute_header():  return "[", "EXECUTE", "]"

def generic_section(): return generic_header, ZeroOrMore(assignment)
def include_section(): return include_header, ZeroOrMore(string)
def execute_section(): return execute_header, ZeroOrMore(expression)
def section():         return [ include_section, execute_section, generic_section ]

# START SYMBOL
def config():          return ZeroOrMore(section), EOF

# SEMANTIC ANALYSIS

class TitanSimConfigVisitor(PTNodeVisitor):

     def visit_true(self, node,  children):
         return True

     def visit_false(self, node,  children):
         return False

     def visit_string(self, node,  children):
         if children:
              return "\"" + str(children[0]) + "\"" + "".join(children[1:])
         else:
              return "\"\""

     def visit_key(self, node,  children):
         return node.value

     def visit_octet(self, node,  children):
         return node.value

     def visit_number(self, node,  children):
         try:
             return int(node.value)
         except ValueError:
             return float(node.value)

     def visit_ip(self, node,  children):
         return ".".join(children)

     def visit_comment(self, node,  children):
         pass

     def visit_boolean(self, node,  children):
         return node.value

     def visit_expression(self, node,  children):
         return children[0]

     def visit_or_expr(self, node,  children):
         # we do nothing with these expressions at this point
         return " | ".join(children)

     def visit_reference(self, node,  children):
         ref = children[0]
         if len(ref) > 1:
             return "${" + ref[0] + ", " + ref[1] + "}"
         else:
             return "$" + ref[0]

     def visit_bracketed(self, node,  children):
         return children

     def visit_variable(self, node,  children):
         return children

     def visit_array(self, node,  children):
         return list(children[0])

     def visit_value(self, node,  children):
         return children[0]

     def visit_value_list(self, node,  children):
         return children

     def visit_pair(self, node,  children):
         return (children[0], children[1])

     def visit_pair_list(self, node,  children):
         return list(children)

     def visit_value_map(self, node,  children):
         if children:
             return dict(children[0])
         else:
             return dict()

     def visit_assignment(self, node,  children):
         return children[0]

     def visit_section_header(self, node, children):
         return children

     def visit_section_content(self, node, children):
         return children

     def visit_generic_header(self, node,  children):
         return children[0]

     def visit_include_header(self, node,  children):
         return "INCLUDE"

     def visit_execute_header(self, node,  children):
         return "EXECUTE"

     def visit_generic_section(self, node,  children):
         return children

     def visit_include_section(self, node,  children):
         return (children)

     def visit_execute_section(self, node,  children):
         return children

     def visit_section(self, node,  children):
         # A section can be empty, in which case, we return the name
         # as it is in a list.
         if len(children[0]) > 1:
             if isinstance(children[0][1], tuple):
                 return dict({ children[0][0]: dict(children[0][1:])})
             else:
                 return { children[0][0]: children[0][1:] }
         elif isinstance(children[0], list) and len(children[0]) == 1:
             return children[0][0]
         else:
             return children[0]

     def visit_config(self, node,  children):
         ast = dict()
         for key in children:
             if type(key) is dict:
                 ast.update(key)
         return ast

__all__ = ["Config", "Scenario"]
