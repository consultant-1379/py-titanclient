⛔ **The `playlist` module is deprecated!**

The `playlist` module provides a `titanclient` analogue to TitanSim
[Playlists](http://ttcn.ericsson.se/TitanSim/Help/StartUp_and_Use/Controlling_TitanSim/Playlist.html)
with a YAML input format that is hopefully easy to write.

A command-line wrapper is added to `~/.local/bin` during `pip3`-based
installation:

```
$ titanclient-run-playlist -h
usage: titanclient-run-playlist [-h] -p <FILEPATH> [-d] [-o OUTPUT_DIR]

optional arguments:
  -h, --help            show this help message and exit
  -p <FILEPATH>, --playlist <FILEPATH>
                        YAML playlist.
  -d, --dry-run         Display list of operations only.
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Directory to save stats to.
```

Both the script above and the main module class, `Playlist` take a
YAML file path as argument, and execute each operation in that
file. The format of the YAML file is as follows:


```
simulators:
  - name: ts11
    address: 10.10.10.10
    port: 8080 # port can be omitted and defaults to 8080
  ...
playlist:
  ... steps
```

The following steps are supported:

- `ready` wait until specified TitanSims are in ready state.

- `wait`: do nothing for the specified amount of time. Time is a string
in the format _10s_, _10m_, _10h_, or _1d_.

- `label`: named position to be referred to in `jumpif`.

- `jump`: unconditionally jump to label. Argument is a string label name.

- `jumpif`: conditionally jump to label. _to_ is the target label.
  __cond_ is a simple comparison expression in the form _mode
  value-name operator number_, e.g. "cps < 10". The supported
  operators are "<", ">", "<=", ">=" and "==". _mode_ is an optional

  prefix and can be _avg_ or _all_. _avg_ causes the given value to be
  averaged across all scenarios on the given TitanSim before
  comparison. If it's _all_, the comparison will return true only if
  all values across all scenarios/titansims return true for the
  comparison. Otherwise, individual scenario values are compared one
  by one and a single match will cause a jump.

- `start`: start scenarios on the given TitanSims. This operation
  waits until loadgen - RUNNING. Supports a _timeout_ parameter with
  an integer value of seconds (default 600).

- `stop`: stop scenarios on the given TitanSims. This operation waits
  until preamble - IDLE. Supports a _timeout_ parameter.

- `set`: set scenario values on the given TitanSims. Settable values
supported by `titanclient.client.Client` can be used as attributes to
this operation. Besides literal values, a limited expression format is
supported that can contain two keywords: `current` (the running
value)/`default`(the value stored at playlist startup). The format of
expressions is e.g. _current + 10%_. The "%" can be omitted.

- `stat`: emit (pretty-printed) stats. Value names (as featured in
`titanclient.client.Client`) are listed under the _name_ attribute. If
the `avg` attribute is provided with a comma-separated list of value
names, emit the average of those values.

- `reset`: reset stats on the given TitanSims

Except for `wait` and `jump`, each step can take a _titansim_ and a
_scenario_ attribute. _titansim_ is a comma-separated list of TitanSim
names (as defined in the YAML file). _scenario_ is used as the
`scenario_filter` parameter of the given request (use to filter for
specific scenarios for the given step). If the value of either is set
to _all_, all scenarios/TitanSims will be included for the step. _all_
(no filtering) is used by default, as these attributes can be omitted
in `set`/`stat`.

Note that registers are not supported currently.

Example playlist:

```
simulators:
  - name: ts13
    address: localhost
    port: 2000
playlist:
  - ready:
      titansim: all
  - wait: 10s
  - start:
      titansim: all
      timeout: 1800
  - set:
      cps: default + 5%
      rps: default + 5%
  - wait: 90s
  - stat:
      name: gos, cps
      avg: gos
  - reset:
      titansim: all
  - set:
      cps: default
      rps: default
  - stop:
      titansim: all
      scenario: all
      timeout: 1800
```

Increase CPS to 15 in increments of 2.5/10 seconds, then reset
to zero:

```
simulators:
  - name: ts13
    address: localhost
    port: 8080
playlist:
  - ready:
      titansim: all
  - label: loop
  - wait: 10s
  - set:
      cps: current + 2.5
  - jumpif:
      cond: cps < 15
      to: loop
  - set:
      cps: 0
```

Set call CPS & RPS to 10 on a single scenario:

```
simulators:
  - name: ts14
    address: localhost
    port: 8080
playlist:
  - ready:
      titansim: all
  - set:
      rps: 10
      call_cps: 10
      scenario: 0010PsPs_A
```
